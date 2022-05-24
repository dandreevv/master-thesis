from typing import Dict, List, Tuple
import pandas as pd
import attr
from master_thesis.abstract import (
    PairEvent,
    SequenceRelation,
    CoexRelation,
    DeclareTemplate,
    MAP_DECLARE_TMPLT_TO_COEX,
    MAP_DECLARE_TMPLT_TO_SEQ,
)
from .algorithm import find_transition

__all__ = (
    "DeclareConstraint",
    "DeclarativeModel",
)


@attr.s(auto_attribs=True, frozen=True)
class DeclareConstraint:
    template: DeclareTemplate
    var_1: str
    var_2: str


@attr.s(auto_attribs=True)
class DeclarativeModel:
    model: List[DeclareConstraint]
    vocabulary: Tuple[str] = None
    coex: Dict[PairEvent, CoexRelation] = None
    sequence: Dict[PairEvent, SequenceRelation] = None

    def construct_matrices(self) -> None:
        coex = dict()
        sequence = dict()
        vocabulary = set()
        for constraint in self.model:
            vocabulary.update((constraint.var_1, constraint.var_2))
            coex_rel = MAP_DECLARE_TMPLT_TO_COEX[constraint.template]
            if coex_rel[0]:
                coex[(constraint.var_1, constraint.var_2)] = coex_rel[0]
            if coex_rel[1]:
                coex[(constraint.var_2, constraint.var_1)] = coex_rel[1]
            seq_rel = MAP_DECLARE_TMPLT_TO_SEQ[constraint.template]
            sequence[(constraint.var_1, constraint.var_2)] = seq_rel[0]
            sequence[(constraint.var_2, constraint.var_1)] = seq_rel[1]

        self.vocabulary = tuple(sorted(vocabulary))
        self.coex = coex
        self.sequence = sequence

    def resolve_transaction_relations(self) -> None:
        for event1 in self.vocabulary:
            for event2 in self.vocabulary:
                if (event1, event2) not in self.sequence and event1 != event2:
                    relation = find_transition(event1, event2, event1, self.sequence)
                    self.sequence[(event1, event2)] = relation
                    if relation is SequenceRelation.CAUSALITY:
                        relation = SequenceRelation.CAUSALITY_REV
                    elif relation is SequenceRelation.CAUSALITY_REV:
                        relation = SequenceRelation.CAUSALITY
                    self.sequence[(event2, event1)] = relation

    def repr_coex(self) -> str:
        result = ""
        for pair, relation in self.coex.items():
            result += f"| {pair[0]:5}| {pair[1]:5}| {relation} \n"
        return result

    def repr_sequence(self) -> str:
        result = ""
        for pair, relation in self.sequence.items():
            result += f"| {pair[0]:5}| {pair[1]:5}| {relation} \n"
        return result

    def print_sequence_matrix(self) -> pd.DataFrame:
        values = []
        for event1 in self.vocabulary:
            line = []
            for event2 in self.vocabulary:
                if event1 == event2:
                    line.append("\\")
                elif (event1, event2) in self.sequence:
                    rel = self.sequence[(event1, event2)]
                    if rel is SequenceRelation.PARALLEL:
                        line.append("||")
                    elif rel is SequenceRelation.CAUSALITY:
                        line.append("<")
                    elif rel is SequenceRelation.CAUSALITY_REV:
                        line.append(">")
                    else:
                        line.append("#")
                else:
                    line.append("\\")
            values.append(line)
        return pd.DataFrame(values, columns=self.vocabulary, index=self.vocabulary)
