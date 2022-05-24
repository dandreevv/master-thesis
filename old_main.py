from master_thesis.abstract import DeclareTemplate
from master_thesis.declarative.declarative_model import (
    DeclareConstraint,
    DeclarativeMatrices,
)
from master_thesis.event_log.base import EventLog

declare_model = [
    DeclareConstraint(
        DeclareTemplate.PRECEDENCE,
        var_1="A",
        var_2="B",
    ),
    DeclareConstraint(
        DeclareTemplate.RESPONDED_EXISTENCE,
        var_1="B",
        var_2="C",
    ),
    DeclareConstraint(
        DeclareTemplate.RESPONSE,
        var_1="C",
        var_2="D",
    ),
    DeclareConstraint(
        DeclareTemplate.RESPONSE,
        var_1="E",
        var_2="C",
    ),
    DeclareConstraint(
        DeclareTemplate.SUCCESSION,
        var_1="C",
        var_2="F",
    ),
]

declare_model = [
    DeclareConstraint(
        DeclareTemplate.PRECEDENCE,
        var_1="A",
        var_2="B",
    ),
    DeclareConstraint(
        DeclareTemplate.PRECEDENCE,
        var_1="A",
        var_2="C",
    ),
    DeclareConstraint(
        DeclareTemplate.RESPONSE,
        var_1="B",
        var_2="D",
    ),
]


declare_matrices = DeclarativeMatrices.from_model(declare_model)
declare_matrices.resolve_transaction_relations()
print(declare_matrices.repr_coex())
print(declare_matrices.print_sequence_matrix())


traces = [
    ("B", "D"),
    ("A", "C"),
    ("A", "B", "D"),
    ("A", "D", "B"),
    ("A", "B", "C", "D"),
    ("A", "C", "B", "D"),
]

ev = EventLog.from_traces(traces)
ev.parse_groups()
ev.filter(declare_matrices.coex)
ev.create_matrices()
print("-----------")
ev.print_seq_matrices()
# print(ev)

print(ev.errors_coex)
