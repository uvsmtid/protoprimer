from __future__ import annotations

import enum

from protoprimer.primer_kernel import (
    StateGraph,
    StateNode,
)


def topological_sort(
    state_graph: StateGraph,
) -> list[str]:
    """
    Performs a topological sort on the given `StateGraph`.

    Args:
        state_graph: The StateGraph object to sort.

    Returns:
        A list of state names in topological order.
    """
    sorted_nodes: list[str] = []

    class VisitState(enum.Enum):
        unvisited_node = 0
        being_visited = 1
        already_visited = 2

    node_statuses: dict[str, VisitState] = {
        node_name: VisitState.unvisited_node for node_name in state_graph.state_nodes
    }

    def depth_first_search(node_name: str):
        node_statuses[node_name] = VisitState.being_visited

        curr_node: StateNode = state_graph.get_state_node(node_name)
        if curr_node is None:
            raise ValueError(f"`{StateNode.__name__}` [{node_name}] not found in graph")

        for parent_name in curr_node.get_parent_states():
            if parent_name not in state_graph.state_nodes:
                raise ValueError(
                    f"`{StateNode.__name__}` [{parent_name}] not found in graph"
                )
            if node_statuses[parent_name] == VisitState.being_visited:
                raise ValueError("cycle detected in graph")
            if node_statuses[parent_name] == VisitState.unvisited_node:
                depth_first_search(parent_name)

        node_statuses[node_name] = VisitState.already_visited
        sorted_nodes.append(node_name)

    for node_name in state_graph.state_nodes:
        if node_statuses[node_name] == VisitState.unvisited_node:
            depth_first_search(node_name)

    return sorted_nodes


def get_transitive_dependencies(
    state_graph: StateGraph,
    state_name: str,
) -> list[str]:
    """
    Lists all transitive dependencies for a given state name.

    Args:
        state_graph: The `StateGraph` object.
        state_name: The name of the state to get dependencies for.

    Returns:
        A list of state names representing the transitive dependencies.
    """
    trans_dependencies: list[str] = []
    visited_nodes: set[str] = set()

    def depth_first_search(node_name: str):
        visited_nodes.add(node_name)
        curr_node: StateNode = state_graph.get_state_node(node_name)
        if curr_node is None:
            raise ValueError(f"`{StateNode.__name__}` [{node_name}] not found in graph")

        for parent_name in curr_node.get_parent_states():
            if parent_name not in state_graph.state_nodes:
                raise ValueError(
                    f"`{StateNode.__name__}` [{parent_name}] not found in graph"
                )
            if parent_name not in visited_nodes:
                depth_first_search(parent_name)
        if node_name != state_name:
            trans_dependencies.append(node_name)

    depth_first_search(state_name)
    return trans_dependencies
