from __future__ import annotations

import pytest

from protoprimer.primer_kernel import (
    EnvContext,
    EnvState,
    StateNode,
    WizardState,
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

    def test_WizardState_parent_order(self) -> None:
        # given:
        env_context_instance = EnvContext()

        env_state_name_to_ordinal = {s.name: i for i, s in enumerate(EnvState)}
        wizard_state_name_to_ordinal = {s.name: i for i, s in enumerate(WizardState)}

        env_state_names = set(env_state_name_to_ordinal.keys())
        wizard_state_names = set(wizard_state_name_to_ordinal.keys())

        violations = []

        # when:
        for wizard_state in WizardState:
            state_node_class = wizard_state.value
            state_node = state_node_class(env_context_instance)

            parent_states = [
                p for p in state_node.get_parent_states() if not p.startswith("_")
            ]
            if not parent_states:
                continue

            # then:
            env_parents = [p for p in parent_states if p in env_state_names]
            wizard_parents = [p for p in parent_states if p in wizard_state_names]

            all_known_parents = set(env_parents + wizard_parents)
            for p in parent_states:
                if p not in all_known_parents:
                    violations.append(
                        f"Parent '{p}' of '{wizard_state.name}' is not in EnvState or WizardState."
                    )

            if len(env_parents) > 1:
                env_ordinals = [env_state_name_to_ordinal[p] for p in env_parents]
                if env_ordinals != sorted(env_ordinals):
                    violations.append(
                        f"In {wizard_state.name}, EnvState parents {env_parents} with ordinals {env_ordinals} are not sorted."
                    )

            if len(wizard_parents) > 1:
                wizard_ordinals = [
                    wizard_state_name_to_ordinal[p] for p in wizard_parents
                ]
                if wizard_ordinals != sorted(wizard_ordinals):
                    violations.append(
                        f"In {wizard_state.name}, WizardState parents {wizard_parents} with ordinals {wizard_ordinals} are not sorted."
                    )

        _report_violations(violations)
