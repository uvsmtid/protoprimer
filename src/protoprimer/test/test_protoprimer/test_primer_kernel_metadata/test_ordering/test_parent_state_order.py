from __future__ import annotations

import pytest

from local_test.verified_dynamic_graph import (
    VerifyingEnvContext,
    max_deps_env_ctx,
)
from protoprimer.primer_kernel import (
    _EntryFunc,
    _EnvState,
    _StateNode,
)


def _report_order_violations(order_violations: list[str]) -> None:
    if order_violations:
        pytest.fail("Parent states order violations:\n" + "\n".join(order_violations))


# noinspection PyPep8Naming
def test_EnvState_parent_order() -> None:
    """
    Verify parent states follow enum definition order.
    """

    # given:

    env_ctx = VerifyingEnvContext()
    env_ctx._entry_func = _EntryFunc.func_boot_env
    env_ctx._is_app = True
    env_ctx._exec_operation = max_deps_env_ctx._exec_operation
    env_ctx._is_log_enabled = max_deps_env_ctx._is_log_enabled

    state_graph_instance = env_ctx._state_graph

    env_state_name_to_ordinal = {env_state.name: index for index, env_state in enumerate(_EnvState)}

    order_violations = []

    # when:

    for env_state in _EnvState:
        state_node = state_graph_instance.get_state_node(env_state.name)
        if state_node is None:
            raise AssertionError(f"`{_StateNode.__name__}` for [{env_state.name}] not found")

        parent_states = state_node.get_parent_states()

        parent_ordinals = [env_state_name_to_ordinal[parent_state] for parent_state in parent_states]

        # then:

        if parent_ordinals != sorted(parent_ordinals):
            order_violations.append(f"In `{env_state.name}`, parents [{parent_states}] with ordinals [{parent_ordinals}] are not sorted.")

    _report_order_violations(order_violations)


# noinspection PyPep8Naming
def test_EnvState_exec_operation_precedes_symlink_in_parents() -> None:
    """
    The `Node` for `state_local_conf_dir_abs_path_inited` is selected by a factory
    which reads `env_ctx._exec_operation` (set by `state_input_exec_operation_loaded`).

    The order is ensured by the DAG: every state depending on the symlink state
    must also depend on the exec operation state and have it earlier in its parents.
    """

    # given:

    env_ctx = VerifyingEnvContext()
    env_ctx._entry_func = _EntryFunc.func_boot_env
    env_ctx._is_app = True
    env_ctx._exec_operation = max_deps_env_ctx._exec_operation
    env_ctx._is_log_enabled = max_deps_env_ctx._is_log_enabled

    state_graph_instance = env_ctx._state_graph

    order_violations = []

    # when:

    for env_state in _EnvState:
        parent_states = list(state_graph_instance.get_state_node(env_state.name).get_parent_states())
        if _EnvState.state_local_conf_dir_abs_path_inited.name not in parent_states:
            continue

        # then:

        if _EnvState.state_input_exec_operation_loaded.name not in parent_states:
            order_violations.append(f"`{env_state.name}` depends on `{_EnvState.state_local_conf_dir_abs_path_inited.name}` but not on `{_EnvState.state_input_exec_operation_loaded.name}`.")
        elif parent_states.index(_EnvState.state_input_exec_operation_loaded.name) > parent_states.index(_EnvState.state_local_conf_dir_abs_path_inited.name):
            order_violations.append(f"`{env_state.name}` lists `{_EnvState.state_input_exec_operation_loaded.name}` after `{_EnvState.state_local_conf_dir_abs_path_inited.name}`.")

    _report_order_violations(order_violations)
