from __future__ import annotations
from protoprimer.primer_kernel import (
    EnvContext,
    RunStrategy,
    StateGraph,
    StateNode,
    TargetState,
)


class GraphPrinter(RunStrategy):
    """
    This class prints reduced DAG of `EnvState`-s.

    Full DAG for a target may involve the same dependency/parent multiple times.
    Printing each dependency multiple times (with all its transient dependencies) looks excessive.
    Instead, this class prints each dependency/parent only if any of its siblings have not been printed yet.
    Therefore, there is some duplication, but the result is both more concise and less confusing.
    """

    rendered_no_parents: str = "[none]"

    def __init__(
        self,
        state_graph: StateGraph,
    ):
        super().__init__()
        self.state_graph: StateGraph = state_graph
        self.already_printed: set[str] = set()

    def execute_strategy(
        self,
        state_node: StateNode,
    ) -> None:
        self.print_node_parents(
            state_node,
            force_print=False,
            level=0,
        )

    def print_node_parents(
        self,
        state_node,
        force_print: bool,
        level: int,
    ) -> None:
        if state_node.get_state_name() in self.already_printed and not force_print:
            return
        else:
            self.already_printed.add(state_node.get_state_name())

        # Indented name:
        print(
            f"{' ' * level * 4}{state_node.get_state_name()}",
            end="",
        )
        # Dependencies (parents):
        rendered_parent_states: str
        if len(state_node.get_parent_states()) > 0:
            rendered_parent_states = " ".join(state_node.get_parent_states())
        else:
            rendered_parent_states = self.rendered_no_parents
        print(
            f": {rendered_parent_states}",
            end="",
        )
        # new line:
        print()

        # Check ahead if any of the dependencies (parents) are not printed:
        any_parent_to_print: bool = False
        for state_parent in state_node.get_parent_states():
            if state_parent not in self.already_printed:
                any_parent_to_print = True
                break

        # Recurse:
        if any_parent_to_print:
            for state_parent in state_node.get_parent_states():
                self.print_node_parents(
                    self.state_graph.state_nodes[state_parent],
                    # Even if this state was already printed, since we are printing siblings, print them all:
                    force_print=any_parent_to_print,
                    level=level + 1,
                )
