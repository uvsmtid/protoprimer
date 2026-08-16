import os
import subprocess
from unittest.mock import (
    ANY,
    mock_open,
    patch,
)

import pytest

from local_test.integrated_helper import test_python_version
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    ConfField,
    VenvDriverPip,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        VenvDriverPip.__name__,
    )


@patch(f"{primer_kernel.__name__}.os.path.exists")
@patch(f"{primer_kernel.__name__}.subprocess.check_output")
@patch(f"{primer_kernel.__name__}.subprocess.check_call")
def test_create_venv_when_constraints_file_does_not_exist(mock_check_call, mock_check_output, mock_exists):

    # given:

    venv_dir_abs_path = "/tmp/test_venv"
    python_path = "/tmp/python"
    constraints_file_abs_path = "/tmp/constraints.txt"
    mock_exists.return_value = False
    mock_check_output.return_value = b"pip==25.0\nsetuptools==75.0\nwheel==0.47.0\n"
    install_driver = VenvDriverPip(
        required_python_version=test_python_version,
        selected_python_file_abs_path=python_path,
        state_local_venv_dir_abs_path_inited=venv_dir_abs_path,
    )

    # when:

    install_driver.create_venv(venv_dir_abs_path, constraints_file_abs_path)

    # then:

    venv_python_abs_path = os.path.join(venv_dir_abs_path, "bin", "python")

    mock_check_output.assert_called_once_with(
        [
            venv_python_abs_path,
            "-m",
            "pip",
            "list",
            "--format=freeze",
            "--exclude-editable",
        ]
    )

    assert mock_check_call.call_count == 2
    mock_check_call.assert_any_call(
        [
            python_path,
            "-m",
            "venv",
            venv_dir_abs_path,
        ]
    )
    mock_check_call.assert_any_call(
        [
            venv_python_abs_path,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "pip",
            "setuptools",
            "wheel",
        ]
    )


@patch(f"{primer_kernel.__name__}.os.path.exists")
@patch(f"{primer_kernel.__name__}.subprocess.check_output")
@patch(f"{primer_kernel.__name__}.subprocess.check_call")
def test_create_venv_when_constraints_file_exists(mock_check_call, mock_check_output, mock_exists):

    # given:

    venv_dir_abs_path = "/tmp/test_venv"
    python_path = "/tmp/python"
    constraints_file_abs_path = "/tmp/constraints.txt"
    mock_exists.return_value = True
    mock_check_output.return_value = b"pip==25.0\nsetuptools==75.0\nwheel==0.47.0\n"
    install_driver = VenvDriverPip(
        required_python_version=test_python_version,
        selected_python_file_abs_path=python_path,
        state_local_venv_dir_abs_path_inited=venv_dir_abs_path,
    )

    # when:

    install_driver.create_venv(venv_dir_abs_path, constraints_file_abs_path)

    # then:

    venv_python_abs_path = os.path.join(venv_dir_abs_path, "bin", "python")

    mock_check_output.assert_called_once_with(
        [
            venv_python_abs_path,
            "-m",
            "pip",
            "list",
            "--format=freeze",
            "--exclude-editable",
        ]
    )

    assert mock_check_call.call_count == 2
    mock_check_call.assert_any_call(
        [
            python_path,
            "-m",
            "venv",
            venv_dir_abs_path,
        ]
    )
    mock_check_call.assert_any_call(
        [
            venv_python_abs_path,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "pip",
            "setuptools",
            "wheel",
            "--constraint",
            constraints_file_abs_path,
        ]
    )


@patch(f"{subprocess.__name__}.{subprocess.check_call.__name__}")
def test_install_dependencies(mock_subprocess_check_call):

    # given:

    ref_root_dir_abs_path = "/tmp"
    selected_python_file_abs_path = "/tmp/test_venv/bin/python"
    install_driver = VenvDriverPip(
        required_python_version=test_python_version,
        selected_python_file_abs_path=selected_python_file_abs_path,
        state_local_venv_dir_abs_path_inited="/tmp/venv",
    )
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
        venv_python_file_abs_path=selected_python_file_abs_path,
        constraints_file_abs_path=constraints_file_abs_path,
        project_descriptors=project_descriptors,
        extra_command_args=["--test-option"],
    )

    # then:

    mock_subprocess_check_call.assert_called_once_with(
        [
            selected_python_file_abs_path,
            "-m",
            "pip",
            "install",
            "--constraint",
            constraints_file_abs_path,
            "--test-option",
            "--editable",
            "/tmp/project1[extra1]",
            "--editable",
            "/tmp/project2",
        ],
        env=ANY,
    )


@patch(f"{subprocess.__name__}.{subprocess.check_call.__name__}")
def test_pin_versions(mock_subprocess_check_call):

    # given:

    venv_python_file_abs_path = "/tmp/test_venv/bin/python"
    install_driver = VenvDriverPip(
        required_python_version=test_python_version,
        selected_python_file_abs_path=venv_python_file_abs_path,
        state_local_venv_dir_abs_path_inited="/tmp/venv",
    )
    constraints_file_abs_path = "/tmp/constraints.txt"

    # when:

    with patch("builtins.open", mock_open()) as mock_file:
        install_driver.pin_versions(
            venv_python_file_abs_path=venv_python_file_abs_path,
            constraints_file_abs_path=constraints_file_abs_path,
        )

    # then:

    mock_subprocess_check_call.assert_called_once_with(
        [
            venv_python_file_abs_path,
            "-m",
            "pip",
            "freeze",
            "--exclude-editable",
            "--all",
        ],
        stdout=mock_file(),
    )


@patch("protoprimer.primer_kernel.get_venv_type")
def test_is_mine_venv_when_pip_venv(mock_get_venv_type):

    # given:

    venv_path = "/fake/venv"

    install_driver = VenvDriverPip(
        required_python_version=test_python_version,
        selected_python_file_abs_path="/tmp/python",
        state_local_venv_dir_abs_path_inited=venv_path,
    )

    mock_get_venv_type.return_value = primer_kernel.VenvDriverType.venv_pip

    # when:

    result = install_driver.is_mine_venv(venv_path)

    # then:

    mock_get_venv_type.assert_called_once_with(venv_path)
    assert result is True


@patch("protoprimer.primer_kernel.get_venv_type")
def test_is_mine_venv_when_uv_venv(mock_get_venv_type):

    # given:

    install_driver = VenvDriverPip(
        required_python_version=test_python_version,
        selected_python_file_abs_path="/tmp/python",
        state_local_venv_dir_abs_path_inited="/tmp/venv",
    )

    venv_path = "/fake/venv"
    mock_get_venv_type.return_value = primer_kernel.VenvDriverType.venv_uv

    # when:

    result = install_driver.is_mine_venv(venv_path)

    # then:

    mock_get_venv_type.assert_called_once_with(venv_path)
    assert result is False


@patch("os.path.exists")
def test_is_mine_venv_when_cfg_not_exists(mock_exists):

    # given:

    install_driver = VenvDriverPip(
        required_python_version=test_python_version,
        selected_python_file_abs_path="/tmp/python",
        state_local_venv_dir_abs_path_inited="/tmp/venv",
    )

    venv_path = "/fake/venv"
    cfg_path = os.path.join(venv_path, "pyvenv.cfg")
    mock_exists.return_value = False

    # when/then:

    with pytest.raises(AssertionError):
        install_driver.is_mine_venv(venv_path)
    mock_exists.assert_called_once_with(cfg_path)
