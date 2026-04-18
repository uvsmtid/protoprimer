from __future__ import annotations

from protoprimer.primer_kernel import (
    EnvContext,
    EnvState,
    ExecMode,
    TargetState,
)
from test_protoprimer.test_fast_slim_max_mocked.misc_tools.graph_utils import (
    get_transitive_dependencies,
)


class TestTargetDependencies:
    """
    This test ensures there are no dangling states in the DAG that are not part of target states.
    """

    # These are not dependencies of `TargetState.target_proto_bootstrap_completed`,
    # but they are dependencies of `TargetState.target_exec_mode_executed`.
    some_state_exec_mode_executed_dependencies = [
        EnvState.state_input_exec_mode_arg_loaded.name,
        EnvState.state_input_final_state_eval_finalized.name,
        EnvState.state_exec_mode_executed.name,
    ]

    def test_all_env_states_are_dependencies_of_target_proto_bootstrap_completed(
        self,
    ):
        # given:

        env_context_instance = EnvContext()
        env_context_instance.graph_coordinates.exec_mode = ExecMode.mode_boot
        state_graph_instance = env_context_instance.state_graph
        final_state_name = EnvState.state_command_executed.name

        # when:

        all_dependencies = set(
            get_transitive_dependencies(
                state_graph_instance,
                final_state_name,
                env_context_instance,
            )
        )
        all_dependencies.add(final_state_name)

        all_env_state_names = {env_state.name for env_state in EnvState}
        missing_dependencies = all_env_state_names - all_dependencies

        allowed_missing_dependencies = set(self.some_state_exec_mode_executed_dependencies)
        allowed_missing_dependencies.add(EnvState.state_derived_conf_data_loaded.name)
        allowed_missing_dependencies.add(EnvState.state_effective_conf_data_printed.name)

        missing_dependencies -= allowed_missing_dependencies

        # then:

        if missing_dependencies:
            raise AssertionError(
                f"The following `{EnvState.__name__}` members are not dependencies of "
                f"[{final_state_name}]: {sorted(list(missing_dependencies))}"
                #
            )

    def test_dependencies_of_state_exec_mode_executed(
        self,
    ):
        # given:

        env_context_instance = EnvContext()
        env_context_instance.graph_coordinates.exec_mode = ExecMode.mode_boot
        state_graph_instance = env_context_instance.state_graph
        final_state_name = TargetState.target_exec_mode_executed.value.name

        # when:

        all_dependencies_only = set(
            get_transitive_dependencies(
                state_graph_instance,
                final_state_name,
                env_context_instance,
            )
        )
        all_dependencies_only.add(final_state_name)

        # another set which is supposed to be equal:
        all_dependencies_with_extra = set(all_dependencies_only)
        all_dependencies_with_extra.update(self.some_state_exec_mode_executed_dependencies)

        # then:

        assert all_dependencies_only == all_dependencies_with_extra
