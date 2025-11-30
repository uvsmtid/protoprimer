from __future__ import annotations

import pytest

from protoprimer.primer_kernel import (
    EnvContext,
    EnvState,
    StateNode,
)


def _report_violations(
    violations: list[str],
) -> None:
    if violations:
        pytest.fail("Parent definition order violations:\n" + "\n".join(violations))


class TestParentStateOrdering:
    """
    This test ensures that parent states are ordered in the same way as in the enum definition.
    This is purely cosmetic enforcement.
    It also helps to keep line history consistent with ordering.
    """

    def test_EnvState_parent_order(self) -> None:
        # given:
        env_context_instance = EnvContext()
        state_graph_instance = env_context_instance.state_graph

        env_state_name_to_ordinal = {
            env_state.name: index for index, env_state in enumerate(EnvState)
        }

        violations = []

        # when:
        for env_state in EnvState:
            state_node = state_graph_instance.get_state_node(env_state.name)
            assert (
                state_node is not None
            ), f"`{StateNode.__name__}` for [{env_state.name}] not found"

            parent_states = state_node.get_parent_states()
            if len(parent_states) <= 1:
                continue

            parent_ordinals = [env_state_name_to_ordinal[p] for p in parent_states]

            # then:
            if parent_ordinals != sorted(parent_ordinals):
                violations.append(
                    f"In `{env_state.name}`, parents [{parent_states}] with ordinals [{parent_ordinals}] are not sorted."
                )

        _report_violations(violations)
