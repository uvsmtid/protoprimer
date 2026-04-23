import os
import pathlib
import platform
import stat
import subprocess
import sys

from local_doc import (
    cmd_start_app,
    cmd_boot_env,
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
    SubCommand,
    SyntaxArg,
    VenvDriverBase,
    VenvDriverPip,
    VenvDriverUv,
)
from protoprimer.proto_generator import generate_entry_script_content


def test_python_from_arbitrary_venv_with_start_app(
    tmp_path: pathlib.Path,
):
    """
    Run the `boot_env` then `start_app` from within an arbitrary virtual environment.
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
    arbitrary_venv_python = arbitrary_venv_dir / ConfConstGeneral.file_rel_path_venv_python

    # === create `ConfLeap.leap_primer`

    proto_code_dir_abs_path = ref_root_abs_path / ConfConstInput.default_proto_conf_dir_rel_path
    proto_kernel_abs_path: pathlib.Path = create_plain_proto_code(proto_code_dir_abs_path)
    create_conf_primer_file(
        ref_root_abs_path,
        proto_code_dir_abs_path,
    )

    # === create `pyproject.toml`

    project_dir_abs_path = ref_root_abs_path / test_pyproject_src_dir_rel_path
    create_test_pyproject_toml(project_dir_abs_path)

    # === create `ConfLeap.leap_env` / `default_env`

    conf_env_dir_abs_path = ref_root_abs_path / ConfConstClient.default_default_env_dir_rel_path

    create_conf_env_file(
        ref_root_abs_path,
        conf_env_dir_abs_path,
        project_dir_abs_path,
    )

    # === create `ConfLeap.leap_client`

    conf_client_dir_abs_path = ref_root_abs_path / ConfConstPrimer.default_client_conf_dir_rel_path

    create_conf_client_file(
        ref_root_abs_path,
        conf_client_dir_abs_path,
        conf_env_dir_abs_path,
        project_dir_abs_path,
    )

    # === create `boot_env` entry script

    boot_env_script_abs_path = ref_root_abs_path / "boot_env"
    boot_env_script_content = generate_entry_script_content(
        SubCommand.command_boot.value,
        str(proto_kernel_abs_path),
        str(boot_env_script_abs_path),
        f"{cmd_boot_env.__name__}",
        f"{cmd_boot_env.custom_main.__name__}",
        {},
    )
    with open(boot_env_script_abs_path, "w") as f:
        f.write(boot_env_script_content)
    boot_env_script_abs_path.chmod(boot_env_script_abs_path.stat().st_mode | stat.S_IEXEC)

    # === create `start_app` entry script

    start_app_script_abs_path = ref_root_abs_path / "start_app"
    start_app_script_content = generate_entry_script_content(
        SubCommand.command_start.value,
        str(proto_kernel_abs_path),
        str(start_app_script_abs_path),
        f"{cmd_start_app.__name__}",
        f"{cmd_start_app.custom_main.__name__}",
        {},
    )
    with open(start_app_script_abs_path, "w") as f:
        f.write(start_app_script_content)
    start_app_script_abs_path.chmod(start_app_script_abs_path.stat().st_mode | stat.S_IEXEC)

    # === run `boot_env`
    # See FT_75_87_82_46.entry_script.md

    command_args_boot_env = [
        str(arbitrary_venv_python),
        str(boot_env_script_abs_path),
    ]

    sub_proc_boot_env = subprocess.run(
        command_args_boot_env,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Hello, world!" in sub_proc_boot_env.stdout

    # === run `start_app`
    # See FT_75_87_82_46.entry_script.md

    command_args_start_app = [
        str(arbitrary_venv_python),
        str(start_app_script_abs_path),
    ]

    # when:
    sub_proc_start_app = subprocess.run(
        command_args_start_app,
        capture_output=True,
        text=True,
        check=True,
    )

    # then:
    assert "Hello, world!" in sub_proc_start_app.stdout


def test_python_from_required_venv_with_start_app(
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
            required_python_version=convert_test_python_version(platform.python_version()),
            selected_python_file_abs_path=sys.executable,
            state_local_venv_dir_abs_path_inited=str(required_venv_dir_abs_path),
            state_local_cache_dir_abs_path_inited=str(ref_root_abs_path / KeyWord.key_var.value / KeyWord.key_cache.value),
        )
    venv_driver.create_venv(str(required_venv_dir_abs_path))
    required_venv_python = required_venv_dir_abs_path / ConfConstGeneral.file_rel_path_venv_python

    # === create `python` selector (see FT_72_45_12_06.python_executable.md)

    python_version: str = f"{sys.version_info.major}.{sys.version_info.minor}"
    python_selector_rel_path: pathlib.Path = pathlib.Path(f"test_python_selector_py{python_version}.py")
    create_test_python_selector(
        ref_root_abs_path,
        python_selector_rel_path,
        python_version,
    )

    # === create `ConfLeap.leap_primer`

    proto_code_dir_abs_path = ref_root_abs_path / ConfConstInput.default_proto_conf_dir_rel_path
    proto_kernel_abs_path = create_plain_proto_code(proto_code_dir_abs_path)
    create_conf_primer_file(
        ref_root_abs_path,
        proto_code_dir_abs_path,
    )

    # === create `pyproject.toml`

    project_dir_abs_path = ref_root_abs_path / test_pyproject_src_dir_rel_path
    create_test_pyproject_toml(project_dir_abs_path)

    # === create `ConfLeap.leap_env` / `default_env`

    conf_env_dir_abs_path = ref_root_abs_path / ConfConstClient.default_default_env_dir_rel_path

    base_python_executable = os.path.join(sys.base_prefix, ConfConstGeneral.file_rel_path_venv_python)
    create_conf_env_file(
        ref_root_abs_path,
        conf_env_dir_abs_path,
        project_dir_abs_path,
        python_abs_path=base_python_executable,
        venv_dir_rel_path=required_venv_dir_rel_path,
        python_selector_rel_path=python_selector_rel_path,
    )

    # === create `ConfLeap.leap_client`

    conf_client_dir_abs_path = ref_root_abs_path / ConfConstPrimer.default_client_conf_dir_rel_path

    create_conf_client_file(
        ref_root_abs_path,
        conf_client_dir_abs_path,
        conf_env_dir_abs_path,
        project_dir_abs_path,
    )

    # === create `boot_env` entry script

    boot_env_script_abs_path = ref_root_abs_path / "boot_env"
    boot_env_script_content = generate_entry_script_content(
        SubCommand.command_boot.value,
        str(proto_kernel_abs_path),
        str(boot_env_script_abs_path),
        f"{cmd_boot_env.__name__}",
        f"{cmd_boot_env.custom_main.__name__}",
        {},
    )
    with open(boot_env_script_abs_path, "w") as f:
        f.write(boot_env_script_content)
    boot_env_script_abs_path.chmod(boot_env_script_abs_path.stat().st_mode | stat.S_IEXEC)

    # === create `start_app` entry script

    start_app_script_abs_path = ref_root_abs_path / "start_app"
    start_app_script_content = generate_entry_script_content(
        SubCommand.command_start.value,
        str(proto_kernel_abs_path),
        str(start_app_script_abs_path),
        f"{cmd_start_app.__name__}",
        f"{cmd_start_app.custom_main.__name__}",
        {},
    )
    with open(start_app_script_abs_path, "w") as f:
        f.write(start_app_script_content)
    start_app_script_abs_path.chmod(start_app_script_abs_path.stat().st_mode | stat.S_IEXEC)

    # === run `boot_env`
    # See FT_75_87_82_46.entry_script.md

    command_args_boot_env = [
        str(required_venv_python),
        str(boot_env_script_abs_path),
    ]

    sub_proc_boot_env = subprocess.run(
        command_args_boot_env,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Hello, world!" in sub_proc_boot_env.stdout

    # === run `start_app`
    # See FT_75_87_82_46.entry_script.md

    command_args_start_app = [
        str(required_venv_python),
        str(start_app_script_abs_path),
    ]

    # when:
    sub_proc_start_app = subprocess.run(
        command_args_start_app,
        capture_output=True,
        text=True,
        check=True,
    )

    # then:
    assert "Hello, world!" in sub_proc_start_app.stdout
