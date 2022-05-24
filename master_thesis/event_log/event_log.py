from typing import List, Dict, Tuple
import pandas as pd
import attr

from master_thesis.abstract import CoexRelation, SequenceRelation, PairEvent, ELRelation
from .algorithm import create_group_matrix

__all__ = (
    "EventLog",
)


@attr.s(auto_attribs=True)
class EventLog:
    traces: List[Tuple[str, ...]]
    vocabulary: Tuple[str]
    groups: Dict[Tuple[str, ...], List[Tuple[str, ...]]] = None
    filtered_group_keys: List[Tuple[str, ...]] = None
    seq_matrices_by_key: Dict[Tuple[str, ...], Dict[PairEvent, ELRelation]] = None
    errors_coex: Dict[Tuple[PairEvent, CoexRelation], int] = None
    errors_seq: Dict[Tuple[PairEvent, SequenceRelation], int] = None
    valid_traces: List[Tuple[str, ...]] = None
    invalid_traces: List[Tuple[str, ...]] = None

    def statistic(self) -> str:
        amount_of_traces = len(self.traces)
        vocabulary = len(self.vocabulary)
        amount_of_valid_traces = len(self.valid_traces) / len(self.traces) * 100

        return (f"""
        amount_of_traces = {amount_of_traces}
        vocabulary = {vocabulary}
        amount_of_valid_traces_percentage = {amount_of_valid_traces}
        {self.errors_coex}
        {self.errors_seq}
        """)

    def parse_groups(self) -> None:
        groups = dict()
        for trace in self.traces:
            sorted_trace = tuple(sorted(trace))
            if sorted_trace in groups:
                groups[sorted_trace].append(trace)
            else:
                groups[sorted_trace] = [trace]

        self.groups = groups

    def filter(
        self,
        declare_coex: Dict[PairEvent, CoexRelation],
    ) -> None:
        self.filtered_group_keys = []
        self.errors_coex = {}
        for group_key in self.groups.keys():
            flag = True
            for pair, coex in declare_coex.items():
                if pair[0] in group_key:
                    if coex is CoexRelation.CONFLICT:
                        if pair[1] in group_key:
                            if (pair, coex) in self.errors_coex:
                                self.errors_coex[(pair, coex)] += len(self.groups[group_key])
                            else:
                                self.errors_coex[(pair, coex)] = len(self.groups[group_key])
                            flag = False
                    if coex is CoexRelation.DEPENDENCE:
                        if pair[1] not in group_key:
                            if (pair, coex) in self.errors_coex:
                                self.errors_coex[(pair, coex)] += len(self.groups[group_key])
                            else:
                                self.errors_coex[(pair, coex)] = len(self.groups[group_key])
                            flag = False
            if flag:
                self.filtered_group_keys.append(group_key)

    def validate_sequence(
        self,
        declare_seq: Dict[PairEvent, SequenceRelation],
    ) -> None:
        self.valid_traces = []
        self.invalid_traces = []
        self.errors_seq = {}
        for group_key, matrix in self.seq_matrices_by_key.items():
            valid = True
            parallel_invalid = set()
            for pair, rel in declare_seq.items():
                if pair in matrix:
                    if rel is matrix[pair].relation_main or rel is SequenceRelation.PARALLEL:
                        continue
                    if matrix[pair].relation_main is SequenceRelation.PARALLEL:
                        if rel is SequenceRelation.CAUSALITY:
                            parallel_invalid.update(matrix[pair].relation_causality_rev)
                            if (pair, rel) not in self.errors_seq:
                                self.errors_seq[(pair, rel)] = len(matrix[pair].relation_causality_rev)
                            else:
                                self.errors_seq[(pair, rel)] += len(matrix[pair].relation_causality_rev)
                        else:
                            parallel_invalid.update(matrix[pair].relation_causality)
                            if (pair, rel) not in self.errors_seq:
                                self.errors_seq[(pair, rel)] = len(matrix[pair].relation_causality)
                            else:
                                self.errors_seq[(pair, rel)] += len(matrix[pair].relation_causality)
                    else:
                        valid = False
                        if (pair, rel) not in self.errors_seq:
                            self.errors_seq[(pair, rel)] = len(self.groups[group_key])
                        else:
                            self.errors_seq[(pair, rel)] += len(self.groups[group_key])
            if valid:
                traces = self.groups[group_key]
                for index, trace in enumerate(traces):
                    if index not in parallel_invalid:
                        self.valid_traces.append(trace)
                    else:
                        self.invalid_traces.append(trace)
            else:
                self.invalid_traces.extend(self.groups[group_key])

    def create_matrices(self) -> None:
        self.seq_matrices_by_key = {}
        for group_key in self.filtered_group_keys:
            group_traces = self.groups[group_key]
            self.seq_matrices_by_key[group_key] = create_group_matrix(
                group_traces,
            )

    def print_seq_matrices(self) -> None:
        for group_key, matrix in self.seq_matrices_by_key.items():
            values = []
            for event1 in group_key:  # matrix size
                line = []
                for event2 in group_key:  # matrix size
                    if event1 == event2:
                        line.append("\\")
                    elif (event1, event2) in matrix:
                        rel = matrix[(event1, event2)]
                        if rel.relation_main is SequenceRelation.PARALLEL:
                            line.append("||")
                        elif rel.relation_main is SequenceRelation.CAUSALITY:
                            line.append("<")
                        else:
                            line.append(">")
                    else:
                        line.append("\\")
                values.append(line)
            print(f"Group: {group_key}")
            print(pd.DataFrame(values, columns=group_key, index=group_key).to_markdown())
            print("\n")

    @classmethod
    def from_traces(cls, traces: List[Tuple[str, ...]]) -> "EventLog":
        vocabulary = set()
        for trace in traces:
            vocabulary.update(trace)
        return EventLog(traces, tuple(sorted(vocabulary)))

    def amount(self) -> int:
        return len(self.traces)
