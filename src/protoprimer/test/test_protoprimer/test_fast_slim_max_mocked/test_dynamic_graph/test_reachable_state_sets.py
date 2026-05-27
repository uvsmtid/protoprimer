from __future__ import annotations

from local_test.verified_dynamic_graph import VerifyingEnvContext
from protoprimer.primer_kernel import (
    EntryFunc,
    EnvContext,
    EnvState,
    SubCommand,
)
from local_repo.misc_tools.graph_utils import (
    topological_sort_of_verified_states,
)


def _make_env_ctx(
    entry_func: EntryFunc,
    prepare_venv: bool,
    sub_command: SubCommand | None,
    is_log_enabled: bool,
) -> EnvContext:
    env_ctx = VerifyingEnvContext()
    env_ctx.graph_coordinates.entry_func = entry_func
    env_ctx.graph_coordinates.prepare_venv = prepare_venv
    env_ctx.graph_coordinates.sub_command = sub_command
    env_ctx.graph_coordinates.is_log_enabled = is_log_enabled
    return env_ctx


class TestTopologicalSort:
    """
    Verifies the topologically sorted list of `EnvState.name`-s for each meaningful `GraphCoordinates` combination.

    Each test method:
    *   Constructs an `EnvContext` with specific `GraphCoordinates`.
    *   Calls `topological_sort` (which instantiates nodes via factories — factories use `GraphCoordinates`).
    *   Asserts the sorted list equals the expected hardcoded list.

    The expected list serves as a reviewable snapshot:
    if a factory is modified (parents added/removed for a specific combo), the corresponding test breaks.

    See: FT_77_15_06_50.dynamic_DAG.md
    """

    def test_func_boot_env_and_prepare_venv_true(self):
        """
        `EntryFunc.func_boot_env`, `prepare_venv=True`: the primary bootstrap path.
        """

        # given:
        env_ctx = _make_env_ctx(
            entry_func=EntryFunc.func_boot_env,
            prepare_venv=True,
            sub_command=SubCommand.command_boot,
            is_log_enabled=False,
        )

        # when:
        sorted_names = topological_sort_of_verified_states(
            env_ctx.state_graph,
            env_ctx,
            EnvState.state_everything_executed.name,
        )

        # then:
        assert sorted_names == [
            EnvState.state_input_py_exec_var_loaded.name,
            EnvState.state_input_is_stderr_log_enabled.name,
            EnvState.state_input_stderr_log_level_var_loaded.name,
            EnvState.state_default_stderr_log_handler_configured.name,
            EnvState.state_args_parsed.name,
            EnvState.state_input_stderr_log_level_eval_finalized.name,
            EnvState.state_input_stderr_log_level_handler_configured.name,
            EnvState.state_input_sub_command_arg_loaded.name,
            EnvState.state_input_final_state_eval_finalized.name,
            EnvState.state_func_boot_env_executed.name,
            EnvState.state_everything_executed.name,
        ]

    def test_func_start_app_and_prepare_venv_false(self):
        """
        `EntryFunc.func_start_app`, `prepare_venv=False`: application start path (venv already exists).
        """
        # given:
        env_ctx = _make_env_ctx(
            entry_func=EntryFunc.func_start_app,
            prepare_venv=False,
            sub_command=None,
            is_log_enabled=False,
        )

        # when:
        sorted_names = topological_sort_of_verified_states(
            env_ctx.state_graph,
            env_ctx,
            EnvState.state_everything_executed.name,
        )

        # then:
        assert sorted_names == [
            EnvState.state_input_is_stderr_log_enabled.name,
            EnvState.state_input_final_state_eval_finalized.name,
            EnvState.state_func_start_app_executed.name,
            EnvState.state_everything_executed.name,
        ]

    def test_func_call_lib(self):
        """
        `EntryFunc.func_call_lib`: library call path (e.g., `get_config`).
        """
        # given:
        env_ctx = _make_env_ctx(
            entry_func=EntryFunc.func_call_lib,
            prepare_venv=False,
            sub_command=None,
            is_log_enabled=False,
        )

        # when:
        sorted_names = topological_sort_of_verified_states(
            env_ctx.state_graph,
            env_ctx,
            EnvState.state_everything_executed.name,
        )

        # then:
        assert sorted_names == [
            EnvState.state_input_is_stderr_log_enabled.name,
            EnvState.state_input_final_state_eval_finalized.name,
            EnvState.state_func_call_lib_executed.name,
            EnvState.state_everything_executed.name,
        ]

    def test_func_boot_env_and_prepare_venv_false(self):
        """
        `EntryFunc.func_boot_env`, `prepare_venv=False`: bootstrap without creating/updating `venv`.
        """
        # given:
        env_ctx = _make_env_ctx(
            entry_func=EntryFunc.func_boot_env,
            prepare_venv=False,
            sub_command=SubCommand.command_boot,
            is_log_enabled=False,
        )

        # when:
        sorted_names = topological_sort_of_verified_states(
            env_ctx.state_graph,
            env_ctx,
            EnvState.state_everything_executed.name,
        )

        # then:
        assert sorted_names == [
            EnvState.state_input_py_exec_var_loaded.name,
            EnvState.state_input_is_stderr_log_enabled.name,
            EnvState.state_input_stderr_log_level_var_loaded.name,
            EnvState.state_default_stderr_log_handler_configured.name,
            EnvState.state_args_parsed.name,
            EnvState.state_input_stderr_log_level_eval_finalized.name,
            EnvState.state_input_stderr_log_level_handler_configured.name,
            EnvState.state_input_sub_command_arg_loaded.name,
            EnvState.state_input_final_state_eval_finalized.name,
            EnvState.state_func_boot_env_executed.name,
            EnvState.state_everything_executed.name,
        ]
