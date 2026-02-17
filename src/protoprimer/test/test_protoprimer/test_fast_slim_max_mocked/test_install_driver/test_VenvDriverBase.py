import subprocess
from typing import List
from unittest.mock import (
    mock_open,
    patch,
)

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    ConfField,
    VenvDriverBase,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        VenvDriverBase.__name__,
    )


class VenvDriverConcrete(VenvDriverBase):
    def _create_venv_impl(self, local_venv_dir_abs_path: str) -> None:
        pass

    def get_install_dependencies_cmd(
        self, selected_python_file_abs_path: str
    ) -> List[str]:
        return []

    def _get_pin_versions_cmd(self, selected_python_file_abs_path: str) -> List[str]:
        return []


def test_venv_driver_base_is_instantiable():
    # given:
    # when:
    driver = VenvDriverConcrete()
    # then:
    assert isinstance(driver, VenvDriverBase)


@patch.object(VenvDriverConcrete, "_create_venv_impl")
def test_venv_driver_base_create_venv(mock_create_venv_impl):
    # given:
    driver = VenvDriverConcrete()

    # when:
    driver.create_venv("venv_path")

    # then:
    mock_create_venv_impl.assert_called_once_with("venv_path")


@patch.object(VenvDriverConcrete, "get_install_dependencies_cmd")
@patch(f"{subprocess.__name__}.check_call")
def test_venv_driver_base_install_dependencies(mock_check_call, mock_get_cmd_base):
    # given:
    driver = VenvDriverConcrete()
    mock_get_cmd_base.return_value = ["base", "command"]

    # when:
    driver.install_dependencies(
        ref_root_dir_abs_path="/ref",
        selected_python_file_abs_path="python_path",
        constraints_file_abs_path="constraints_path",
        project_descriptors=[
            {
                ConfField.field_build_root_dir_rel_path.value: "proj1",
                ConfField.field_install_extras.value: ["extra1"],
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
@patch.object(VenvDriverConcrete, "_get_pin_versions_cmd")
@patch(f"{subprocess.__name__}.check_call")
def test_venv_driver_base_pin_versions(mock_check_call, mock_get_cmd, mock_file):
    # given:
    driver = VenvDriverConcrete()
    mock_get_cmd.return_value = ["freeze", "command"]

    # when:
    driver.pin_versions("python_path", "constraints_path")

    # then:
    mock_get_cmd.assert_called_once_with("python_path")
    mock_check_call.assert_called_once_with(["freeze", "command"], stdout=mock_file())


def test_venv_driver_base_create_venv_impl_raises_not_implemented_error():
    # given:
    # when/then:
    with pytest.raises(NotImplementedError):
        VenvDriverBase._create_venv_impl(None, "venv_path")


@patch.object(VenvDriverConcrete, "get_install_dependencies_cmd")
@patch(f"{subprocess.__name__}.check_call")
def test_venv_driver_base_install_dependencies_no_extras(
    mock_check_call, mock_get_cmd_base
):
    # given:
    driver = VenvDriverConcrete()
    mock_get_cmd_base.return_value = ["base", "command"]

    # when:
    driver.install_dependencies(
        ref_root_dir_abs_path="/ref",
        selected_python_file_abs_path="python_path",
        constraints_file_abs_path="constraints_path",
        project_descriptors=[
            {
                ConfField.field_build_root_dir_rel_path.value: "proj1",
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


def test_venv_driver_base_get_install_dependencies_cmd_raises_not_implemented_error():
    # given:
    # when/then:
    with pytest.raises(NotImplementedError):
        VenvDriverBase.get_install_dependencies_cmd(None, "python_path")


def test_venv_driver_base_get_pin_versions_cmd_raises_not_implemented_error():
    # given:
    # when/then:
    with pytest.raises(NotImplementedError):
        VenvDriverBase._get_pin_versions_cmd(None, "python_path")


@patch.object(VenvDriverConcrete, "get_install_dependencies_cmd")
@patch(f"{subprocess.__name__}.check_call")
def test_venv_driver_base_install_packages(mock_check_call, mock_get_cmd_base):
    # given:
    driver = VenvDriverConcrete()
    mock_get_cmd_base.return_value = ["base", "command"]
    packages_to_install = ["package1", "package2"]

    # when:
    driver.install_packages(
        selected_python_file_abs_path="python_path",
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


def test_venv_driver_base_get_type_raises_not_implemented_error():
    # given:
    # when/then:
    with pytest.raises(NotImplementedError):
        VenvDriverBase.get_type(None)
