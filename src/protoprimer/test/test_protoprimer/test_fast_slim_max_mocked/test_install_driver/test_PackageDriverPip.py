import subprocess
import venv
from unittest.mock import patch

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
def test_create_venv(mock_venv):
    # given:
    install_driver = PackageDriverPip()
    venv_dir_abs_path = "/tmp/test_venv"

    # when:
    install_driver.create_venv("/tmp/python", venv_dir_abs_path)

    # then:
    mock_venv.create.assert_called_once_with(
        venv_dir_abs_path,
        with_pip=True,
        upgrade_deps=True,
    )


@patch(f"{subprocess.__name__}.{subprocess.check_call.__name__}")
def test_install_dependencies(mock_subprocess_check_call):
    # given:
    install_driver = PackageDriverPip()
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
            file_abs_path_local_python,
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
