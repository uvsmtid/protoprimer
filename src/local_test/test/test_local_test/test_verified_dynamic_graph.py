from __future__ import annotations

import copy
import itertools
import json
from typing import Any

from local_test.verified_dynamic_graph import (
    GraphAssertionError,
    VerifyingEnvContext,
    max_deps_env_ctx,
)
from protoprimer.primer_kernel import (
    EntryFunc,
    EnvContext,
    EnvState,
    SubCommand,
)


def _count_reachable_states(env_ctx: EnvContext) -> int:
    reachable_state_set = set()
    for env_state in EnvState:
        state_node = env_ctx.state_graph.get_state_node(env_state.name)
        for parent_state in state_node.get_parent_states():
            reachable_state_set.add(parent_state)
    return len(reachable_state_set)


def _env_ctx_to_dict(env_ctx: VerifyingEnvContext) -> dict[str, Any]:
    return {
        "entry_func": env_ctx._entry_func.name if env_ctx._entry_func else None,
        "sub_command": env_ctx._sub_command.name if env_ctx._sub_command else None,
        "prepare_venv": env_ctx._prepare_venv,
        "is_log_enabled": env_ctx._is_log_enabled,
    }


def _find_max_deps_env_ctx() -> tuple[VerifyingEnvContext, int]:
    """
    Find `EnvContext` with maximum unique parent states among all valid coordinate combinations
    (those not rejected by `VerifyingStateGraph`).
    """
    best_env_ctx: VerifyingEnvContext | None = None
    max_count: int = -1

    for entry_func, sub_command, prepare_venv, is_log_enabled in itertools.product(
        list(EntryFunc),
        list(SubCommand),
        [True, False],
        [True, False],
    ):
        env_ctx = VerifyingEnvContext()
        env_ctx._entry_func = entry_func
        env_ctx._is_app = entry_func in (EntryFunc.func_boot_env, EntryFunc.func_run_main)
        env_ctx._sub_command = sub_command
        env_ctx._prepare_venv = prepare_venv
        env_ctx._is_log_enabled = is_log_enabled
        try:
            curr_count = _count_reachable_states(env_ctx)
        except GraphAssertionError:
            continue

        if curr_count > max_count:
            max_count = curr_count
            best_env_ctx = env_ctx

    assert best_env_ctx is not None
    return best_env_ctx, max_count


def test_find_max_deps_env_ctx() -> None:
    """
    Find and print `EnvContext` with maximum unique parent states.
    Run with `-s` to see the stdout.
    """
    best_env_ctx, max_count = _find_max_deps_env_ctx()
    print(
        #
        f"\nmax_count: {max_count}\n"
        + json.dumps(
            _env_ctx_to_dict(best_env_ctx),
            indent=4,
        )
    )


def test_verify_max_deps_env_ctx_is_max() -> None:
    """
    Verify `max_deps_env_ctx` yields more unique parent states than any other valid `EnvContext`.
    """

    # given: count for defined max_deps_env_ctx
    env_ctx = copy.deepcopy(max_deps_env_ctx)
    defined_max_count = _count_reachable_states(env_ctx)

    # when: find actual maximum across all valid combinations
    found_best_env_ctx, found_max_count = _find_max_deps_env_ctx()

    # then:
    if found_max_count > defined_max_count:
        raise AssertionError(
            #
            f"`max_deps_env_ctx` has [{defined_max_count}] unique states, "
            f"but there is another one which has [{found_max_count}] unique states:\n"
            f"{json.dumps(_env_ctx_to_dict(found_best_env_ctx), indent=4)}"
        )
