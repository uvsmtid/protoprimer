from __future__ import annotations

import itertools
import json
from typing import Any

from local_test.verified_dynamic_graph import (
    GraphAssertionError,
    VerifyingEnvContext,
    max_deps_graph_coordinates,
)
from protoprimer.primer_kernel import (
    EntryFunc,
    EnvContext,
    EnvState,
    GraphCoordinates,
    SubCommand,
)


def _count_reachable_states(env_ctx: EnvContext) -> int:
    reachable_state_set = set()
    for env_state in EnvState:
        state_node = env_ctx.state_graph.get_state_node(env_state.name)
        for parent_state in state_node.get_parent_states():
            reachable_state_set.add(parent_state)
    return len(reachable_state_set)


def _graph_coordinates_to_dict(coords: GraphCoordinates) -> dict[str, Any]:
    return {
        "entry_func": coords.entry_func.name if coords.entry_func else None,
        "sub_command": coords.sub_command.name if coords.sub_command else None,
        "prepare_venv": coords.prepare_venv,
        "is_log_enabled": coords.is_log_enabled,
    }


def _find_max_deps_graph_coordinates() -> tuple[GraphCoordinates, int]:
    """
    Find `GraphCoordinates` with maximum unique parent states among all valid combinations
    (those not rejected by `VerifyingStateGraph`).
    """
    best_coords: GraphCoordinates | None = None
    max_count: int = -1

    for entry_func, sub_command, prepare_venv, is_log_enabled in itertools.product(
        list(EntryFunc),
        list(SubCommand),
        [True, False],
        [True, False],
    ):
        env_ctx = VerifyingEnvContext()
        env_ctx.graph_coordinates.entry_func = entry_func
        env_ctx.graph_coordinates.sub_command = sub_command
        env_ctx.graph_coordinates.prepare_venv = prepare_venv
        env_ctx.graph_coordinates.is_log_enabled = is_log_enabled
        try:
            curr_count = _count_reachable_states(env_ctx)
        except GraphAssertionError:
            continue

        if curr_count > max_count:
            max_count = curr_count
            best_coords = GraphCoordinates()
            best_coords.entry_func = entry_func
            best_coords.sub_command = sub_command
            best_coords.prepare_venv = prepare_venv
            best_coords.is_log_enabled = is_log_enabled

    assert best_coords is not None
    return best_coords, max_count


def test_find_max_deps_graph_coordinates() -> None:
    """
    Find and print `GraphCoordinates` with maximum unique parent states.
    Run with `-s` to see the stdout.
    """
    best_coords, max_count = _find_max_deps_graph_coordinates()
    print(
        #
        f"\nmax_count: {max_count}\n"
        + json.dumps(
            _graph_coordinates_to_dict(best_coords),
            indent=4,
        )
    )


def test_verify_max_deps_graph_coordinates_is_max() -> None:
    """
    Verify `max_deps_graph_coordinates` yields more unique parent states than any other valid `GraphCoordinates`.
    """

    # given: count for defined max_deps_graph_coordinates
    env_ctx = VerifyingEnvContext()
    env_ctx.graph_coordinates.entry_func = max_deps_graph_coordinates.entry_func
    env_ctx.graph_coordinates.sub_command = max_deps_graph_coordinates.sub_command
    env_ctx.graph_coordinates.prepare_venv = max_deps_graph_coordinates.prepare_venv
    env_ctx.graph_coordinates.is_log_enabled = max_deps_graph_coordinates.is_log_enabled
    defined_max_count = _count_reachable_states(env_ctx)

    # when: find actual maximum across all valid combinations
    found_best_coords, found_max_count = _find_max_deps_graph_coordinates()

    # then:
    if found_max_count > defined_max_count:
        raise AssertionError(
            #
            f"`max_deps_graph_coordinates` has [{defined_max_count}] unique states, "
            f"but there is another one which has [{found_max_count}] unique states:\n"
            f"{json.dumps(_graph_coordinates_to_dict(found_best_coords), indent=4)}"
        )
