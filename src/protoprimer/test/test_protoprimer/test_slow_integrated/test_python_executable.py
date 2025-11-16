import pathlib
import subprocess
import sys
import venv

from local_test.integrated_helper import (
    create_conf_client_file,
    create_conf_env_file,
    create_conf_primer_file,
    create_plain_proto_code,
    create_test_pyproject_toml,
    switch_to_ref_root_abs_path,
    test_pyproject_src_dir_rel_path,
)
from protoprimer.primer_kernel import (
    ConfConstClient,
    ConfConstGeneral,
    ConfConstInput,
    ConfConstPrimer,
    EnvVar,
    PythonExecutable,
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

    ref_root_abs_path = switch_to_ref_root_abs_path(tmp_path)

    # === create `ConfLeap.leap_primer`

    # An arbitrary venv to start from:
    arbitrary_venv_dir = ref_root_abs_path / "arbitrary_venv"
    venv.create(arbitrary_venv_dir, with_pip=True)
    arbitrary_venv_python = (
        arbitrary_venv_dir / ConfConstGeneral.file_rel_path_venv_python
    )

    # === create `ConfLeap.leap_primer`

    proto_code_dir_abs_path = (
        ref_root_abs_path / ConfConstInput.default_proto_conf_dir_rel_path
    )
    proto_kernel_abs_path: pathlib.Path = create_plain_proto_code(
        proto_code_dir_abs_path
    )
    create_conf_primer_file(
        ref_root_abs_path,
        proto_code_dir_abs_path,
    )

    # === create `pyproject.toml`

    project_dir_abs_path = ref_root_abs_path / test_pyproject_src_dir_rel_path
    create_test_pyproject_toml(project_dir_abs_path)

    # === create `ConfLeap.leap_env` / `default_env`

    conf_env_dir_abs_path = (
        ref_root_abs_path / ConfConstClient.default_client_default_env_dir_rel_path
    )

    create_conf_env_file(
        ref_root_abs_path,
        conf_env_dir_abs_path,
        project_dir_abs_path,
    )

    # === create `ConfLeap.leap_client`

    conf_client_dir_abs_path = (
        ref_root_abs_path / ConfConstPrimer.default_client_conf_dir_rel_path
    )

    create_conf_client_file(
        ref_root_abs_path,
        conf_client_dir_abs_path,
        conf_env_dir_abs_path,
    )

    command_args = [
        str(arbitrary_venv_python),
        proto_kernel_abs_path,
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

    ref_root_abs_path = switch_to_ref_root_abs_path(tmp_path)

    # === create `ConfLeap.leap_primer`

    # Create the required `venv`:
    required_venv_dir_rel_path = "required_venv"
    required_venv_dir_abs_path = ref_root_abs_path / required_venv_dir_rel_path
    venv.create(required_venv_dir_abs_path, with_pip=True)
    required_venv_python = (
        required_venv_dir_abs_path / ConfConstGeneral.file_rel_path_venv_python
    )

    # === create `ConfLeap.leap_primer`

    proto_code_dir_abs_path = (
        ref_root_abs_path / ConfConstInput.default_proto_conf_dir_rel_path
    )
    create_plain_proto_code(proto_code_dir_abs_path)
    create_conf_primer_file(
        ref_root_abs_path,
        proto_code_dir_abs_path,
    )

    # === create `pyproject.toml`

    project_dir_abs_path = ref_root_abs_path / test_pyproject_src_dir_rel_path
    create_test_pyproject_toml(project_dir_abs_path)

    # === create `ConfLeap.leap_env` / `default_env`

    conf_env_dir_abs_path = (
        ref_root_abs_path / ConfConstClient.default_client_default_env_dir_rel_path
    )

    create_conf_env_file(
        ref_root_abs_path,
        conf_env_dir_abs_path,
        project_dir_abs_path,
        python_abs_path=sys.executable,
        venv_dir_rel_path=required_venv_dir_rel_path,
    )

    # === create `ConfLeap.leap_client`

    conf_client_dir_abs_path = (
        ref_root_abs_path / ConfConstPrimer.default_client_conf_dir_rel_path
    )

    create_conf_client_file(
        ref_root_abs_path,
        conf_client_dir_abs_path,
        conf_env_dir_abs_path,
    )

    # ===

    proto_code_file = (
        ref_root_abs_path
        / ConfConstGeneral.name_proto_code
        / ConfConstGeneral.default_proto_code_basename
    )
    command_args = [
        str(required_venv_python),
        str(proto_code_file),
    ]

    # when:
    # then:
    sub_proc = subprocess.run(
        command_args,
        capture_output=False,
        text=True,
        check=True,
        env={
            EnvVar.var_PROTOPRIMER_PY_EXEC.value: PythonExecutable.py_exec_venv.name,
            EnvVar.var_PROTOPRIMER_PROTO_CODE.value: str(proto_code_file),
        },
    )
