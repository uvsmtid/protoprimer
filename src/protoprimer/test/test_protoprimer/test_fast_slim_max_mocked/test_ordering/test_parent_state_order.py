from __future__ import annotations

import pytest

from local_test.verified_dynamic_graph import (
    VerifyingEnvContext,
    max_deps_env_ctx,
)
from protoprimer.primer_kernel import (
    EntryFunc,
    EnvState,
    StateNode,
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
    env_ctx._entry_func = EntryFunc.func_boot_env
    env_ctx._is_app = True
    env_ctx._sub_command = max_deps_env_ctx._sub_command
    env_ctx._is_log_enabled = max_deps_env_ctx._is_log_enabled

    state_graph_instance = env_ctx.state_graph

    env_state_name_to_ordinal = {env_state.name: index for index, env_state in enumerate(EnvState)}

    order_violations = []

    # when:

    for env_state in EnvState:
        state_node = state_graph_instance.get_state_node(env_state.name)
        if state_node is None:
            raise AssertionError(f"`{StateNode.__name__}` for [{env_state.name}] not found")

        parent_states = state_node.get_parent_states()

        parent_ordinals = [env_state_name_to_ordinal[parent_state] for parent_state in parent_states]

        # then:

        if parent_ordinals != sorted(parent_ordinals):
            order_violations.append(f"In `{env_state.name}`, parents [{parent_states}] with ordinals [{parent_ordinals}] are not sorted.")

    _report_order_violations(order_violations)
