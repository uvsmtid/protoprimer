import argparse
from unittest.mock import (
    patch,
)

import pytest

from local_test.mock_verifier import (
    assert_parent_states_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_args_parsed,
    Bootstrapper_state_local_conf_symlink_abs_path_inited,
    Bootstrapper_state_local_tmp_dir_abs_path_inited,
    Bootstrapper_state_local_venv_dir_abs_path_inited,
    Bootstrapper_state_proto_code_file_abs_path_inited,
    Bootstrapper_state_input_start_id_var_loaded,
    Bootstrapper_state_py_exec_required_reached,
    CommandAction,
    ConfConstEnv,
    EnvContext,
    EnvState,
    ParsedArg,
    PythonExecutable,
    RunMode,
)


@pytest.fixture
def env_ctx():
    return EnvContext()


def test_relationship():
    assert_test_module_name_embeds_str(EnvState.state_reinstall_triggered.name)


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.eval_own_state"
)
@patch("os.path.exists")
@patch("os.remove")
@patch(f"{primer_kernel.__name__}.shutil.move")
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_required_reached.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_local_tmp_dir_abs_path_inited.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_symlink_abs_path_inited.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_file_abs_path_inited.__name__}.eval_own_state"
)
def test_reinstall_true(
    mock_state_proto_code_file_abs_path_inited,
    mock_state_args_parsed,
    mock_state_local_venv_dir_abs_path_inited,
    mock_state_local_conf_symlink_abs_path_inited,
    mock_state_local_tmp_dir_abs_path_inited,
    mock_state_py_exec_required_reached,
    mock_shutil_move,
    mock_os_remove,
    mock_os_path_exists,
    mock_state_input_start_id_var_loaded,
    env_ctx,
):

    # given:

    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_reinstall_triggered.name,
    )
    mock_state_args_parsed.return_value = argparse.Namespace(
        **{
            ParsedArg.name_run_mode.value: RunMode.mode_upgrade.value,
        }
    )
    mock_state_input_start_id_var_loaded.return_value = "mock_start_id"
    mock_state_py_exec_required_reached.return_value = PythonExecutable.py_exec_required
    mock_state_local_venv_dir_abs_path_inited.return_value = "/path/to/venv"
    mock_state_local_tmp_dir_abs_path_inited.return_value = "/path/to/tmp"
    mock_state_local_conf_symlink_abs_path_inited.return_value = "/path/to/conf"
    mock_os_path_exists.return_value = True

    # when:
    state_value = env_ctx.state_graph.eval_state(
        EnvState.state_reinstall_triggered.name
    )

    # then:
    assert state_value is True
    mock_shutil_move.assert_called_once_with(
        "/path/to/venv", "/path/to/tmp/venv.before.mock_start_id"
    )
    mock_os_remove.assert_called_once_with(
        f"/path/to/conf/{ConfConstEnv.constraints_txt_basename}"
    )


@patch("os.path.exists")
@patch("os.remove")
@patch("shutil.move")
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_required_reached.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_local_tmp_dir_abs_path_inited.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_symlink_abs_path_inited.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_file_abs_path_inited.__name__}.eval_own_state"
)
def test_reinstall_false(
    mock_state_proto_code_file_abs_path_inited,
    mock_state_args_parsed,
    mock_state_local_venv_dir_abs_path_inited,
    mock_state_local_conf_symlink_abs_path_inited,
    mock_state_local_tmp_dir_abs_path_inited,
    mock_state_py_exec_required_reached,
    mock_state_input_start_id_var_loaded,
    mock_shutil_move,
    mock_os_remove,
    mock_os_path_exists,
    env_ctx,
):
    # given:
    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_reinstall_triggered.name,
    )
    mock_state_args_parsed.return_value = argparse.Namespace(
        **{
            ParsedArg.name_run_mode.value: RunMode.mode_prime.value,
        }
    )
    mock_state_py_exec_required_reached.return_value = PythonExecutable.py_exec_required

    # when:
    state_value = env_ctx.state_graph.eval_state(
        EnvState.state_reinstall_triggered.name
    )

    # then:
    assert state_value is False
    mock_shutil_move.assert_not_called()
    mock_os_remove.assert_not_called()


@patch("os.path.exists")
@patch("os.remove")
@patch("shutil.move")
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_required_reached.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_local_tmp_dir_abs_path_inited.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_symlink_abs_path_inited.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_file_abs_path_inited.__name__}.eval_own_state"
)
def test_reinstall_true_but_py_exec_not_required(
    mock_state_proto_code_file_abs_path_inited,
    mock_state_args_parsed,
    mock_state_local_venv_dir_abs_path_inited,
    mock_state_local_conf_symlink_abs_path_inited,
    mock_state_local_tmp_dir_abs_path_inited,
    mock_state_py_exec_required_reached,
    mock_state_input_start_id_var_loaded,
    mock_shutil_move,
    mock_os_remove,
    mock_os_path_exists,
    env_ctx,
):
    # given:
    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_reinstall_triggered.name,
    )
    mock_state_args_parsed.return_value = argparse.Namespace(
        **{
            ParsedArg.name_run_mode.value: CommandAction.action_reinstall.value,
        }
    )
    mock_state_input_start_id_var_loaded.return_value = "mock_start_id"
    mock_state_py_exec_required_reached.return_value = PythonExecutable.py_exec_venv

    # when:
    state_value = env_ctx.state_graph.eval_state(
        EnvState.state_reinstall_triggered.name
    )

    # then:
    assert state_value is False
    mock_shutil_move.assert_not_called()
    mock_os_remove.assert_not_called()
