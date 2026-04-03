import os
import pathlib
import platform
import stat
import subprocess
import sys

from local_doc import (
    cmd_app_starter,
    cmd_env_bootstrapper,
)
from local_test.case_condition import is_min_python
from local_test.integrated_helper import (
    convert_test_python_version,
    create_conf_client_file,
    create_conf_env_file,
    create_conf_primer_file,
    create_plain_proto_code,
    create_test_pyproject_toml,
    create_test_python_selector,
    switch_to_ref_root_abs_path,
    test_pyproject_src_dir_rel_path,
)
from protoprimer.primer_kernel import (
    ConfConstClient,
    ConfConstGeneral,
    ConfConstInput,
    ConfConstPrimer,
    EnvVar,
    KeyWord,
    ExecMode,
    SyntaxArg,
    VenvDriverBase,
    VenvDriverPip,
    VenvDriverUv,
)
from protoprimer.proto_generator import generate_entry_script_content


def test_python_from_arbitrary_venv_with_app_starter(
    tmp_path: pathlib.Path,
):
    """
    Run the `env_bootstrapper` then `app_starter` from within an arbitrary virtual environment.
    """

    # given:

    ref_root_abs_path = switch_to_ref_root_abs_path(tmp_path)

    # === create `ConfLeap.leap_primer`

    # An arbitrary venv to start from:
    arbitrary_venv_dir = ref_root_abs_path / "arbitrary_venv"
    venv_driver = VenvDriverPip(
        required_python_version=platform.python_version(),
        selected_python_file_abs_path=sys.executable,
        state_local_venv_dir_abs_path_inited=str(arbitrary_venv_dir),
    )
    venv_driver.create_venv(str(arbitrary_venv_dir))
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
        ref_root_abs_path / ConfConstClient.default_default_env_dir_rel_path
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
        project_dir_abs_path,
    )

    # === create `env_bootstrapper` entry script

    env_bootstrapper_script_abs_path = ref_root_abs_path / "env_bootstrapper"
    env_bootstrapper_script_content = generate_entry_script_content(
        ExecMode.mode_prime.value,
        str(proto_kernel_abs_path),
        str(env_bootstrapper_script_abs_path),
        f"{cmd_env_bootstrapper.__name__}",
        f"{cmd_env_bootstrapper.custom_main.__name__}",
        {},
    )
    with open(env_bootstrapper_script_abs_path, "w") as f:
        f.write(env_bootstrapper_script_content)
    env_bootstrapper_script_abs_path.chmod(
        env_bootstrapper_script_abs_path.stat().st_mode | stat.S_IEXEC
    )

    # === create `app_starter` entry script

    app_starter_script_abs_path = ref_root_abs_path / "app_starter"
    app_starter_script_content = generate_entry_script_content(
        ExecMode.mode_start.value,
        str(proto_kernel_abs_path),
        str(app_starter_script_abs_path),
        f"{cmd_app_starter.__name__}",
        f"{cmd_app_starter.custom_main.__name__}",
        {},
    )
    with open(app_starter_script_abs_path, "w") as f:
        f.write(app_starter_script_content)
    app_starter_script_abs_path.chmod(
        app_starter_script_abs_path.stat().st_mode | stat.S_IEXEC
    )

    # === run `env_bootstrapper`
    # See FT_75_87_82_46.entry_script.md

    command_args_env_bootstrapper = [
        str(arbitrary_venv_python),
        str(env_bootstrapper_script_abs_path),
    ]

    sub_proc_env_bootstrapper = subprocess.run(
        command_args_env_bootstrapper,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Hello, world!" in sub_proc_env_bootstrapper.stdout

    # === run `app_starter`
    # See FT_75_87_82_46.entry_script.md

    command_args_app_starter = [
        str(arbitrary_venv_python),
        str(app_starter_script_abs_path),
    ]

    # when:
    sub_proc_app_starter = subprocess.run(
        command_args_app_starter,
        capture_output=True,
        text=True,
        check=True,
    )

    # then:
    assert "Hello, world!" in sub_proc_app_starter.stdout


def test_python_from_required_venv_with_app_starter(
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
    venv_driver: VenvDriverBase
    if is_min_python():
        venv_driver = VenvDriverPip(
            required_python_version=platform.python_version(),
            selected_python_file_abs_path=sys.executable,
            state_local_venv_dir_abs_path_inited=str(required_venv_dir_abs_path),
        )
    else:
        venv_driver = VenvDriverUv(
            required_python_version=convert_test_python_version(
                platform.python_version()
            ),
            selected_python_file_abs_path=sys.executable,
            state_local_venv_dir_abs_path_inited=str(required_venv_dir_abs_path),
            state_local_cache_dir_abs_path_inited=str(
                ref_root_abs_path / KeyWord.key_var.value / KeyWord.key_cache.value
            ),
        )
    venv_driver.create_venv(str(required_venv_dir_abs_path))
    required_venv_python = (
        required_venv_dir_abs_path / ConfConstGeneral.file_rel_path_venv_python
    )

    # === create `python` selector (see FT_72_45_12_06.python_executable.md)

    python_version: str = f"{sys.version_info.major}.{sys.version_info.minor}"
    python_selector_rel_path: pathlib.Path = pathlib.Path(
        f"test_python_selector_py{python_version}.py"
    )
    create_test_python_selector(
        ref_root_abs_path,
        python_selector_rel_path,
        python_version,
    )

    # === create `ConfLeap.leap_primer`

    proto_code_dir_abs_path = (
        ref_root_abs_path / ConfConstInput.default_proto_conf_dir_rel_path
    )
    proto_kernel_abs_path = create_plain_proto_code(proto_code_dir_abs_path)
    create_conf_primer_file(
        ref_root_abs_path,
        proto_code_dir_abs_path,
    )

    # === create `pyproject.toml`

    project_dir_abs_path = ref_root_abs_path / test_pyproject_src_dir_rel_path
    create_test_pyproject_toml(project_dir_abs_path)

    # === create `ConfLeap.leap_env` / `default_env`

    conf_env_dir_abs_path = (
        ref_root_abs_path / ConfConstClient.default_default_env_dir_rel_path
    )

    base_python_executable = os.path.join(
        sys.base_prefix, ConfConstGeneral.file_rel_path_venv_python
    )
    create_conf_env_file(
        ref_root_abs_path,
        conf_env_dir_abs_path,
        project_dir_abs_path,
        python_abs_path=base_python_executable,
        venv_dir_rel_path=required_venv_dir_rel_path,
        python_selector_rel_path=python_selector_rel_path,
    )

    # === create `ConfLeap.leap_client`

    conf_client_dir_abs_path = (
        ref_root_abs_path / ConfConstPrimer.default_client_conf_dir_rel_path
    )

    create_conf_client_file(
        ref_root_abs_path,
        conf_client_dir_abs_path,
        conf_env_dir_abs_path,
        project_dir_abs_path,
    )

    # === create `env_bootstrapper` entry script

    env_bootstrapper_script_abs_path = ref_root_abs_path / "env_bootstrapper"
    env_bootstrapper_script_content = generate_entry_script_content(
        ExecMode.mode_prime.value,
        str(proto_kernel_abs_path),
        str(env_bootstrapper_script_abs_path),
        f"{cmd_env_bootstrapper.__name__}",
        f"{cmd_env_bootstrapper.custom_main.__name__}",
        {},
    )
    with open(env_bootstrapper_script_abs_path, "w") as f:
        f.write(env_bootstrapper_script_content)
    env_bootstrapper_script_abs_path.chmod(
        env_bootstrapper_script_abs_path.stat().st_mode | stat.S_IEXEC
    )

    # === create `app_starter` entry script

    app_starter_script_abs_path = ref_root_abs_path / "app_starter"
    app_starter_script_content = generate_entry_script_content(
        ExecMode.mode_start.value,
        str(proto_kernel_abs_path),
        str(app_starter_script_abs_path),
        f"{cmd_app_starter.__name__}",
        f"{cmd_app_starter.custom_main.__name__}",
        {},
    )
    with open(app_starter_script_abs_path, "w") as f:
        f.write(app_starter_script_content)
    app_starter_script_abs_path.chmod(
        app_starter_script_abs_path.stat().st_mode | stat.S_IEXEC
    )

    # === run `env_bootstrapper`
    # See FT_75_87_82_46.entry_script.md

    command_args_env_bootstrapper = [
        str(required_venv_python),
        str(env_bootstrapper_script_abs_path),
    ]

    sub_proc_env_bootstrapper = subprocess.run(
        command_args_env_bootstrapper,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Hello, world!" in sub_proc_env_bootstrapper.stdout

    # === run `app_starter`
    # See FT_75_87_82_46.entry_script.md

    command_args_app_starter = [
        str(required_venv_python),
        str(app_starter_script_abs_path),
    ]

    # when:
    sub_proc_app_starter = subprocess.run(
        command_args_app_starter,
        capture_output=True,
        text=True,
        check=True,
    )

    # then:
    assert "Hello, world!" in sub_proc_app_starter.stdout
