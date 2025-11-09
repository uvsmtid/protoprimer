import os
import subprocess

import pytest
from unittest.mock import patch, mock_open

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import PackageDriverBase, ConfField


def test_relationship():
    assert_test_module_name_embeds_str(
        PackageDriverBase.__name__,
    )


class PackageDriverConcrete(PackageDriverBase):
    def _create_venv_impl(
        self, local_python_file_abs_path: str, local_venv_dir_abs_path: str
    ) -> None:
        pass

    def get_install_dependencies_cmd(
        self, local_python_file_abs_path: str
    ) -> list[str]:
        return []

    def _get_pin_versions_cmd(self, local_python_file_abs_path: str) -> list[str]:
        return []


def test_package_driver_base_is_instantiable():
    # given:
    # when:
    driver = PackageDriverConcrete()
    # then:
    assert isinstance(driver, PackageDriverBase)


@patch.object(PackageDriverConcrete, "_create_venv_impl")
def test_package_driver_base_create_venv(mock_create_venv_impl):
    # given:
    driver = PackageDriverConcrete()

    # when:
    driver.create_venv("python_path", "venv_path")

    # then:
    mock_create_venv_impl.assert_called_once_with("python_path", "venv_path")


@patch.object(PackageDriverConcrete, "get_install_dependencies_cmd")
@patch(f"{subprocess.__name__}.check_call")
def test_package_driver_base_install_dependencies(mock_check_call, mock_get_cmd_base):
    # given:
    driver = PackageDriverConcrete()
    mock_get_cmd_base.return_value = ["base", "command"]

    # when:
    driver.install_dependencies(
        ref_root_dir_abs_path="/ref",
        local_python_file_abs_path="python_path",
        constraints_file_abs_path="constraints_path",
        project_descriptors=[
            {
                ConfField.field_env_build_root_dir_rel_path.value: "proj1",
                ConfField.field_env_install_extras.value: ["extra1"],
            }
        ],
    )

    # then:
    mock_get_cmd_base.assert_called_once_with("python_path")
    mock_check_call.assert_called_once_with(
        [
            "base",
            "command",
            "--constraint",
            "constraints_path",
            "--editable",
            "/ref/proj1[extra1]",
        ]
    )


@patch("builtins.open", new_callable=mock_open)
@patch.object(PackageDriverConcrete, "_get_pin_versions_cmd")
@patch(f"{subprocess.__name__}.check_call")
def test_package_driver_base_pin_versions(mock_check_call, mock_get_cmd, mock_file):
    # given:
    driver = PackageDriverConcrete()
    mock_get_cmd.return_value = ["freeze", "command"]

    # when:
    driver.pin_versions("python_path", "constraints_path")

    # then:
    mock_get_cmd.assert_called_once_with("python_path")
    mock_check_call.assert_called_once_with(["freeze", "command"], stdout=mock_file())


def test_package_driver_base_create_venv_impl_raises_not_implemented_error():
    # given:
    # when/then:
    with pytest.raises(NotImplementedError):
        PackageDriverBase._create_venv_impl(None, "python_path", "venv_path")


@patch.object(PackageDriverConcrete, "get_install_dependencies_cmd")
@patch(f"{subprocess.__name__}.check_call")
def test_package_driver_base_install_dependencies_no_extras(
    mock_check_call, mock_get_cmd_base
):
    # given:
    driver = PackageDriverConcrete()
    mock_get_cmd_base.return_value = ["base", "command"]

    # when:
    driver.install_dependencies(
        ref_root_dir_abs_path="/ref",
        local_python_file_abs_path="python_path",
        constraints_file_abs_path="constraints_path",
        project_descriptors=[
            {
                ConfField.field_env_build_root_dir_rel_path.value: "proj1",
            }
        ],
    )

    # then:
    mock_get_cmd_base.assert_called_once_with("python_path")
    mock_check_call.assert_called_once_with(
        [
            "base",
            "command",
            "--constraint",
            "constraints_path",
            "--editable",
            "/ref/proj1",
        ]
    )


def test_package_driver_base_get_install_dependencies_cmd_raises_not_implemented_error():
    # given:
    # when/then:
    with pytest.raises(NotImplementedError):
        PackageDriverBase.get_install_dependencies_cmd(None, "python_path")


def test_package_driver_base_get_pin_versions_cmd_raises_not_implemented_error():
    # given:
    # when/then:
    with pytest.raises(NotImplementedError):
        PackageDriverBase._get_pin_versions_cmd(None, "python_path")


@patch.object(PackageDriverConcrete, "get_install_dependencies_cmd")
@patch(f"{subprocess.__name__}.check_call")
def test_package_driver_base_install_packages(mock_check_call, mock_get_cmd_base):
    # given:
    driver = PackageDriverConcrete()
    mock_get_cmd_base.return_value = ["base", "command"]
    packages_to_install = ["package1", "package2"]

    # when:
    driver.install_packages(
        local_python_file_abs_path="python_path",
        given_packages=packages_to_install,
    )

    # then:
    mock_get_cmd_base.assert_called_once_with("python_path")
    mock_check_call.assert_called_once_with(
        [
            "base",
            "command",
            "package1",
            "package2",
        ]
    )


def test_package_driver_base_get_type_raises_not_implemented_error():
    # given:
    # when/then:
    with pytest.raises(NotImplementedError):
        PackageDriverBase.get_type(None)
