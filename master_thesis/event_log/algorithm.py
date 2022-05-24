from typing import List, Dict, Tuple

from master_thesis.abstract import PairEvent, SequenceRelation, ELRelation

__all__ = (
    "create_matrix",
    "sum_matrices",
    "create_group_matrix",
)


def create_matrix(trace: Tuple[str, ...]) -> Dict[PairEvent, ELRelation]:
    result = {}
    reversed_trace = trace[::-1]
    for index, event in enumerate(reversed_trace):
        if index + 1 == len(trace):
            break
        for event2 in reversed_trace[index+1:]:
            result[(event, event2)] = ELRelation(SequenceRelation.CAUSALITY_REV)
            result[(event2, event)] = ELRelation(SequenceRelation.CAUSALITY)
    return result


def sum_matrices(
    matrix_a: Dict[PairEvent, ELRelation],
    matrix_b: Dict[PairEvent, ELRelation],
    index: int,
) -> Dict[PairEvent, ELRelation]:
    for pair, rel in matrix_b.items():
        if matrix_a[pair].relation_main is SequenceRelation.PARALLEL:
            if rel.relation_main is SequenceRelation.CAUSALITY:
                matrix_a[pair].relation_causality.append(index)
            else:
                matrix_a[pair].relation_causality_rev.append(index)
        else:
            if matrix_a[pair].relation_main is not rel.relation_main:
                if rel.relation_main is SequenceRelation.CAUSALITY:
                    matrix_a[pair] = ELRelation(
                        SequenceRelation.PARALLEL,
                        [index],
                        [i for i in range(index)],
                    )
                else:
                    matrix_a[pair] = ELRelation(
                        SequenceRelation.PARALLEL,
                        [i for i in range(index)],
                        [index],
                    )
    return matrix_a


def create_group_matrix(
    traces: List[Tuple[str, ...]],
) -> Dict[PairEvent, ELRelation]:
    matrices = []
    for trace in traces:
        interm_matrix = create_matrix(trace)
        matrices.append(interm_matrix)
    final_matrix: Dict[PairEvent, ELRelation] = matrices[0]
    if len(matrices) == 1:
        return final_matrix
    for index, matrix in enumerate(matrices[1:], start=1):
        final_matrix = sum_matrices(final_matrix, matrix, index)

    return final_matrix
