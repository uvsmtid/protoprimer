import os
import subprocess
import venv
from unittest.mock import (
    patch,
)

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    ConfField,
    PackageDriverPip,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        PackageDriverPip.__name__,
    )


@patch(f"{primer_kernel.__name__}.{venv.__name__}")
@patch(f"{primer_kernel.__name__}.subprocess.check_call")
def test_create_venv(mock_check_call, mock_venv):
    # given:
    install_driver = PackageDriverPip()
    venv_dir_abs_path = "/tmp/test_venv"

    # when:
    install_driver.create_venv("/tmp/python", venv_dir_abs_path)

    # then:
    mock_venv.create.assert_called_once_with(
        venv_dir_abs_path,
        with_pip=True,
    )
    # Assert that subprocess.check_call was called with the correct arguments
    mock_check_call.assert_called_once_with(
        [
            os.path.join(venv_dir_abs_path, "bin", "python"),
            "-m",
            "pip",
            "install",
            "--upgrade",
            "pip",
        ]
    )


@patch(f"{subprocess.__name__}.{subprocess.check_call.__name__}")
def test_install_dependencies(mock_subprocess_check_call):
    # given:
    install_driver = PackageDriverPip()
    ref_root_dir_abs_path = "/tmp"
    required_python_file_abs_path = "/tmp/test_venv/bin/python"
    constraints_file_abs_path = "/tmp/constraints.txt"
    project_descriptors = [
        {
            ConfField.field_build_root_dir_rel_path.value: "project1",
            ConfField.field_install_extras.value: ["extra1"],
        },
        {
            ConfField.field_build_root_dir_rel_path.value: "project2",
            ConfField.field_install_extras.value: [],
        },
    ]

    # when:
    install_driver.install_dependencies(
        ref_root_dir_abs_path=ref_root_dir_abs_path,
        required_python_file_abs_path=required_python_file_abs_path,
        constraints_file_abs_path=constraints_file_abs_path,
        project_descriptors=project_descriptors,
    )

    # then:
    mock_subprocess_check_call.assert_called_once_with(
        [
            required_python_file_abs_path,
            "-m",
            "pip",
            "install",
            "--constraint",
            constraints_file_abs_path,
            "--editable",
            "/tmp/project1[extra1]",
            "--editable",
            "/tmp/project2",
        ]
    )


@patch("protoprimer.primer_kernel.get_venv_type")
def test_is_mine_venv_when_pip_venv(mock_get_venv_type):
    # given
    driver = PackageDriverPip()
    venv_path = "/fake/venv"
    mock_get_venv_type.return_value = primer_kernel.PackageDriverType.driver_pip

    # when
    result = driver.is_mine_venv(venv_path)

    # then
    mock_get_venv_type.assert_called_once_with(venv_path)
    assert result is True


@patch("protoprimer.primer_kernel.get_venv_type")
def test_is_mine_venv_when_uv_venv(mock_get_venv_type):
    # given
    driver = PackageDriverPip()
    venv_path = "/fake/venv"
    mock_get_venv_type.return_value = primer_kernel.PackageDriverType.driver_uv

    # when
    result = driver.is_mine_venv(venv_path)

    # then
    mock_get_venv_type.assert_called_once_with(venv_path)
    assert result is False


@patch("os.path.exists")
def test_is_mine_venv_when_cfg_not_exists(mock_exists):
    # given
    driver = PackageDriverPip()
    venv_path = "/fake/venv"
    cfg_path = os.path.join(venv_path, "pyvenv.cfg")
    mock_exists.return_value = False

    # when/then
    with pytest.raises(AssertionError):
        driver.is_mine_venv(venv_path)
    mock_exists.assert_called_once_with(cfg_path)
