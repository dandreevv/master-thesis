from typing import Dict

from master_thesis.abstract import SequenceRelation, PairEvent

__all__ = ("find_transition",)


def find_transition(
    first_event,
    second_event,
    stop_event,
    sequences: Dict[PairEvent, SequenceRelation],
    relation=None,
) -> SequenceRelation:
    if (first_event, second_event) in sequences:
        if sequences[(first_event, second_event)] is relation:
            return relation
        else:
            return SequenceRelation.PARALLEL
    else:
        for pair, rel in sequences.items():
            if pair[0] == first_event and stop_event != pair[1]:
                result = find_transition(
                    pair[1],
                    second_event,
                    first_event,
                    sequences,
                    rel,
                )
                if result:
                    return result
        return SequenceRelation.PARALLEL
