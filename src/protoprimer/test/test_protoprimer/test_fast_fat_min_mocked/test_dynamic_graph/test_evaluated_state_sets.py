from __future__ import annotations

import os
import pathlib
import sys
from unittest.mock import patch

from pyfakefs.fake_filesystem import FakeFilesystem

from local_test.fat_mocked_helper import (
    _ExitCalled,
    fat_mock_wrapper,
)
from local_test.integrated_helper import create_max_layout
from local_test.verified_dynamic_graph import (
    TrackingEnvContext,
    TrackingStateGraph,
)
from protoprimer.primer_kernel import (
    EntryFunc,
    EnvState,
    EnvVar,
    StateStride,
)


def _make_tracking_env_ctx(
    entry_func: EntryFunc,
) -> TrackingEnvContext:
    env_ctx = TrackingEnvContext()
    env_ctx._entry_func = entry_func
    env_ctx._is_app = entry_func in (EntryFunc.func_boot_env, EntryFunc.func_run_main)
    env_ctx._state_stride = StateStride.stride_src_updated
    return env_ctx


def _eval_and_collect(
    env_ctx: TrackingEnvContext,
) -> list[str]:
    state_graph: TrackingStateGraph = env_ctx._state_graph
    try:
        state_graph.eval_state(EnvState.state_everything_executed.name)
    except _ExitCalled:
        pass
    return state_graph.get_evaluated_state_names()


def _verify_actual_have_no_prohibited_state_names(
    prohibited_state_names: list[str],
    actual_state_names: list[str],
):
    for prohibited_state_name in prohibited_state_names:
        if prohibited_state_name in actual_state_names:
            raise AssertionError(f"`prohibited_state_name` [{prohibited_state_name}] is in `actual_state_names`")


def _verify_actual_have_all_mandatory_state_names(
    mandatory_state_names: list[str],
    actual_state_names: list[str],
):
    for mandatory_state_name in mandatory_state_names:
        if mandatory_state_name not in actual_state_names:
            raise AssertionError(f"`mandatory_state_name` [{mandatory_state_name}] is not in `actual_state_names`")


