from __future__ import annotations

from protoprimer.primer_kernel import (
    _ContextBuilder,
    _EntryFunc,
    _EnvState,
    _ExecOperation,
    _TargetState,
)
from local_repo.misc_tools.graph_utils import (
    get_transitive_dependencies,
)


class TestTargetDependencies:
    """
    This test ensures there are no dangling states in the DAG that are not part of target states.
    """

    # These are not dependencies of `_TargetState.target_proto_bootstrap_completed`,
    # but they are dependencies of `_TargetState.target_everything_executed`.
    state_func_boot_env_executed_dependencies = [
        _EnvState.state_input_exec_operation_loaded.name,
        _EnvState.state_input_final_state_eval_finalized.name,
        _EnvState.state_func_boot_env_executed.name,
    ]

    conditionally_missing_func_executed_states = [
        _EnvState.state_func_start_app_executed.name,
        _EnvState.state_func_call_lib_executed.name,
    ]

    def test_all_env_states_are_dependencies_of_target_proto_bootstrap_completed(
        self,
    ):
        # given:

        env_context_instance = (
            _ContextBuilder()
            .entry_func(_EntryFunc.func_boot_env)
            .is_app(True)
            .exec_operation(_ExecOperation.op_boot)
            #
            .build_context()
        )
        state_graph_instance = env_context_instance._state_graph
        final_state_name = _EnvState.state_command_executed.name

        # when:

        all_dependencies = set(
            get_transitive_dependencies(
                state_graph_instance,
                final_state_name,
                env_context_instance,
            )
        )
        all_dependencies.add(final_state_name)

        all_env_state_names = {env_state.name for env_state in _EnvState}
        missing_dependencies = all_env_state_names - all_dependencies

        allowed_missing_dependencies = set(self.state_func_boot_env_executed_dependencies)
        allowed_missing_dependencies.update(self.conditionally_missing_func_executed_states)
        allowed_missing_dependencies.add(_EnvState.state_derived_conf_data_loaded.name)
        allowed_missing_dependencies.add(_EnvState.state_effective_conf_data_printed.name)
        # `state_local_run_dir_abs_path_inited` is only reached via `state_derived_conf_data_loaded`
        # (nothing else consumes the `run` dir yet, unlike `venv`/`log`/`tmp`/`cache`):
        allowed_missing_dependencies.add(_EnvState.state_local_run_dir_abs_path_inited.name)
        allowed_missing_dependencies.add(_EnvState.state_wrap_executed.name)
        allowed_missing_dependencies.add(_EnvState.state_client_func_executed.name)
        allowed_missing_dependencies.add(_EnvState.state_shell_executed.name)
        allowed_missing_dependencies.add(_EnvState.state_start_executed.name)
        allowed_missing_dependencies.add(_EnvState.state_everything_executed.name)
        allowed_missing_dependencies.add(_EnvState.state_is_app_defined.name)

        missing_dependencies -= allowed_missing_dependencies

        # then:

        if missing_dependencies:
            raise AssertionError(
                f"The following `{_EnvState.__name__}` members are not dependencies of "
                f"[{final_state_name}]: {sorted(list(missing_dependencies))}"
                #
            )

    def test_dependencies_of_state_func_boot_env_executed(
        self,
    ):
        # given:

        env_context_instance = (
            _ContextBuilder()
            .entry_func(_EntryFunc.func_boot_env)
            .is_app(True)
            .exec_operation(_ExecOperation.op_boot)
            #
            .build_context()
        )
        state_graph_instance = env_context_instance._state_graph
        final_state_name = _TargetState.target_everything_executed.value.name

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
        all_dependencies_with_extra.update(self.state_func_boot_env_executed_dependencies)

        # then:

        assert all_dependencies_only == all_dependencies_with_extra
