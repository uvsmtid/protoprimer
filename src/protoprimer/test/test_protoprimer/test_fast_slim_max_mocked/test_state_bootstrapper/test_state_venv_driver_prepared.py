from unittest.mock import (
    Mock,
    patch,
)

import pytest

from local_test.mock_verifier import (
    assert_parent_states_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_local_cache_dir_abs_path_inited,
    Bootstrapper_state_venv_driver_inited,
    Bootstrapper_state_reinstall_triggered,
    Bootstrapper_state_selected_python_file_abs_path_inited,
    EnvContext,
    EnvState,
    VenvDriverPip,
    VenvDriverType,
    VenvDriverUv,
)


@pytest.fixture
def env_ctx():
    return EnvContext()


def test_relationship():
    assert_test_module_name_embeds_str(EnvState.state_venv_driver_prepared.name)


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_venv_driver_inited.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_reinstall_triggered.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_local_cache_dir_abs_path_inited.__name__}.eval_own_state"
)
@patch(
    "protoprimer.primer_kernel.Bootstrapper_required_python_version_inited.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_selected_python_file_abs_path_inited.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_run_mode_arg_loaded.__name__}.eval_own_state"
)
def test_pip_driver_inited(
    mock_input_run_mode_arg_loaded,
    mock_state_selected_python_file_abs_path_inited,
    mock_state_required_python_version_inited,
    mock_state_local_cache_dir_abs_path_inited,
    mock_state_reinstall_triggered,
    mock_state_venv_driver_inited,
    env_ctx,
):
    # given:
    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_venv_driver_prepared.name,
    )
    mock_state_venv_driver_inited.return_value = VenvDriverType.venv_pip
    mock_state_selected_python_file_abs_path_inited.return_value = "/usr/bin/python"
    mock_state_local_cache_dir_abs_path_inited.return_value = "/cache"
    mock_state_reinstall_triggered.return_value = False

    # when:
    state_value = env_ctx.state_graph.eval_state(
        EnvState.state_venv_driver_prepared.name
    )

    # then:
    assert isinstance(state_value, VenvDriverPip)


@patch(f"{primer_kernel.__name__}.os.path.isfile")
@patch(f"{primer_kernel.__name__}.os.path.exists")
@patch(f"{primer_kernel.__name__}.VenvDriverPip.install_packages")
@patch(f"{primer_kernel.__name__}.VenvDriverPip.create_venv")
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_venv_driver_inited.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_reinstall_triggered.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_local_cache_dir_abs_path_inited.__name__}.eval_own_state"
)
@patch(
    "protoprimer.primer_kernel.Bootstrapper_required_python_version_inited.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_selected_python_file_abs_path_inited.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_run_mode_arg_loaded.__name__}.eval_own_state"
)
def test_uv_driver_inited_when_not_installed(
    mock_input_run_mode_arg_loaded,
    mock_state_selected_python_file_abs_path_inited,
    mock_state_required_python_version_inited,
    mock_state_local_cache_dir_abs_path_inited,
    mock_state_reinstall_triggered,
    mock_state_venv_driver_inited,
    mock_pip_create_venv,
    mock_pip_install_packages,
    mock_os_path_exists,
    mock_os_path_isfile,
    env_ctx,
):
    # given:
    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_venv_driver_prepared.name,
    )
    mock_state_venv_driver_inited.return_value = VenvDriverType.venv_uv
    mock_state_selected_python_file_abs_path_inited.return_value = "/usr/bin/python"
    mock_state_local_cache_dir_abs_path_inited.return_value = "/cache"
    mock_state_reinstall_triggered.return_value = False
    mock_os_path_exists.return_value = False
    mock_os_path_isfile.return_value = True

    # when:
    state_value = env_ctx.state_graph.eval_state(
        EnvState.state_venv_driver_prepared.name
    )

    # then:
    assert isinstance(state_value, VenvDriverUv)


@patch(f"{primer_kernel.__name__}.os.path.isfile")
@patch(f"{primer_kernel.__name__}.os.path.exists")
@patch(f"{primer_kernel.__name__}.VenvDriverPip.install_packages")
@patch(f"{primer_kernel.__name__}.VenvDriverPip.create_venv")
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_venv_driver_inited.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_reinstall_triggered.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_local_cache_dir_abs_path_inited.__name__}.eval_own_state"
)
@patch(
    "protoprimer.primer_kernel.Bootstrapper_required_python_version_inited.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_selected_python_file_abs_path_inited.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_run_mode_arg_loaded.__name__}.eval_own_state"
)
def test_uv_driver_inited_when_already_installed(
    mock_input_run_mode_arg_loaded,
    mock_state_selected_python_file_abs_path_inited,
    mock_state_required_python_version_inited,
    mock_state_local_cache_dir_abs_path_inited,
    mock_state_reinstall_triggered,
    mock_state_venv_driver_inited,
    mock_pip_create_venv,
    mock_pip_install_packages,
    mock_os_path_exists,
    mock_os_path_isfile,
    env_ctx,
):
    # given:
    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_venv_driver_prepared.name,
    )
    mock_state_venv_driver_inited.return_value = VenvDriverType.venv_uv
    mock_state_selected_python_file_abs_path_inited.return_value = "/usr/bin/python"
    mock_state_local_cache_dir_abs_path_inited.return_value = "/cache"
    mock_state_reinstall_triggered.return_value = False
    mock_os_path_exists.return_value = True
    mock_os_path_isfile.return_value = True

    # when:
    state_value = env_ctx.state_graph.eval_state(
        EnvState.state_venv_driver_prepared.name
    )

    # then:
    assert isinstance(state_value, VenvDriverUv)
    mock_pip_create_venv.assert_not_called()


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_venv_driver_inited.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_reinstall_triggered.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_local_cache_dir_abs_path_inited.__name__}.eval_own_state"
)
@patch(
    "protoprimer.primer_kernel.Bootstrapper_required_python_version_inited.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_selected_python_file_abs_path_inited.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_run_mode_arg_loaded.__name__}.eval_own_state"
)
def test_unsupported_driver(
    mock_input_run_mode_arg_loaded,
    mock_state_selected_python_file_abs_path_inited,
    mock_state_required_python_version_inited,
    mock_state_local_cache_dir_abs_path_inited,
    mock_state_reinstall_triggered,
    mock_state_venv_driver_inited,
    env_ctx,
):
    # given:
    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_venv_driver_prepared.name,
    )
    mock_driver = Mock()
    mock_driver.name = "unsupported_driver"
    mock_state_venv_driver_inited.return_value = mock_driver
    mock_state_selected_python_file_abs_path_inited.return_value = "/usr/bin/python"
    mock_state_local_cache_dir_abs_path_inited.return_value = "/cache"
    mock_state_reinstall_triggered.return_value = False

    # when/then:
    with pytest.raises(AssertionError, match="unsupported `VenvDriverType`"):
        env_ctx.state_graph.eval_state(EnvState.state_venv_driver_prepared.name)
