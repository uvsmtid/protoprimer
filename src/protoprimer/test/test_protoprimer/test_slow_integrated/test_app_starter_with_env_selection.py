import pathlib
import pathlib
import stat
import subprocess
import sys

from local_doc import cmd_app_starter
from local_test.fat_mocked_helper import run_primer_main
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
    PackageDriverPip,
    RunMode,
    SyntaxArg,
)
from protoprimer.proto_generator import generate_entry_script_content


def test_app_starter_from_env_default(tmp_path: pathlib.Path):
    """
    *   Bootstrap env without args -> picks `ConfConstClient.common_env_name` as configured.
    *   Start app -> picks `ConfConstClient.common_env_name` as specified.
    """

    # given:

    ref_root_abs_path = switch_to_ref_root_abs_path(tmp_path)

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

    # An arbitrary venv to start from:
    arbitrary_venv_dir = ref_root_abs_path / "arbitrary_venv"
    package_driver = PackageDriverPip()
    package_driver.create_venv(sys.executable, str(arbitrary_venv_dir))
    arbitrary_venv_python = (
        arbitrary_venv_dir / ConfConstGeneral.file_rel_path_venv_python
    )

    # === create `pyproject.toml`

    project_dir_abs_path = ref_root_abs_path / test_pyproject_src_dir_rel_path
    create_test_pyproject_toml(project_dir_abs_path)

    # === create `ConfLeap.leap_env` / `ConfConstClient.common_env_name`

    common_env_dir_name = ConfConstClient.common_env_name
    common_env_dir_abs_path = ref_root_abs_path / common_env_dir_name
    default_venv_rel_path = "venv_default"
    create_conf_env_file(
        ref_root_abs_path,
        common_env_dir_abs_path,
        project_dir_abs_path,
        venv_dir_rel_path=default_venv_rel_path,
    )

    # === create `ConfLeap.leap_env` / `special_env`

    special_env_dir_name = "special_env"
    special_env_dir_abs_path = ref_root_abs_path / special_env_dir_name
    special_venv_rel_path = "venv_special"
    create_conf_env_file(
        ref_root_abs_path,
        special_env_dir_abs_path,
        project_dir_abs_path,
        venv_dir_rel_path=special_venv_rel_path,
    )

    # === create `ConfLeap.leap_client` / `ConfConstClient.common_env_name`

    conf_client_dir_abs_path = (
        ref_root_abs_path / ConfConstPrimer.default_client_conf_dir_rel_path
    )

    create_conf_client_file(
        ref_root_abs_path,
        conf_client_dir_abs_path,
        common_env_dir_abs_path,
        project_dir_abs_path,
    )

    # ===

    default_venv_abs_path = ref_root_abs_path / default_venv_rel_path
    special_venv_abs_path = ref_root_abs_path / special_venv_rel_path

    # === create `app_starter` entry script

    app_starter_script_abs_path = ref_root_abs_path / "app_starter"
    app_starter_script_content = generate_entry_script_content(
        RunMode.mode_start.value,
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

    # when:
    # bootstrap with `ConfConstClient.common_env_name`

    run_primer_main(
        [
            str(proto_kernel_abs_path),
            SyntaxArg.arg_v,
            SyntaxArg.arg_v,
        ]
    )

    # then:
    # assert `ConfConstClient.common_env_name` created

    assert default_venv_abs_path.exists()
    assert not special_venv_abs_path.exists()

    # when:
    # start without args

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


def test_app_started_from_env_special(tmp_path: pathlib.Path):
    """
    *   Bootstrap with override `SyntaxArg.arg_env` -> picks `special_env` as specified.
    *   Start app -> still picks `special_env` as configured (not `ConfConstClient.common_env_name`).
    """

    # given:

    ref_root_abs_path = switch_to_ref_root_abs_path(tmp_path)

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

    # An arbitrary venv to start from:
    arbitrary_venv_dir = ref_root_abs_path / "arbitrary_venv"
    package_driver = PackageDriverPip()
    package_driver.create_venv(sys.executable, str(arbitrary_venv_dir))
    arbitrary_venv_python = (
        arbitrary_venv_dir / ConfConstGeneral.file_rel_path_venv_python
    )

    # === create `pyproject.toml`

    project_dir_abs_path = ref_root_abs_path / test_pyproject_src_dir_rel_path
    create_test_pyproject_toml(project_dir_abs_path)

    # === create `ConfLeap.leap_env` / `special_env`

    special_env_dir_name = "special_env"
    special_env_dir_abs_path = ref_root_abs_path / special_env_dir_name
    special_venv_rel_path = "venv_special"
    create_conf_env_file(
        ref_root_abs_path,
        special_env_dir_abs_path,
        project_dir_abs_path,
        venv_dir_rel_path=special_venv_rel_path,
    )

    # === create `ConfLeap.leap_env` / `ConfConstClient.common_env_name`

    common_env_dir_name = ConfConstClient.common_env_name
    common_env_dir_abs_path = ref_root_abs_path / common_env_dir_name
    default_venv_rel_path = "venv_default"
    create_conf_env_file(
        ref_root_abs_path,
        common_env_dir_abs_path,
        project_dir_abs_path,
        venv_dir_rel_path=default_venv_rel_path,
    )

    # === create `ConfLeap.leap_client` / `special_env`

    conf_client_dir_abs_path = (
        ref_root_abs_path / ConfConstPrimer.default_client_conf_dir_rel_path
    )

    create_conf_client_file(
        ref_root_abs_path,
        conf_client_dir_abs_path,
        special_env_dir_abs_path,
        project_dir_abs_path,
    )

    # ===

    default_venv_abs_path = ref_root_abs_path / default_venv_rel_path
    special_venv_abs_path = ref_root_abs_path / special_venv_rel_path

    # === create `app_starter` entry script

    app_starter_script_abs_path = ref_root_abs_path / "app_starter"
    app_starter_script_content = generate_entry_script_content(
        RunMode.mode_start.value,
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

    # when:
    # bootstrap with `special_env`

    run_primer_main(
        [
            str(proto_kernel_abs_path),
            SyntaxArg.arg_v,
            SyntaxArg.arg_v,
            RunMode.mode_prime.value,
            SyntaxArg.arg_env,
            special_env_dir_name,
        ]
    )

    # then:
    # assert `special_env` created

    assert not default_venv_abs_path.exists()
    assert special_venv_abs_path.exists()

    # when:
    # start without args

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


def test_app_started_with_symlink_to_env_special_but_config_to_env_common(
    tmp_path: pathlib.Path,
):
    """
    *   Bootstrap with override `SyntaxArg.arg_env` -> picks `special_env` as specified.
    *   Change config to use `ConfConstClient.common_env_name` as default.
    *   Start app -> still picks `special_env` as set by symlink.
    """

    # given:

    ref_root_abs_path = switch_to_ref_root_abs_path(tmp_path)

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

    # An arbitrary venv to start from:
    arbitrary_venv_dir = ref_root_abs_path / "arbitrary_venv"
    package_driver = PackageDriverPip()
    package_driver.create_venv(sys.executable, str(arbitrary_venv_dir))
    arbitrary_venv_python = (
        arbitrary_venv_dir / ConfConstGeneral.file_rel_path_venv_python
    )

    # === create `pyproject.toml`

    project_dir_abs_path = ref_root_abs_path / test_pyproject_src_dir_rel_path
    create_test_pyproject_toml(project_dir_abs_path)

    # === create `ConfLeap.leap_env` / `special_env`

    special_env_dir_name = "special_env"
    special_env_dir_abs_path = ref_root_abs_path / special_env_dir_name
    special_venv_rel_path = "venv_special"
    create_conf_env_file(
        ref_root_abs_path,
        special_env_dir_abs_path,
        project_dir_abs_path,
        venv_dir_rel_path=special_venv_rel_path,
    )

    # === create `ConfLeap.leap_env` / `ConfConstClient.common_env_name`

    common_env_dir_name = ConfConstClient.common_env_name
    common_env_dir_abs_path = ref_root_abs_path / common_env_dir_name
    default_venv_rel_path = "venv_default"
    create_conf_env_file(
        ref_root_abs_path,
        common_env_dir_abs_path,
        project_dir_abs_path,
        venv_dir_rel_path=default_venv_rel_path,
    )

    # === create `ConfLeap.leap_client` / `special_env`

    conf_client_dir_abs_path = (
        ref_root_abs_path / ConfConstPrimer.default_client_conf_dir_rel_path
    )

    create_conf_client_file(
        ref_root_abs_path,
        conf_client_dir_abs_path,
        special_env_dir_abs_path,
        project_dir_abs_path,
    )

    # ===

    default_venv_abs_path = ref_root_abs_path / default_venv_rel_path
    special_venv_abs_path = ref_root_abs_path / special_venv_rel_path

    # === create `app_starter` entry script

    app_starter_script_abs_path = ref_root_abs_path / "app_starter"
    app_starter_script_content = generate_entry_script_content(
        RunMode.mode_start.value,
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

    # when:
    # bootstrap with `special_env`

    run_primer_main(
        [
            str(proto_kernel_abs_path),
            SyntaxArg.arg_v,
            SyntaxArg.arg_v,
            RunMode.mode_prime.value,
            SyntaxArg.arg_env,
            special_env_dir_name,
        ]
    )

    # then:
    # assert `special_env` created

    assert not default_venv_abs_path.exists()
    assert special_venv_abs_path.exists()

    # given:
    # switch config from `env_special` to `ConfConstClient.common_env_name`

    create_conf_client_file(
        ref_root_abs_path,
        conf_client_dir_abs_path,
        common_env_dir_abs_path,
        project_dir_abs_path,
    )

    # when:
    # start without args

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
