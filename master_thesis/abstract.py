from enum import Enum, unique, auto

import attr

from typing import Tuple, List

__all__ = (
    "PairEvent",
    "CoexRelation",
    "SequenceRelation",
    "DeclareTemplate",
    "ELRelation",
    "MAP_DECLARE_TMPLT_TO_COEX",
    "MAP_DECLARE_TMPLT_TO_SEQ",
)

PairEvent = Tuple[str, str]


@unique
class CoexRelation(Enum):
    CONFLICT = auto()
    DEPENDENCE = auto()
    UNION = auto()


@unique
class SequenceRelation(Enum):
    CAUSALITY = auto()
    CAUSALITY_REV = auto()
    PARALLEL = auto()
    UNDEFINED = auto()


@unique
class DeclareTemplate(Enum):
    EXCLUSIVE_CHOICE = auto()
    RESPONDED_EXISTENCE = auto()
    CO_EXISTENCE = auto()
    RESPONSE = auto()
    PRECEDENCE = auto()
    SUCCESSION = auto()


@attr.s(auto_attribs=True)
class ELRelation:
    relation_main: SequenceRelation
    relation_causality: List = None
    relation_causality_rev: List = None


MAP_DECLARE_TMPLT_TO_COEX = {
    DeclareTemplate.EXCLUSIVE_CHOICE: (CoexRelation.CONFLICT, CoexRelation.CONFLICT),
    DeclareTemplate.RESPONDED_EXISTENCE: (CoexRelation.DEPENDENCE, None),
    DeclareTemplate.CO_EXISTENCE: (CoexRelation.DEPENDENCE, CoexRelation.DEPENDENCE),
    DeclareTemplate.RESPONSE: (CoexRelation.DEPENDENCE, None),
    DeclareTemplate.PRECEDENCE: (None, CoexRelation.DEPENDENCE),
    DeclareTemplate.SUCCESSION: (CoexRelation.DEPENDENCE, CoexRelation.DEPENDENCE),
}


MAP_DECLARE_TMPLT_TO_SEQ = {
    DeclareTemplate.EXCLUSIVE_CHOICE: (SequenceRelation.UNDEFINED, SequenceRelation.UNDEFINED),
    DeclareTemplate.RESPONDED_EXISTENCE: (SequenceRelation.PARALLEL, SequenceRelation.PARALLEL),
    DeclareTemplate.CO_EXISTENCE: (SequenceRelation.PARALLEL, SequenceRelation.PARALLEL),
    DeclareTemplate.RESPONSE: (SequenceRelation.CAUSALITY, SequenceRelation.CAUSALITY_REV),
    DeclareTemplate.PRECEDENCE: (SequenceRelation.CAUSALITY, SequenceRelation.CAUSALITY_REV),
    DeclareTemplate.SUCCESSION: (SequenceRelation.CAUSALITY, SequenceRelation.CAUSALITY_REV),
}
