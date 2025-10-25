import subprocess
from unittest.mock import (
    patch,
    mock_open,
)

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    ConfField,
    PackageDriverUv,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        PackageDriverUv.__name__,
    )


@patch(f"{subprocess.__name__}.{subprocess.check_call.__name__}")
def test_create_venv(mock_subprocess_check_call):
    # given:
    install_driver = PackageDriverUv()
    file_abs_path_local_python = "/tmp/python"
    venv_dir_abs_path = "/tmp/test_venv"

    # when:
    install_driver.create_venv(
        file_abs_path_local_python=file_abs_path_local_python,
        dir_abs_path_local_venv=venv_dir_abs_path,
    )

    # then:
    mock_subprocess_check_call.assert_called_once_with(
        [
            "uv",
            "venv",
            "--python",
            file_abs_path_local_python,
            venv_dir_abs_path,
        ]
    )


@patch(f"{subprocess.__name__}.{subprocess.check_call.__name__}")
def test_install_dependencies(mock_subprocess_check_call):
    # given:
    install_driver = PackageDriverUv()
    ref_root_dir_abs_path = "/tmp"
    file_abs_path_local_python = "/tmp/test_venv/bin/python"
    constraints_file_abs_path = "/tmp/constraints.txt"
    project_descriptors = [
        {
            ConfField.field_env_build_root_dir_rel_path.value: "project1",
            ConfField.field_env_install_extras.value: ["extra1"],
        },
        {
            ConfField.field_env_build_root_dir_rel_path.value: "project2",
            ConfField.field_env_install_extras.value: [],
        },
    ]

    # when:
    install_driver.install_dependencies(
        ref_root_dir_abs_path=ref_root_dir_abs_path,
        file_abs_path_local_python=file_abs_path_local_python,
        constraints_file_abs_path=constraints_file_abs_path,
        project_descriptors=project_descriptors,
    )

    # then:
    mock_subprocess_check_call.assert_called_once_with(
        [
            "uv",
            "pip",
            "install",
            "--python",
            file_abs_path_local_python,
            "--constraint",
            constraints_file_abs_path,
            "--editable",
            "/tmp/project1[extra1]",
            "--editable",
            "/tmp/project2",
        ]
    )


@patch(f"{subprocess.__name__}.{subprocess.check_call.__name__}")
def test_pin_versions(mock_subprocess_check_call):
    # given:
    install_driver = PackageDriverUv()
    file_abs_path_local_python = "/tmp/test_venv/bin/python"
    constraints_file_abs_path = "/tmp/constraints.txt"

    # when:
    with patch("builtins.open", mock_open()) as mock_file:
        install_driver.pin_versions(
            file_abs_path_local_python=file_abs_path_local_python,
            constraints_file_abs_path=constraints_file_abs_path,
        )

    # then:
    mock_subprocess_check_call.assert_called_once_with(
        [
            "uv",
            "pip",
            "freeze",
            "--exclude-editable",
            "--python",
            file_abs_path_local_python,
        ],
        stdout=mock_file(),
    )
