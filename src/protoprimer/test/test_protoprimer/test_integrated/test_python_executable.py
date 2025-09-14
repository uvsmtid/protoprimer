import os
import pathlib
import subprocess
import sys
import venv

import protoprimer
from local_test.toml_handler import save_toml_data
from protoprimer.primer_kernel import (
    ArgConst,
    ConfConstClient,
    ConfConstEnv,
    ConfConstGeneral,
    ConfConstInput,
    ConfConstPrimer,
    ConfField,
    PythonExecutable,
    write_json_file,
)
from test_protoprimer.test_integrated.integrated_helper import (
    switch_to_test_dir_with_plain_proto_code,
)


def test_python_from_arbitrary_venv(
    tmp_path: pathlib.Path,
):
    """
    Run the `proto_kernel` from within an arbitrary virtual environment.

    The script should:
    *   detect this
    *   escape to the base python
    *   create the required venv
    *   run until it succeeds.
    """

    # given:

    # A directory with the `proto_kernel`:
    switch_to_test_dir_with_plain_proto_code(tmp_path)

    # Config to allow the script to run:
    prime_conf_data = {
        ConfField.field_primer_ref_root_dir_rel_path.value: ".",
        ConfField.field_primer_conf_client_file_rel_path.value: ConfConstPrimer.default_client_conf_file_rel_path,
    }
    write_json_file(
        str(tmp_path / ConfConstInput.default_file_basename_conf_primer),
        prime_conf_data,
    )

    client_conf_data = {
        ConfField.field_client_link_name_dir_rel_path.value: ConfConstClient.default_dir_rel_path_leap_env_link_name,
        ConfField.field_client_default_target_dir_rel_path.value: ConfConstClient.default_client_default_target_dir_rel_path,
    }
    os.makedirs(
        os.path.dirname(tmp_path / ConfConstPrimer.default_client_conf_file_rel_path)
    )
    write_json_file(
        str(tmp_path / ConfConstPrimer.default_client_conf_file_rel_path),
        client_conf_data,
    )

    # Project to install:
    protoprimer_project_dir = pathlib.Path(protoprimer.__file__).parent.parent.parent
    project_dir = tmp_path / "pyproject"
    os.mkdir(project_dir)
    toml_data = {
        "project": {
            "name": "whatever",
            "version": "0.0.0.dev0",
            "dependencies": [
                f"protoprimer @ file://{protoprimer_project_dir}",
            ],
        }
    }
    save_toml_data(
        str(project_dir / "pyproject.toml"),
        toml_data,
    )

    base_python = os.path.join(
        sys.base_prefix,
        ConfConstGeneral.file_rel_path_venv_python,
    )
    env_conf_data = {
        ConfField.field_env_local_python_file_abs_path.value: base_python,
        ConfField.field_env_local_venv_dir_rel_path.value: ConfConstEnv.default_dir_rel_path_venv,
        ConfField.field_env_project_descriptors.value: [
            {
                ConfField.field_env_build_root_dir_rel_path.value: str(project_dir),
                ConfField.field_env_install_extras.value: [],
            },
        ],
    }
    write_json_file(
        str(tmp_path / ConfConstClient.default_file_basename_leap_env),
        env_conf_data,
    )

    # An arbitrary venv to start from:
    arbitrary_venv_dir = tmp_path / "arbitrary_venv"
    venv.create(arbitrary_venv_dir, with_pip=True)
    arbitrary_venv_python = (
        arbitrary_venv_dir / ConfConstGeneral.file_rel_path_venv_python
    )

    command_args = [
        str(arbitrary_venv_python),
        "./primer_kernel.py",
    ]

    # when:
    # then:
    sub_proc = subprocess.run(
        command_args,
        capture_output=False,
        text=True,
        check=True,
    )


def test_python_from_required_venv(
    tmp_path: pathlib.Path,
):
    """
    Run the `proto_kernel` from within the required, but pre-existing virtual environment.
    """

    # given:

    switch_to_test_dir_with_plain_proto_code(tmp_path)

    # Config to allow the script to run:
    prime_conf_data = {
        ConfField.field_primer_ref_root_dir_rel_path.value: ".",
        ConfField.field_primer_conf_client_file_rel_path.value: ConfConstPrimer.default_client_conf_file_rel_path,
    }
    write_json_file(
        str(tmp_path / ConfConstInput.default_file_basename_conf_primer),
        prime_conf_data,
    )

    client_conf_data = {
        ConfField.field_client_link_name_dir_rel_path.value: ConfConstClient.default_dir_rel_path_leap_env_link_name,
        ConfField.field_client_default_target_dir_rel_path.value: ConfConstClient.default_client_default_target_dir_rel_path,
    }
    os.makedirs(
        os.path.dirname(tmp_path / ConfConstPrimer.default_client_conf_file_rel_path)
    )
    write_json_file(
        str(tmp_path / ConfConstPrimer.default_client_conf_file_rel_path),
        client_conf_data,
    )

    # Create the required `venv`:
    required_venv_dir_rel_path = "project_venv"
    required_venv_dir_abs_path = tmp_path / required_venv_dir_rel_path
    venv.create(required_venv_dir_abs_path, with_pip=True)
    required_venv_python = required_venv_dir_abs_path / "bin" / "python"

    # Project to install:
    protoprimer_project_dir = pathlib.Path(protoprimer.__file__).parent.parent.parent
    project_dir = tmp_path / "pyproject"
    os.mkdir(project_dir)
    toml_data = {
        "project": {
            "name": "whatever",
            "version": "0.0.0.dev0",
            "dependencies": [
                f"protoprimer @ file://{protoprimer_project_dir}",
            ],
        }
    }
    save_toml_data(
        str(project_dir / "pyproject.toml"),
        toml_data,
    )

    env_conf_data = {
        ConfField.field_env_local_python_file_abs_path.value: sys.executable,
        ConfField.field_env_local_venv_dir_rel_path.value: required_venv_dir_rel_path,
        ConfField.field_env_project_descriptors.value: [
            {
                ConfField.field_env_build_root_dir_rel_path.value: str(project_dir),
                ConfField.field_env_install_extras.value: [],
            },
        ],
    }
    write_json_file(
        str(tmp_path / ConfConstClient.default_file_basename_leap_env),
        env_conf_data,
    )

    proto_code_file = tmp_path / "primer_kernel.py"
    command_args = [
        str(required_venv_python),
        str(proto_code_file),
        ArgConst.arg_py_exec,
        PythonExecutable.py_exec_venv.name,
        ArgConst.arg_proto_code_abs_file_path,
        str(proto_code_file),
    ]

    # when:
    # then:
    sub_proc = subprocess.run(
        command_args,
        capture_output=False,
        text=True,
        check=True,
    )
