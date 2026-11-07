from unittest.mock import (
    Mock,
    patch,
)

import pytest

from local_test.mock_verifier import (
    assert_parent_factories_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    _Node_state_local_cache_dir_abs_path_inited,
    _Factory_state_reset_triggered,
    _Node_state_selected_python_file_abs_path_inited,
    _Node_state_venv_driver_inited,
    _ContextBuilder,
    _EntryFunc,
    _EnvState,
    _VenvDriverPip,
    VenvDriverType,
    _VenvDriverUv,
    _Node_state_local_venv_dir_abs_path_inited,
    _Factory_state_input_exec_operation_loaded,
)


@pytest.fixture
def env_ctx():
    return (
        _ContextBuilder()
        #
        .entry_func(_EntryFunc.func_boot_env)
        #
        .is_app(True)
        #
        .build_context()
    )


def test_relationship():
    assert_test_module_name_embeds_str(_EnvState.state_venv_driver_prepared.name)


@patch(f"{primer_kernel.__name__}.{_Node_state_local_venv_dir_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{_Node_state_venv_driver_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{_Factory_state_reset_triggered.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{_Node_state_local_cache_dir_abs_path_inited.__name__}.create_state_node")
@patch("protoprimer.primer_kernel._Node_state_required_python_version_inited.create_state_node")
@patch(f"{primer_kernel.__name__}.{_Node_state_selected_python_file_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{_Factory_state_input_exec_operation_loaded.__name__}.create_state_node")
def test_pip_driver_inited(
    mock_input_exec_operation_loaded,
    mock_state_selected_python_file_abs_path_inited,
    mock_state_required_python_version_inited,
    mock_state_local_cache_dir_abs_path_inited,
    mock_state_reset_triggered,
    mock_state_venv_driver_inited,
    mock_state_local_venv_dir_abs_path_inited,
    env_ctx,
):
    # given:
    assert_parent_factories_mocked(
        env_ctx,
        _EnvState.state_venv_driver_prepared.name,
    )
    mock_state_venv_driver_inited.return_value.eval_own_state.return_value = VenvDriverType.venv_pip
    mock_state_selected_python_file_abs_path_inited.return_value.eval_own_state.return_value = "/usr/bin/python"
    mock_state_local_cache_dir_abs_path_inited.return_value.eval_own_state.return_value = "/cache"
    mock_state_reset_triggered.return_value.eval_own_state.return_value = False
    mock_state_local_venv_dir_abs_path_inited.return_value.eval_own_state.return_value = "/venv"

    # when:
    state_value = env_ctx.eval_state(_EnvState.state_venv_driver_prepared.name)

    # then:
    assert isinstance(state_value, _VenvDriverPip)


@patch(f"{primer_kernel.__name__}.os.path.isfile")
@patch(f"{primer_kernel.__name__}.os.path.exists")
@patch(f"{primer_kernel.__name__}._VenvDriverPip.install_packages")
@patch(f"{primer_kernel.__name__}._VenvDriverPip.create_venv")
@patch(f"{primer_kernel.__name__}.{_Node_state_local_venv_dir_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{_Node_state_venv_driver_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{_Factory_state_reset_triggered.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{_Node_state_local_cache_dir_abs_path_inited.__name__}.create_state_node")
@patch("protoprimer.primer_kernel._Node_state_required_python_version_inited.create_state_node")
@patch(f"{primer_kernel.__name__}.{_Node_state_selected_python_file_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{_Factory_state_input_exec_operation_loaded.__name__}.create_state_node")
def test_uv_driver_inited_when_not_installed(
    mock_input_exec_operation_loaded,
    mock_state_selected_python_file_abs_path_inited,
    mock_state_required_python_version_inited,
    mock_state_local_cache_dir_abs_path_inited,
    mock_state_reset_triggered,
    mock_state_venv_driver_inited,
    mock_state_local_venv_dir_abs_path_inited,
    mock_pip_create_venv,
    mock_pip_install_packages,
    mock_os_path_exists,
    mock_os_path_isfile,
    env_ctx,
):
    # given:
    assert_parent_factories_mocked(
        env_ctx,
        _EnvState.state_venv_driver_prepared.name,
    )
    mock_state_venv_driver_inited.return_value.eval_own_state.return_value = VenvDriverType.venv_uv
    mock_state_selected_python_file_abs_path_inited.return_value.eval_own_state.return_value = "/usr/bin/python"
    mock_state_local_cache_dir_abs_path_inited.return_value.eval_own_state.return_value = "/cache"
    mock_state_reset_triggered.return_value.eval_own_state.return_value = False
    mock_os_path_exists.return_value = False
    mock_os_path_isfile.return_value = True
    mock_state_local_venv_dir_abs_path_inited.return_value.eval_own_state.return_value = "/venv"

    # when:
    state_value = env_ctx.eval_state(_EnvState.state_venv_driver_prepared.name)

    # then:
    assert isinstance(state_value, _VenvDriverUv)


