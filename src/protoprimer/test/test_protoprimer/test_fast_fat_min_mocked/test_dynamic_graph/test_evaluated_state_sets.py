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
    SubCommand,
)


def _make_tracking_env_ctx(
    entry_func: EntryFunc,
    prepare_venv: bool,
) -> TrackingEnvContext:
    env_ctx = TrackingEnvContext()
    env_ctx.graph_coordinates.entry_func = entry_func
    env_ctx.graph_coordinates.prepare_venv = prepare_venv
    env_ctx.state_stride = StateStride.stride_src_updated
    return env_ctx


def _eval_and_collect(
    env_ctx: TrackingEnvContext,
) -> list[str]:
    state_graph: TrackingStateGraph = env_ctx.state_graph
    try:
        state_graph.eval_state(EnvState.state_everything_executed.name)
    except _ExitCalled:
        pass
    return state_graph.get_evaluated_state_names()


class TestEvaluatedStateSets:
    """
    Verifies the actual set of `EnvState` names evaluated during graph execution.

    Each function uses a meaningful `GraphCoordinates` combination.

    Each test method:
    *   Use fake filesystem with `create_max_layout` (inside `fat_mock_wrapper`).
    *   Use `state_stride = stride_src_updated` to skip process-restart transitions.
    *   Runs the graph inside `fat_mock_wrapper` (which mocks execution side effects).
    *   Asserts the collected state names match the expected list.

    See: FT_77_15_06_50.dynamic_DAG.md
    """

    def test_func_boot_env_and_prepare_venv_true(self, fs: FakeFilesystem):
        """
        `EntryFunc.func_boot_env`, `prepare_venv=True`: bootstrap creates venv.
        """
        mock_test_dir = fs.create_dir("/mock_test_dir")

        with fat_mock_wrapper(fs):
            (proto_kernel_abs_path, _, _) = create_max_layout(pathlib.Path(mock_test_dir.path))

            env_ctx = _make_tracking_env_ctx(
                entry_func=EntryFunc.func_boot_env,
                prepare_venv=True,
            )
            env_ctx.proto_code = str(proto_kernel_abs_path)
            os.environ[EnvVar.var_PROTOPRIMER_PROTO_CODE.value] = str(proto_kernel_abs_path)

            with patch.object(sys, "argv", [str(proto_kernel_abs_path), SubCommand.command_boot.value]):
                state_names = _eval_and_collect(env_ctx)

        assert state_names == [
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

    def test_func_start_app_and_prepare_venv_false(self, fs: FakeFilesystem):
        """
        `EntryFunc.func_start_app`, `prepare_venv=False`: app start (venv already exists).
        """
        mock_test_dir = fs.create_dir("/mock_test_dir")

        with fat_mock_wrapper(fs):
            (proto_kernel_abs_path, _, _) = create_max_layout(pathlib.Path(mock_test_dir.path))

            env_ctx = _make_tracking_env_ctx(
                entry_func=EntryFunc.func_start_app,
                prepare_venv=False,
            )
            env_ctx.proto_code = str(proto_kernel_abs_path)
            os.environ[EnvVar.var_PROTOPRIMER_PROTO_CODE.value] = str(proto_kernel_abs_path)

            state_names = _eval_and_collect(env_ctx)

        assert state_names == [
            EnvState.state_input_is_stderr_log_enabled.name,
            EnvState.state_input_final_state_eval_finalized.name,
            EnvState.state_input_proto_code_file_abs_path_var_loaded.name,
            EnvState.state_input_sub_command_arg_loaded.name,
            EnvState.state_input_start_id_var_loaded.name,
            EnvState.state_stride_py_arbitrary_reached.name,
            EnvState.state_proto_code_file_abs_path_inited.name,
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
            EnvState.state_local_tmp_dir_abs_path_inited.name,
            EnvState.state_input_py_exec_var_loaded.name,
            EnvState.state_input_stderr_log_level_var_loaded.name,
            EnvState.state_default_stderr_log_handler_configured.name,
            EnvState.state_input_stderr_log_level_eval_finalized.name,
            EnvState.state_input_stderr_log_level_handler_configured.name,
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
            EnvState.state_func_start_app_executed.name,
            EnvState.state_everything_executed.name,
        ]

        # TODO: TODO_60_63_68_81.refactor_DAG_builder.md
        #       Add assertions for state_name-s which should or should not be seen in this scenario.

    def test_func_call_lib(self, fs: FakeFilesystem):
        """
        `EntryFunc.func_call_lib`: library call path (e.g., `get_config`).
        """
        mock_test_dir = fs.create_dir("/mock_test_dir")

        with fat_mock_wrapper(fs):
            (proto_kernel_abs_path, _, _) = create_max_layout(pathlib.Path(mock_test_dir.path))

            env_ctx = _make_tracking_env_ctx(
                entry_func=EntryFunc.func_call_lib,
                prepare_venv=False,
            )
            env_ctx.proto_code = str(proto_kernel_abs_path)

            state_names = _eval_and_collect(env_ctx)

        assert state_names == [
            EnvState.state_input_is_stderr_log_enabled.name,
            EnvState.state_input_final_state_eval_finalized.name,
            EnvState.state_proto_code_file_abs_path_inited.name,
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
            EnvState.state_input_sub_command_arg_loaded.name,
            EnvState.state_input_start_id_var_loaded.name,
            EnvState.state_version_constraints_file_basename_inited.name,
            EnvState.state_required_python_version_inited.name,
            EnvState.state_python_selector_file_abs_path_inited.name,
            EnvState.state_selected_python_file_abs_path_inited.name,
            EnvState.state_venv_driver_inited.name,
            EnvState.state_local_tmp_dir_abs_path_inited.name,
            EnvState.state_input_py_exec_var_loaded.name,
            EnvState.state_input_stderr_log_level_var_loaded.name,
            EnvState.state_default_stderr_log_handler_configured.name,
            EnvState.state_input_stderr_log_level_eval_finalized.name,
            EnvState.state_input_stderr_log_level_handler_configured.name,
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
            EnvState.state_func_call_lib_executed.name,
            EnvState.state_everything_executed.name,
        ]

        # TODO: TODO_60_63_68_81.refactor_DAG_builder.md
        #       Add assertions for state_name-s which should or should not be seen in this scenario.

    def test_func_call_lib_get_config_leap_derived(self, fs: FakeFilesystem):
        """
        `EntryFunc.func_call_lib` evaluating `state_derived_conf_data_loaded`
        (as `get_config(ConfLeap.leap_derived)` does — no `state_everything_executed`).
        """
        mock_test_dir = fs.create_dir("/mock_test_dir")

        with fat_mock_wrapper(fs):
            (proto_kernel_abs_path, _, _) = create_max_layout(pathlib.Path(mock_test_dir.path))

            env_ctx = _make_tracking_env_ctx(
                entry_func=EntryFunc.func_call_lib,
                prepare_venv=False,
            )
            env_ctx.proto_code = str(proto_kernel_abs_path)

            state_graph: TrackingStateGraph = env_ctx.state_graph
            state_graph.eval_state(EnvState.state_derived_conf_data_loaded.name)
            state_names = state_graph.get_evaluated_state_names()

        assert state_names == [
            EnvState.state_proto_code_file_abs_path_inited.name,
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
        ]

        # TODO: TODO_60_63_68_81.refactor_DAG_builder.md
        #       Add assertions for state_name-s which should or should not be seen in this scenario.

    def test_func_boot_env_and_prepare_venv_false(self, fs: FakeFilesystem):
        """
        `EntryFunc.func_boot_env`, `prepare_venv=False`: bootstrap skips venv creation.
        """
        mock_test_dir = fs.create_dir("/mock_test_dir")

        with fat_mock_wrapper(fs):
            (proto_kernel_abs_path, _, _) = create_max_layout(pathlib.Path(mock_test_dir.path))

            env_ctx = _make_tracking_env_ctx(
                entry_func=EntryFunc.func_boot_env,
                prepare_venv=False,
            )
            env_ctx.proto_code = str(proto_kernel_abs_path)
            os.environ[EnvVar.var_PROTOPRIMER_PROTO_CODE.value] = str(proto_kernel_abs_path)

            with patch.object(sys, "argv", [str(proto_kernel_abs_path), SubCommand.command_boot.value]):
                state_names = _eval_and_collect(env_ctx)

        assert state_names == [
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
