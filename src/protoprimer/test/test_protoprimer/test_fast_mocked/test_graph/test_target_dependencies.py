from __future__ import annotations

from protoprimer.primer_kernel import (
    EnvContext,
    EnvState,
    TargetState,
)
from test_protoprimer.test_fast_mocked.misc_tools.graph_utils import (
    get_transitive_dependencies,
)


class TestTargetDependencies:
    """
    This test ensures there are no dangling states in the DAG that are not part of target states.
    """

    # These are not dependencies of `TargetState.target_full_proto_bootstrap`,
    # but they are dependencies of `TargetState.target_run_mode_executed`.
    some_state_run_mode_executed_dependencies = [
        EnvState.state_input_run_mode_arg_loaded.name,
        EnvState.state_input_final_state_eval_finalized.name,
        EnvState.state_run_mode_executed.name,
    ]

    def test_all_env_states_are_dependencies_of_target_full_proto_bootstrap(
        self,
    ):
        # given:

        env_context_instance = EnvContext()
        state_graph_instance = env_context_instance.state_graph
        final_state_name = EnvState.state_command_executed.name

        # when:

        all_dependencies = set(
            get_transitive_dependencies(
                state_graph_instance,
                final_state_name,
            )
        )
        all_dependencies.add(final_state_name)

        all_env_state_names = {env_state.name for env_state in EnvState}
        missing_dependencies = all_env_state_names - all_dependencies

        allowed_missing_dependencies = set(
            self.some_state_run_mode_executed_dependencies
        )
        allowed_missing_dependencies.add(EnvState.state_process_status_initialized.name)
        allowed_missing_dependencies.add(EnvState.state_process_status_reported.name)

        missing_dependencies -= allowed_missing_dependencies

        # then:

        assert not missing_dependencies, (
            f"The following `{EnvState.__name__}` members are not dependencies of "
            f"[{final_state_name}]: {sorted(list(missing_dependencies))}"
        )

    def test_dependencies_of_state_run_mode_executed(
        self,
    ):
        # given:

        env_context_instance = EnvContext()
        state_graph_instance = env_context_instance.state_graph
        final_state_name = TargetState.target_run_mode_executed

        # when:

        all_dependencies_only = set(
            get_transitive_dependencies(
                state_graph_instance,
                final_state_name,
            )
        )
        all_dependencies_only.add(final_state_name)

        # another set which is supposed to be equal:
        all_dependencies_with_extra = set(all_dependencies_only)
        all_dependencies_with_extra.update(
            self.some_state_run_mode_executed_dependencies
        )

        # then:

        assert all_dependencies_only == all_dependencies_with_extra