class TestEvaluatedStateSets:
    """
    Verifies the actual set of `EnvState` names evaluated during graph execution.

    Each function uses a meaningful `EnvContext` coordinate combination.

    Each test method:
    *   Use fake filesystem with `create_max_layout` (inside `fat_mock_wrapper`).
    *   Use `StateStride.stride_src_updated` to skip process-restart transitions.
    *   Runs the graph inside `fat_mock_wrapper` (which mocks execution side effects).
    *   Asserts the collected state names match the expected list.

    See: FT_77_15_06_50.dynamic_DAG.md
    """

    def test_func_boot_env(self, fs: FakeFilesystem):
        """
        `EntryFunc.func_boot_env`, `prepare_venv=True`: bootstrap creates venv.
        """
        mock_test_dir = fs.create_dir("/mock_test_dir")

        with fat_mock_wrapper(fs):
            (proto_kernel_abs_path, _, _) = create_max_layout(pathlib.Path(mock_test_dir.path))

            env_ctx = _make_tracking_env_ctx(
                entry_func=EntryFunc.func_boot_env,
            )
            os.environ[EnvVar.var_PROTOPRIMER_PROTO_CODE.value] = str(proto_kernel_abs_path)

            # Patch `argv` - otherwise, `argparse` will see args of the test runner:
            with patch.object(sys, "argv", [str(proto_kernel_abs_path)]):
                actual_state_names = _eval_and_collect(env_ctx)

        assert actual_state_names == [
            EnvState.state_is_app_defined.name,
            EnvState.state_input_py_exec_var_loaded.name,
            EnvState.state_input_is_stderr_log_enabled.name,
            EnvState.state_input_stderr_log_level_var_loaded.name,
            EnvState.state_default_stderr_log_handler_configured.name,
            EnvState.state_args_parsed.name,
            EnvState.state_input_stderr_log_level_eval_finalized.name,
            EnvState.state_input_stderr_log_level_handler_configured.name,
            EnvState.state_input_sub_command_arg_loaded.name,
            EnvState.state_input_final_state_eval_finalized.name,
            EnvState.state_input_proto_code_file_abs_path_var_loaded.name,
            EnvState.state_input_start_id_var_loaded.name,
            EnvState.state_stride_py_arbitrary_reached.name,
            EnvState.state_proto_code_file_abs_path_inited.name,
            EnvState.state_print_conf_finalized.name,
            EnvState.state_primer_conf_file_abs_path_inited.name,
            EnvState.state_primer_conf_file_data_loaded.name,
            EnvState.state_ref_root_dir_abs_path_inited.name,
            EnvState.state_global_conf_dir_abs_path_inited.name,
            EnvState.state_global_conf_file_abs_path_inited.name,
            EnvState.state_client_conf_file_data_loaded.name,
            EnvState.state_selected_env_dir_rel_path_inited.name,
            EnvState.state_local_conf_symlink_abs_path_inited.name,
            EnvState.state_local_conf_file_abs_path_inited.name,
            EnvState.state_env_conf_file_data_loaded.name,
            EnvState.state_local_venv_dir_abs_path_inited.name,
            EnvState.state_local_cache_dir_abs_path_inited.name,
            EnvState.state_version_constraints_file_basename_inited.name,
            EnvState.state_required_python_version_inited.name,
            EnvState.state_python_selector_file_abs_path_inited.name,
            EnvState.state_selected_python_file_abs_path_inited.name,
            EnvState.state_venv_driver_inited.name,
            EnvState.state_prepare_venv_finalized.name,
            EnvState.state_local_tmp_dir_abs_path_inited.name,
            EnvState.state_local_log_dir_abs_path_inited.name,
            EnvState.state_default_file_log_handler_configured.name,
            EnvState.state_stride_py_required_reached.name,
            EnvState.state_reboot_triggered.name,
            EnvState.state_venv_driver_prepared.name,
            EnvState.state_project_descriptors_inited.name,
            EnvState.state_install_specs_inited.name,
            EnvState.state_stride_py_venv_reached.name,
            EnvState.state_protoprimer_package_installed.name,
            EnvState.state_version_constraints_generated.name,
            EnvState.state_stride_deps_updated_reached.name,
            EnvState.state_proto_code_updated.name,
            EnvState.state_stride_src_updated_reached.name,
            EnvState.state_input_command_line.name,
            EnvState.state_command_executed.name,
            EnvState.state_func_boot_env_executed.name,
            EnvState.state_everything_executed.name,
        ]

        # TODO: TODO_60_63_68_81.refactor_DAG_builder.md
        #       Add assertions for state_name-s which should or should not be seen in this scenario.

        mandatory_state_names = [
            # args:
            EnvState.state_args_parsed.name,
            # logs:
            EnvState.state_input_stderr_log_level_handler_configured.name,
            EnvState.state_default_file_log_handler_configured.name,
            # main:
            EnvState.state_everything_executed.name,
            EnvState.state_func_boot_env_executed.name,
            EnvState.state_command_executed.name,
        ]

        _verify_actual_have_all_mandatory_state_names(
            mandatory_state_names,
            actual_state_names,
        )

        prohibited_state_names = [
            EnvState.state_func_start_app_executed.name,
        ]

        _verify_actual_have_no_prohibited_state_names(
            prohibited_state_names,
            actual_state_names,
        )

    def test_func_start_app(self, fs: FakeFilesystem):
        """
        `EntryFunc.func_start_app`, `prepare_venv=False`: app start (venv already exists).
        """
        mock_test_dir = fs.create_dir("/mock_test_dir")

        with fat_mock_wrapper(fs):
            (proto_kernel_abs_path, _, _) = create_max_layout(pathlib.Path(mock_test_dir.path))

            env_ctx = _make_tracking_env_ctx(
                entry_func=EntryFunc.func_start_app,
            )
            os.environ[EnvVar.var_PROTOPRIMER_PROTO_CODE.value] = str(proto_kernel_abs_path)

            actual_state_names = _eval_and_collect(env_ctx)

        assert actual_state_names == [
            EnvState.state_is_app_defined.name,
            EnvState.state_input_is_stderr_log_enabled.name,
            EnvState.state_input_final_state_eval_finalized.name,
            EnvState.state_input_start_id_var_loaded.name,
            EnvState.state_input_proto_code_file_abs_path_var_loaded.name,
            EnvState.state_stride_py_arbitrary_reached.name,
            EnvState.state_proto_code_file_abs_path_inited.name,
            EnvState.state_print_conf_finalized.name,
            EnvState.state_primer_conf_file_abs_path_inited.name,
            EnvState.state_primer_conf_file_data_loaded.name,
            EnvState.state_ref_root_dir_abs_path_inited.name,
            EnvState.state_global_conf_dir_abs_path_inited.name,
            EnvState.state_global_conf_file_abs_path_inited.name,
            EnvState.state_client_conf_file_data_loaded.name,
            EnvState.state_selected_env_dir_rel_path_inited.name,
            EnvState.state_local_conf_symlink_abs_path_inited.name,
            EnvState.state_local_conf_file_abs_path_inited.name,
            EnvState.state_env_conf_file_data_loaded.name,
            EnvState.state_local_venv_dir_abs_path_inited.name,
            EnvState.state_stride_py_venv_reached.name,
            EnvState.state_func_start_app_executed.name,
            EnvState.state_everything_executed.name,
        ]

        # TODO: TODO_60_63_68_81.refactor_DAG_builder.md
        #       Add assertions for state_name-s which should or should not be seen in this scenario.

        mandatory_state_names = [
            EnvState.state_everything_executed.name,
            EnvState.state_func_start_app_executed.name,
            EnvState.state_stride_py_venv_reached.name,
        ]

        _verify_actual_have_all_mandatory_state_names(
            mandatory_state_names,
            actual_state_names,
        )

        prohibited_state_names = [
            # args:
            EnvState.state_input_sub_command_arg_loaded.name,
            # python:
            EnvState.state_required_python_version_inited.name,
            EnvState.state_python_selector_file_abs_path_inited.name,
            EnvState.state_selected_python_file_abs_path_inited.name,
            EnvState.state_reboot_triggered.name,
            EnvState.state_venv_driver_prepared.name,
            # wrong func:
            EnvState.state_func_boot_env_executed.name,
            # logs:
            EnvState.state_input_stderr_log_level_handler_configured.name,
            EnvState.state_default_file_log_handler_configured.name,
        ]

        _verify_actual_have_no_prohibited_state_names(
            prohibited_state_names,
            actual_state_names,
        )

    def test_func_call_lib(self, fs: FakeFilesystem):
        """
        `EntryFunc.func_call_lib`: library call path (e.g., `get_config`).
        """
        mock_test_dir = fs.create_dir("/mock_test_dir")

        with fat_mock_wrapper(fs):
            (proto_kernel_abs_path, _, _) = create_max_layout(pathlib.Path(mock_test_dir.path))

            env_ctx = _make_tracking_env_ctx(
                entry_func=EntryFunc.func_call_lib,
            )
            env_ctx._proto_kernel_abs_path = str(proto_kernel_abs_path)

            actual_state_names = _eval_and_collect(env_ctx)

        assert actual_state_names == [
            EnvState.state_is_app_defined.name,
            EnvState.state_input_is_stderr_log_enabled.name,
            EnvState.state_input_final_state_eval_finalized.name,
            EnvState.state_proto_code_file_abs_path_inited.name,
            EnvState.state_primer_conf_file_abs_path_inited.name,
            EnvState.state_print_conf_finalized.name,
            EnvState.state_primer_conf_file_data_loaded.name,
            EnvState.state_ref_root_dir_abs_path_inited.name,
            EnvState.state_global_conf_dir_abs_path_inited.name,
            EnvState.state_global_conf_file_abs_path_inited.name,
            EnvState.state_client_conf_file_data_loaded.name,
            EnvState.state_selected_env_dir_rel_path_inited.name,
            EnvState.state_local_conf_symlink_abs_path_inited.name,
            EnvState.state_local_conf_file_abs_path_inited.name,
            EnvState.state_env_conf_file_data_loaded.name,
            EnvState.state_required_python_version_inited.name,
            EnvState.state_python_selector_file_abs_path_inited.name,
            EnvState.state_selected_python_file_abs_path_inited.name,
            EnvState.state_local_venv_dir_abs_path_inited.name,
            EnvState.state_local_log_dir_abs_path_inited.name,
            EnvState.state_local_tmp_dir_abs_path_inited.name,
            EnvState.state_local_cache_dir_abs_path_inited.name,
            EnvState.state_venv_driver_inited.name,
            EnvState.state_version_constraints_file_basename_inited.name,
            EnvState.state_project_descriptors_inited.name,
            EnvState.state_derived_conf_data_loaded.name,
            EnvState.state_func_call_lib_executed.name,
            EnvState.state_everything_executed.name,
        ]

        # TODO: TODO_60_63_68_81.refactor_DAG_builder.md
        #       Add assertions for state_name-s which should or should not be seen in this scenario.

        mandatory_state_names = [
            EnvState.state_everything_executed.name,
            EnvState.state_func_call_lib_executed.name,
            EnvState.state_derived_conf_data_loaded.name,
        ]

        _verify_actual_have_all_mandatory_state_names(
            mandatory_state_names,
            actual_state_names,
        )

        prohibited_state_names = [
            # args:
            EnvState.state_input_sub_command_arg_loaded.name,
            # logs:
            EnvState.state_input_stderr_log_level_handler_configured.name,
            EnvState.state_default_file_log_handler_configured.name,
        ]

        _verify_actual_have_no_prohibited_state_names(
            prohibited_state_names,
            actual_state_names,
        )
