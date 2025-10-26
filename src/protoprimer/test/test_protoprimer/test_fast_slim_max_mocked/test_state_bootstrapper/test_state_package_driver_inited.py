import os
from unittest.mock import (
    patch,
    Mock,
)

import pytest

from local_test.mock_verifier import (
    assert_parent_states_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_env_local_python_file_abs_path_eval_finalized,
    Bootstrapper_state_env_local_cache_dir_abs_path_eval_finalized,
    Bootstrapper_state_reinstall_triggered,
    Bootstrapper_state_package_driver_selected,
    EnvContext,
    EnvState,
    PackageDriverType,
    PackageDriverPip,
    PackageDriverUv,
)


@pytest.fixture
def env_ctx():
    return EnvContext()


def test_relationship():
    assert_test_module_name_embeds_str(EnvState.state_package_driver_inited.name)


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_package_driver_selected.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_reinstall_triggered.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_env_local_cache_dir_abs_path_eval_finalized.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_env_local_python_file_abs_path_eval_finalized.__name__}.eval_own_state"
)
def test_pip_driver_inited(
    mock_state_env_local_python_file_abs_path_eval_finalized,
    mock_state_env_local_cache_dir_abs_path_eval_finalized,
    mock_state_reinstall_triggered,
    mock_state_package_driver_selected,
    env_ctx,
):
    # given:
    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_package_driver_inited.name,
    )
    mock_state_package_driver_selected.return_value = PackageDriverType.driver_pip
    mock_state_env_local_python_file_abs_path_eval_finalized.return_value = (
        "/usr/bin/python"
    )
    mock_state_env_local_cache_dir_abs_path_eval_finalized.return_value = "/cache"
    mock_state_reinstall_triggered.return_value = False

    # when:
    state_value = env_ctx.state_graph.eval_state(
        EnvState.state_package_driver_inited.name
    )

    # then:
    assert isinstance(state_value, PackageDriverPip)


@patch(f"{primer_kernel.__name__}.os.path.isfile")
@patch(f"{primer_kernel.__name__}.os.path.exists")
@patch(f"{primer_kernel.__name__}.PackageDriverPip.install_packages")
@patch(f"{primer_kernel.__name__}.PackageDriverPip.create_venv")
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_package_driver_selected.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_reinstall_triggered.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_env_local_cache_dir_abs_path_eval_finalized.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_env_local_python_file_abs_path_eval_finalized.__name__}.eval_own_state"
)
def test_uv_driver_inited_when_not_installed(
    mock_state_env_local_python_file_abs_path_eval_finalized,
    mock_state_env_local_cache_dir_abs_path_eval_finalized,
    mock_state_reinstall_triggered,
    mock_state_package_driver_selected,
    mock_pip_create_venv,
    mock_pip_install_packages,
    mock_os_path_exists,
    mock_os_path_isfile,
    env_ctx,
):
    # given:
    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_package_driver_inited.name,
    )
    mock_state_package_driver_selected.return_value = PackageDriverType.driver_uv
    mock_state_env_local_python_file_abs_path_eval_finalized.return_value = (
        "/usr/bin/python"
    )
    mock_state_env_local_cache_dir_abs_path_eval_finalized.return_value = "/cache"
    mock_state_reinstall_triggered.return_value = False
    mock_os_path_exists.return_value = False
    mock_os_path_isfile.return_value = True

    # when:
    state_value = env_ctx.state_graph.eval_state(
        EnvState.state_package_driver_inited.name
    )

    # then:
    assert isinstance(state_value, PackageDriverUv)
    mock_pip_create_venv.assert_called_once_with(
        "/usr/bin/python",
        "/cache/venv/uv.venv",
    )
    mock_pip_install_packages.assert_called_once_with(
        "/cache/venv/uv.venv/bin/python",
        ["uv"],
    )
    mock_os_path_exists.assert_called_once_with("/cache/venv/uv.venv/bin/uv")
    mock_os_path_isfile.assert_called_once_with("/cache/venv/uv.venv/bin/uv")


@patch(f"{primer_kernel.__name__}.os.path.isfile")
@patch(f"{primer_kernel.__name__}.os.path.exists")
@patch(f"{primer_kernel.__name__}.PackageDriverPip.install_packages")
@patch(f"{primer_kernel.__name__}.PackageDriverPip.create_venv")
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_package_driver_selected.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_reinstall_triggered.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_env_local_cache_dir_abs_path_eval_finalized.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_env_local_python_file_abs_path_eval_finalized.__name__}.eval_own_state"
)
def test_uv_driver_inited_when_already_installed(
    mock_state_env_local_python_file_abs_path_eval_finalized,
    mock_state_env_local_cache_dir_abs_path_eval_finalized,
    mock_state_reinstall_triggered,
    mock_state_package_driver_selected,
    mock_pip_create_venv,
    mock_pip_install_packages,
    mock_os_path_exists,
    mock_os_path_isfile,
    env_ctx,
):
    # given:
    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_package_driver_inited.name,
    )
    mock_state_package_driver_selected.return_value = PackageDriverType.driver_uv
    mock_state_env_local_python_file_abs_path_eval_finalized.return_value = (
        "/usr/bin/python"
    )
    mock_state_env_local_cache_dir_abs_path_eval_finalized.return_value = "/cache"
    mock_state_reinstall_triggered.return_value = False
    mock_os_path_exists.return_value = True
    mock_os_path_isfile.return_value = True

    # when:
    state_value = env_ctx.state_graph.eval_state(
        EnvState.state_package_driver_inited.name
    )

    # then:
    assert isinstance(state_value, PackageDriverUv)
    mock_pip_create_venv.assert_not_called()
    mock_os_path_exists.assert_called_once_with("/cache/venv/uv.venv/bin/uv")
    mock_os_path_isfile.assert_called_once_with("/cache/venv/uv.venv/bin/uv")


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_package_driver_selected.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_reinstall_triggered.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_env_local_cache_dir_abs_path_eval_finalized.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_env_local_python_file_abs_path_eval_finalized.__name__}.eval_own_state"
)
def test_unsupported_driver(
    mock_state_env_local_python_file_abs_path_eval_finalized,
    mock_state_env_local_cache_dir_abs_path_eval_finalized,
    mock_state_reinstall_triggered,
    mock_state_package_driver_selected,
    env_ctx,
):
    # given:
    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_package_driver_inited.name,
    )
    mock_driver = Mock()
    mock_driver.name = "unsupported_driver"
    mock_state_package_driver_selected.return_value = mock_driver
    mock_state_env_local_python_file_abs_path_eval_finalized.return_value = (
        "/usr/bin/python"
    )
    mock_state_env_local_cache_dir_abs_path_eval_finalized.return_value = "/cache"
    mock_state_reinstall_triggered.return_value = False

    # when/then:
    with pytest.raises(AssertionError, match="unsupported `PackageDriverType`"):
        env_ctx.state_graph.eval_state(EnvState.state_package_driver_inited.name)
