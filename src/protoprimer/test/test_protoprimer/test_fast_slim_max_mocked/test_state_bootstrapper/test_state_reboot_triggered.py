from unittest.mock import (
    patch,
)

import pytest

from local_test.mock_verifier import (
    assert_parent_factories_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_input_start_id_var_loaded,
    Bootstrapper_state_local_conf_symlink_abs_path_inited,
    Bootstrapper_state_local_tmp_dir_abs_path_inited,
    Bootstrapper_state_local_venv_dir_abs_path_inited,
    Bootstrapper_state_version_constraints_file_basename_inited,
    ContextBuilder,
    EntryFunc,
    Factory_state_prepare_venv_finalized,
    Factory_state_proto_code_file_abs_path_inited,
    Factory_state_stride_py_required_reached,
    CommandAction,
    ConfConstEnv,
    EnvState,
    SubCommand,
    StateStride,
    Factory_state_input_sub_command_arg_loaded,
)


@pytest.fixture
def env_ctx():
    return (
        ContextBuilder()
        #
        .entry_func(EntryFunc.func_boot_env)
        #
        .is_app(True)
        #
        .build_context()
    )


def test_relationship():
    assert_test_module_name_embeds_str(EnvState.state_reboot_triggered.name)


@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.create_state_node")
@patch("os.path.exists")
@patch("os.remove")
@patch(f"{primer_kernel.__name__}.shutil.move")
@patch(f"{primer_kernel.__name__}.{Factory_state_stride_py_required_reached.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_tmp_dir_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_version_constraints_file_basename_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_symlink_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Factory_state_proto_code_file_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Factory_state_prepare_venv_finalized.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Factory_state_input_sub_command_arg_loaded.__name__}.create_state_node")
def test_reboot_true(
    mock_state_input_sub_command_arg_loaded,
    mock_state_prepare_venv_finalized,
    mock_state_proto_code_file_abs_path_inited,
    mock_state_local_venv_dir_abs_path_inited,
    mock_state_local_conf_symlink_abs_path_inited,
    mock_state_version_constraints_file_basename_inited,
    mock_state_local_tmp_dir_abs_path_inited,
    mock_state_stride_py_required_reached,
    mock_shutil_move,
    mock_os_remove,
    mock_os_path_exists,
    mock_state_input_start_id_var_loaded,
    env_ctx,
):

    # given:

    assert_parent_factories_mocked(
        env_ctx,
        EnvState.state_reboot_triggered.name,
    )
    mock_state_input_sub_command_arg_loaded.return_value.eval_own_state.return_value = SubCommand.command_reboot
    mock_state_input_start_id_var_loaded.return_value.eval_own_state.return_value = "mock_start_id"

    py_exec = StateStride.stride_py_required
    mock_state_stride_py_required_reached.return_value.eval_own_state.return_value = py_exec
    env_ctx._state_stride = py_exec

    mock_state_local_venv_dir_abs_path_inited.return_value.eval_own_state.return_value = "/path/to/venv"
    mock_state_local_tmp_dir_abs_path_inited.return_value.eval_own_state.return_value = "/path/to/tmp"
    mock_state_local_conf_symlink_abs_path_inited.return_value.eval_own_state.return_value = "/path/to/conf"
    mock_state_version_constraints_file_basename_inited.return_value.eval_own_state.return_value = ConfConstEnv.default_version_constraints_file_basename
    mock_os_path_exists.return_value = True

    # when:
    state_value = env_ctx.eval_state(EnvState.state_reboot_triggered.name)

    # then:
    assert state_value is True
    mock_shutil_move.assert_called_once_with("/path/to/venv", "/path/to/tmp/venv.before.mock_start_id")
    mock_os_remove.assert_called_once_with(f"/path/to/conf/{ConfConstEnv.default_version_constraints_file_basename}")


@patch("os.path.exists")
@patch("os.remove")
@patch("shutil.move")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Factory_state_stride_py_required_reached.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_tmp_dir_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_version_constraints_file_basename_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_symlink_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Factory_state_proto_code_file_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Factory_state_prepare_venv_finalized.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Factory_state_input_sub_command_arg_loaded.__name__}.create_state_node")
def test_reboot_false(
    mock_state_input_sub_command_arg_loaded,
    mock_state_prepare_venv_finalized,
    mock_state_proto_code_file_abs_path_inited,
    mock_state_local_venv_dir_abs_path_inited,
    mock_state_local_conf_symlink_abs_path_inited,
    mock_state_version_constraints_file_basename_inited,
    mock_state_local_tmp_dir_abs_path_inited,
    mock_state_stride_py_required_reached,
    mock_state_input_start_id_var_loaded,
    mock_shutil_move,
    mock_os_remove,
    mock_os_path_exists,
    env_ctx,
):
    # given:
    assert_parent_factories_mocked(
        env_ctx,
        EnvState.state_reboot_triggered.name,
    )
    mock_state_input_sub_command_arg_loaded.return_value.eval_own_state.return_value = SubCommand.command_boot

    py_exec = StateStride.stride_py_required
    mock_state_stride_py_required_reached.return_value.eval_own_state.return_value = py_exec
    env_ctx._state_stride = py_exec

    # when:
    state_value = env_ctx.eval_state(EnvState.state_reboot_triggered.name)

    # then:
    assert state_value is False
    mock_shutil_move.assert_not_called()
    mock_os_remove.assert_not_called()


@patch("os.path.exists")
@patch("os.remove")
@patch("shutil.move")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Factory_state_stride_py_required_reached.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_tmp_dir_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_version_constraints_file_basename_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_symlink_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Factory_state_proto_code_file_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Factory_state_prepare_venv_finalized.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Factory_state_input_sub_command_arg_loaded.__name__}.create_state_node")
def test_reboot_true_but_py_exec_not_required(
    mock_state_input_sub_command_arg_loaded,
    mock_state_prepare_venv_finalized,
    mock_state_proto_code_file_abs_path_inited,
    mock_state_local_venv_dir_abs_path_inited,
    mock_state_local_conf_symlink_abs_path_inited,
    mock_state_version_constraints_file_basename_inited,
    mock_state_local_tmp_dir_abs_path_inited,
    mock_state_stride_py_required_reached,
    mock_state_input_start_id_var_loaded,
    mock_shutil_move,
    mock_os_remove,
    mock_os_path_exists,
    env_ctx,
):
    # given:
    assert_parent_factories_mocked(
        env_ctx,
        EnvState.state_reboot_triggered.name,
    )
    mock_state_input_sub_command_arg_loaded.return_value.eval_own_state.return_value = SubCommand.command_reboot
    mock_state_input_start_id_var_loaded.return_value.eval_own_state.return_value = "mock_start_id"

    py_exec = StateStride.stride_py_venv
    mock_state_stride_py_required_reached.return_value.eval_own_state.return_value = py_exec
    env_ctx._state_stride = py_exec

    # when:
    state_value = env_ctx.eval_state(EnvState.state_reboot_triggered.name)

    # then:
    assert state_value is False
    mock_shutil_move.assert_not_called()
    mock_os_remove.assert_not_called()