@patch(f"{primer_kernel.__name__}.os.path.isfile")
@patch(f"{primer_kernel.__name__}.os.path.exists")
@patch(f"{primer_kernel.__name__}._VenvDriverPip.install_packages")
@patch(f"{primer_kernel.__name__}._VenvDriverPip.create_venv")
@patch(f"{primer_kernel.__name__}.{_Node_state_local_venv_dir_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{_Node_state_venv_driver_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{_Factory_state_reset_triggered.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{_Node_state_local_cache_dir_abs_path_inited.__name__}.create_state_node")
@patch("protoprimer.primer_kernel._Node_state_required_python_version_inited.create_state_node")
@patch(f"{primer_kernel.__name__}.{_Node_state_selected_python_file_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{_Factory_state_input_exec_operation_loaded.__name__}.create_state_node")
def test_uv_driver_inited_when_already_installed(
    mock_input_exec_operation_loaded,
    mock_state_selected_python_file_abs_path_inited,
    mock_state_required_python_version_inited,
    mock_state_local_cache_dir_abs_path_inited,
    mock_state_reset_triggered,
    mock_state_venv_driver_inited,
    mock_state_local_venv_dir_abs_path_inited,
    mock_pip_create_venv,
    mock_pip_install_packages,
    mock_os_path_exists,
    mock_os_path_isfile,
    env_ctx,
):
    # given:
    assert_parent_factories_mocked(
        env_ctx,
        _EnvState.state_venv_driver_prepared.name,
    )
    mock_state_venv_driver_inited.return_value.eval_own_state.return_value = VenvDriverType.venv_uv
    mock_state_selected_python_file_abs_path_inited.return_value.eval_own_state.return_value = "/usr/bin/python"
    mock_state_local_cache_dir_abs_path_inited.return_value.eval_own_state.return_value = "/cache"
    mock_state_reset_triggered.return_value.eval_own_state.return_value = False
    mock_os_path_exists.return_value = True
    mock_os_path_isfile.return_value = True
    mock_state_local_venv_dir_abs_path_inited.return_value.eval_own_state.return_value = "/venv"

    # when:
    state_value = env_ctx.eval_state(_EnvState.state_venv_driver_prepared.name)

    # then:
    assert isinstance(state_value, _VenvDriverUv)
    mock_pip_create_venv.assert_not_called()


@patch(f"{primer_kernel.__name__}.{_Node_state_local_venv_dir_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{_Node_state_venv_driver_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{_Factory_state_reset_triggered.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{_Node_state_local_cache_dir_abs_path_inited.__name__}.create_state_node")
@patch("protoprimer.primer_kernel._Node_state_required_python_version_inited.create_state_node")
@patch(f"{primer_kernel.__name__}.{_Node_state_selected_python_file_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{_Factory_state_input_exec_operation_loaded.__name__}.create_state_node")
def test_unsupported_driver(
    mock_input_exec_operation_loaded,
    mock_state_selected_python_file_abs_path_inited,
    mock_state_required_python_version_inited,
    mock_state_local_cache_dir_abs_path_inited,
    mock_state_reset_triggered,
    mock_state_venv_driver_inited,
    mock_state_local_venv_dir_abs_path_inited,
    env_ctx,
):
    # given:
    assert_parent_factories_mocked(
        env_ctx,
        _EnvState.state_venv_driver_prepared.name,
    )
    mock_driver = Mock()
    mock_driver.name = "unsupported_driver"
    mock_state_venv_driver_inited.return_value.eval_own_state.return_value = mock_driver
    mock_state_selected_python_file_abs_path_inited.return_value.eval_own_state.return_value = "/usr/bin/python"
    mock_state_local_cache_dir_abs_path_inited.return_value.eval_own_state.return_value = "/cache"
    mock_state_reset_triggered.return_value.eval_own_state.return_value = False

    # when/then:
    with pytest.raises(AssertionError, match="unsupported `VenvDriverType`"):
        env_ctx.eval_state(_EnvState.state_venv_driver_prepared.name)
