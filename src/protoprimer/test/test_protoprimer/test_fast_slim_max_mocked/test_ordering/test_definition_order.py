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
from local_repo.misc_tools.code_utils import (
    get_class_line_number,
)


def _report_order_violations(
    order_violations: list[str],
) -> None:
    """
    Fail the test and report all accumulated order violations.
    """
    if order_violations:
        pytest.fail("definition order order violations:\n" + "\n".join(order_violations))


class TestEnvStateOrdering:
    """
    Verify that `EnvState` members and their implementation classes follow a valid topological sort order.
    """

    def test_env_state_topological_sort(
        self,
    ) -> None:
        """
        Verify that each `EnvState` enum member is defined AFTER all the states it depends on (its parents).
        """
        self.env_ctx = VerifyingEnvContext()
        self.env_ctx._entry_func = EntryFunc.func_boot_env
        self.env_ctx._is_app = True
        self.env_ctx._sub_command = max_deps_env_ctx._sub_command

        state_graph_instance = self.env_ctx.state_graph

        # Create a mapping from the state name to its ordinal position in the enum:
        env_state_name_to_ordinal = {env_state.name: index for index, env_state in enumerate(EnvState)}

        order_violations = []
        # Verify that for each state, its parents appear before it in the enum definition:
        for env_state in EnvState:
            state_node = state_graph_instance.get_state_node(env_state.name)
            if state_node is None:
                raise AssertionError(f"`{StateNode.__name__}` for [{env_state.name}] not found")

            for parent_state_name in state_node.get_parent_states():
                if not (
                    env_state_name_to_ordinal[parent_state_name]
                    < env_state_name_to_ordinal[env_state.name]
                    #
                ):
                    order_violations.append(
                        f"enum item definition order violation: "
                        f"[{parent_state_name}] "
                        f"should come before "
                        f"[{env_state.name}]"
                        #
                    )

        _report_order_violations(order_violations)

    def test_bootstrapper_class_definition_order(
        self,
    ) -> None:
        """
        Verify that each state's implementation class is defined AFTER the classes of its parent states.
        """
        self.env_ctx = VerifyingEnvContext()
        self.env_ctx._entry_func = EntryFunc.func_boot_env
        self.env_ctx._is_app = True
        self.env_ctx._sub_command = max_deps_env_ctx._sub_command

        state_graph_instance = self.env_ctx.state_graph

        # Create a mapping from the state name to the line number of its implementation class:
        state_name_to_line_number = {
            env_state.name: get_class_line_number(env_state.value)
            for env_state in EnvState
            #
        }

        # then:
        order_violations = []
        # Verify that for each state, its implementation class is defined after its parents:
        for env_state in EnvState:
            state_node = state_graph_instance.get_state_node(env_state.name)
            if state_node is None:
                raise AssertionError(f"`{StateNode.__name__}` for [{env_state.name}] not found")

            for parent_state_name in state_node.get_parent_states():
                parent_line_number = state_name_to_line_number[parent_state_name]
                child_line_number = state_name_to_line_number[env_state.name]
                if not (parent_line_number < child_line_number):
                    order_violations.append(
                        f"class definition order violation: "
                        f"[{parent_state_name}][line {parent_line_number}] "
                        f"should come before "
                        f"[{env_state.name}][line {child_line_number}] "
                        #
                    )

        _report_order_violations(order_violations)

    def test_bootstrapper_class_definition_matches_env_state_order(self) -> None:
        """
        Verify that implementation classes appear in the file in the exact same order as their `EnvState` enum members.
        """
        order_violations = []
        prev_line_number = -1
        prev_env_state: EnvState | None = None

        for curr_env_state in EnvState:
            curr_line_number = get_class_line_number(curr_env_state.value)

            # `EnvState`-s are already defined in the right order:
            if curr_line_number < prev_line_number:
                assert prev_env_state is not None
                order_violations.append(
                    f"class for "
                    f"[{curr_env_state.name}][line {curr_line_number}] "
                    f"is defined before the class for the preceding enum item "
                    f"[{prev_env_state.name}][line {prev_line_number}] "
                    #
                )
            prev_line_number = curr_line_number
            prev_env_state = curr_env_state

        _report_order_violations(order_violations)
