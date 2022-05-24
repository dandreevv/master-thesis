from pathlib import Path

import pm4py

from master_thesis.abstract import DeclareTemplate
from master_thesis.declare import DeclareConstraint, DeclarativeModel
from master_thesis.event_log import EventLog

DIR = Path(__file__).parent

DECLARE_MODEL = [
    DeclareConstraint(
        DeclareTemplate.RESPONSE,
        var_1="t2",
        var_2="a!_1",
    ),
    DeclareConstraint(
        DeclareTemplate.PRECEDENCE,
        var_1="a!_1",
        var_2="a?_2",
    ),
    DeclareConstraint(
        DeclareTemplate.RESPONDED_EXISTENCE,
        var_1="a?_2",
        var_2="e13",
    ),
]


def create_traces_from_file(filename):
    traces = []
    path = DIR / filename
    event_log = pm4py.read_xes(path.__str__())
    for trace in event_log:
        parsed_trace = tuple(event["concept:name"] for event in trace)
        traces.append(parsed_trace)
    return traces


def define_event_log(filename) -> EventLog:
    traces = create_traces_from_file(filename)
    return EventLog.from_traces(traces)


def main():
    declare_model = DeclarativeModel(DECLARE_MODEL)
    declare_model.construct_matrices()
    declare_model.resolve_transaction_relations()

    traces = create_traces_from_file("IP-1_initial_log.xes")
    event_log = EventLog.from_traces(traces)
    event_log.parse_groups()
    event_log.filter(declare_model.coex)

    event_log.create_matrices()
    event_log.validate_sequence(declare_model.sequence)


if __name__ == "__main__":
    main()
