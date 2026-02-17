import os
import subprocess
from unittest.mock import (
    call,
    mock_open,
    patch,
)

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    ConfField,
    VenvDriverUv,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        VenvDriverUv.__name__,
    )


@patch(f"{primer_kernel.__name__}.os.path.isfile")
@patch(f"{primer_kernel.__name__}.os.path.exists")
@patch(f"{subprocess.__name__}.{subprocess.check_call.__name__}")
def test_create_venv(mock_subprocess_check_call, mock_exists, mock_isfile):
    # given:
    mock_exists.return_value = True
    mock_isfile.return_value = True
    install_driver = VenvDriverUv(
        required_python_version="3.10",
        state_local_cache_dir_abs_path_inited="/tmp/cache",
    )
    venv_dir_abs_path = "/tmp/test_venv"

    # when:
    install_driver.create_venv(
        local_venv_dir_abs_path=venv_dir_abs_path,
    )

    # then:
    expected_calls = [
        call(
            [
                "/tmp/cache/venv/uv.venv/bin/uv",
                "python",
                "dir",
            ]
        ),
        call(
            [
                "/tmp/cache/venv/uv.venv/bin/uv",
                "python",
                "install",
                "3.10",
            ]
        ),
        call(
            [
                "/tmp/cache/venv/uv.venv/bin/uv",
                "venv",
                "--python",
                "3.10",
                venv_dir_abs_path,
            ]
        ),
    ]
    mock_subprocess_check_call.assert_has_calls(expected_calls)
    assert mock_subprocess_check_call.call_count == 3


@patch(f"{primer_kernel.__name__}.os.path.isfile")
@patch(f"{primer_kernel.__name__}.os.path.exists")
@patch(f"{subprocess.__name__}.{subprocess.check_call.__name__}")
def test_install_dependencies(mock_subprocess_check_call, mock_exists, mock_isfile):
    # given:
    mock_exists.return_value = True
    mock_isfile.return_value = True
    install_driver = VenvDriverUv(
        required_python_version="3.10",
        state_local_cache_dir_abs_path_inited="/tmp/cache",
    )
    ref_root_dir_abs_path = "/tmp"
    selected_python_file_abs_path = "/tmp/test_venv/bin/python"
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
        selected_python_file_abs_path=selected_python_file_abs_path,
        constraints_file_abs_path=constraints_file_abs_path,
        project_descriptors=project_descriptors,
    )

    # then:
    expected_calls = [
        call(
            [
                "/tmp/cache/venv/uv.venv/bin/uv",
                "python",
                "dir",
            ]
        ),
        call(
            [
                "/tmp/cache/venv/uv.venv/bin/uv",
                "pip",
                "install",
                "--python",
                selected_python_file_abs_path,
                "--constraint",
                constraints_file_abs_path,
                "--editable",
                "/tmp/project1[extra1]",
                "--editable",
                "/tmp/project2",
            ]
        ),
    ]
    mock_subprocess_check_call.assert_has_calls(expected_calls)
    assert mock_subprocess_check_call.call_count == 2


@patch(f"{primer_kernel.__name__}.os.path.isfile")
@patch(f"{primer_kernel.__name__}.os.path.exists")
@patch(f"{subprocess.__name__}.{subprocess.check_call.__name__}")
def test_pin_versions(mock_subprocess_check_call, mock_exists, mock_isfile):
    # given:
    mock_exists.return_value = True
    mock_isfile.return_value = True
    install_driver = VenvDriverUv(
        required_python_version="3.10",
        state_local_cache_dir_abs_path_inited="/tmp/cache",
    )
    selected_python_file_abs_path = "/tmp/test_venv/bin/python"
    constraints_file_abs_path = "/tmp/constraints.txt"

    # when:
    with patch("builtins.open", mock_open()) as mock_file:
        install_driver.pin_versions(
            selected_python_file_abs_path=selected_python_file_abs_path,
            constraints_file_abs_path=constraints_file_abs_path,
        )

    # then:
    expected_calls = [
        call(
            [
                "/tmp/cache/venv/uv.venv/bin/uv",
                "python",
                "dir",
            ]
        ),
        call(
            [
                "/tmp/cache/venv/uv.venv/bin/uv",
                "pip",
                "freeze",
                "--exclude-editable",
                "--python",
                selected_python_file_abs_path,
            ],
            stdout=mock_file(),
        ),
    ]
    mock_subprocess_check_call.assert_has_calls(expected_calls)
    assert mock_subprocess_check_call.call_count == 2


@patch("protoprimer.primer_kernel.get_venv_type")
def test_is_mine_venv_when_uv_venv(mock_get_venv_type):
    # given
    driver = VenvDriverUv(
        required_python_version="3.10",
        state_local_cache_dir_abs_path_inited="/tmp/cache",
    )
    venv_path = "/fake/venv"
    mock_get_venv_type.return_value = primer_kernel.VenvDriverType.venv_uv

    # when
    result = driver.is_mine_venv(venv_path)

    # then
    mock_get_venv_type.assert_called_once_with(venv_path)
    assert result is True


@patch("protoprimer.primer_kernel.get_venv_type")
def test_is_mine_venv_when_pip_venv(mock_get_venv_type):
    # given
    driver = VenvDriverUv(
        required_python_version="3.10",
        state_local_cache_dir_abs_path_inited="/tmp/cache",
    )
    venv_path = "/fake/venv"
    mock_get_venv_type.return_value = primer_kernel.VenvDriverType.venv_pip

    # when
    result = driver.is_mine_venv(venv_path)

    # then
    mock_get_venv_type.assert_called_once_with(venv_path)
    assert result is False


@patch("protoprimer.primer_kernel.get_venv_type")
def test_is_mine_venv_when_cfg_not_exists(mock_get_venv_type):
    # given
    driver = VenvDriverUv(
        required_python_version="3.10",
        state_local_cache_dir_abs_path_inited="/tmp/cache",
    )
    venv_path = "/fake/venv"
    mock_get_venv_type.side_effect = AssertionError("File not found")

    # when/then
    with pytest.raises(AssertionError):
        driver.is_mine_venv(venv_path)
    mock_get_venv_type.assert_called_once_with(venv_path)
