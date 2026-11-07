from __future__ import annotations

from local_test.verified_dynamic_graph import VerifyingEnvContext
from protoprimer.primer_kernel import (
    _EntryFunc,
    _EnvContext,
    _EnvState,
    _ExecOperation,
)
from local_repo.misc_tools.graph_utils import (
    topological_sort_of_verified_states,
)


def _make_env_ctx(
    entry_func: _EntryFunc,
    prepare_venv: bool,
    exec_operation: _ExecOperation | None,
    is_log_enabled: bool,
) -> _EnvContext:
    env_ctx = VerifyingEnvContext()
    env_ctx._entry_func = entry_func
    env_ctx._is_app = entry_func in (_EntryFunc.func_boot_env, _EntryFunc.func_run_main)
    env_ctx._prepare_venv = prepare_venv
    env_ctx._exec_operation = exec_operation
    env_ctx._is_log_enabled = is_log_enabled
    return env_ctx


class TestTopologicalSort:
    """
    Verifies the topologically sorted list of `_EnvState.name`-s for each meaningful `_EnvContext` coordinate combination.

    Each test method:
    *   Constructs an `_EnvContext` with specific graph coordinates.
    *   Calls `topological_sort` (which instantiates nodes via factories - factories use `_EnvContext` coordinates).
    *   Asserts the sorted list equals the expected hardcoded list.

    The expected list serves as a reviewable snapshot:
    if a factory is modified (parents added/removed for a specific combo), the corresponding test breaks.

    See: FT_77_15_06_50.dynamic_DAG.md
    """

    def test_func_boot_env_and_prepare_venv_true(self):
        """
        `_EntryFunc.func_boot_env`, `prepare_venv=True`: the primary bootstrap path.
        """

        # given:
        env_ctx = _make_env_ctx(
            entry_func=_EntryFunc.func_boot_env,
            prepare_venv=True,
            exec_operation=_ExecOperation.op_boot,
            is_log_enabled=False,
        )

        # when:
        sorted_names = topological_sort_of_verified_states(
            env_ctx._state_graph,
            env_ctx,
            _EnvState.state_everything_executed.name,
        )

        # then:
        assert sorted_names == [
            _EnvState.state_is_app_defined.name,
            _EnvState.state_input_py_exec_var_loaded.name,
            _EnvState.state_input_is_stderr_log_enabled.name,
            _EnvState.state_input_stderr_log_level_var_loaded.name,
            _EnvState.state_default_stderr_log_handler_configured.name,
            _EnvState.state_args_parsed.name,
            _EnvState.state_input_stderr_log_level_eval_finalized.name,
            _EnvState.state_input_stderr_log_level_handler_configured.name,
            _EnvState.state_input_exec_operation_loaded.name,
            _EnvState.state_input_final_state_eval_finalized.name,
            _EnvState.state_func_boot_env_executed.name,
            _EnvState.state_everything_executed.name,
        ]

    def test_func_start_app_and_prepare_venv_false(self):
        """
        `_EntryFunc.func_start_app`, `prepare_venv=False`: application start path (venv already exists).
        """
        # given:
        env_ctx = _make_env_ctx(
            entry_func=_EntryFunc.func_start_app,
            prepare_venv=False,
            exec_operation=None,
            is_log_enabled=False,
        )

        # when:
        sorted_names = topological_sort_of_verified_states(
            env_ctx._state_graph,
            env_ctx,
            _EnvState.state_everything_executed.name,
        )

        # then:
        assert sorted_names == [
            _EnvState.state_is_app_defined.name,
            _EnvState.state_input_is_stderr_log_enabled.name,
            _EnvState.state_input_final_state_eval_finalized.name,
            _EnvState.state_func_start_app_executed.name,
            _EnvState.state_everything_executed.name,
        ]

    def test_func_call_lib(self):
        """
        `_EntryFunc.func_call_lib`: library call path (e.g., `get_config`).
        """
        # given:
        env_ctx = _make_env_ctx(
            entry_func=_EntryFunc.func_call_lib,
            prepare_venv=False,
            exec_operation=None,
            is_log_enabled=False,
        )

        # when:
        sorted_names = topological_sort_of_verified_states(
            env_ctx._state_graph,
            env_ctx,
            _EnvState.state_everything_executed.name,
        )

        # then:
        assert sorted_names == [
            _EnvState.state_is_app_defined.name,
            _EnvState.state_input_is_stderr_log_enabled.name,
            _EnvState.state_input_final_state_eval_finalized.name,
            _EnvState.state_func_call_lib_executed.name,
            _EnvState.state_everything_executed.name,
        ]

    def test_func_boot_env_and_prepare_venv_false(self):
        """
        `_EntryFunc.func_boot_env`, `prepare_venv=False`: bootstrap without creating/updating `venv`.
        """
        # given:
        env_ctx = _make_env_ctx(
            entry_func=_EntryFunc.func_boot_env,
            prepare_venv=False,
            exec_operation=_ExecOperation.op_boot,
            is_log_enabled=False,
        )

        # when:
        sorted_names = topological_sort_of_verified_states(
            env_ctx._state_graph,
            env_ctx,
            _EnvState.state_everything_executed.name,
        )

        # then:
        assert sorted_names == [
            _EnvState.state_is_app_defined.name,
            _EnvState.state_input_py_exec_var_loaded.name,
            _EnvState.state_input_is_stderr_log_enabled.name,
            _EnvState.state_input_stderr_log_level_var_loaded.name,
            _EnvState.state_default_stderr_log_handler_configured.name,
            _EnvState.state_args_parsed.name,
            _EnvState.state_input_stderr_log_level_eval_finalized.name,
            _EnvState.state_input_stderr_log_level_handler_configured.name,
            _EnvState.state_input_exec_operation_loaded.name,
            _EnvState.state_input_final_state_eval_finalized.name,
            _EnvState.state_func_boot_env_executed.name,
            _EnvState.state_everything_executed.name,
        ]
