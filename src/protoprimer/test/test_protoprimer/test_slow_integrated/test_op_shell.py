import subprocess
from pathlib import Path

from local_repo.sub_proc_util import get_command_output
from local_test.fat_mocked_helper import run_primer_main
from local_test.integrated_helper import (
    create_conf_client_file,
    create_conf_env_file,
    create_conf_primer_file,
    create_max_leaps_shape,
    create_plain_proto_code,
    create_test_pyproject_toml,
    switch_to_ref_root_abs_path,
    test_pyproject_src_dir_rel_path,
)
from local_test.name_assertion import (
    assert_test_func_name_embeds_str,
    assert_test_module_name_embeds_str,
)
from local_test.package_version_verifier import extract_package_version
from protoprimer.primer_kernel import (
    ConfConstClient,
    ConfConstEnv,
    ConfConstGeneral,
    ConfConstInput,
    ConfConstPrimer,
    ExecOperation,
    SyntaxArg,
)


def test_relationship():
    assert_test_module_name_embeds_str(ExecOperation.command_shell.value)


def test_shell_requires_boot_first(tmp_path: Path):
    """
    `ExecOperation.command_shell` is a fast path (like `ExecOperation.op_start`):
    unlike `boot`, it must not create `venv` itself.
    """

    assert_test_func_name_embeds_str(ExecOperation.command_shell.value)

    # given:

    (
        proto_kernel_abs_path,
        ref_root_abs_path,
        project_dir_abs_path,
    ) = create_max_leaps_shape(tmp_path)

    # when:
    # `venv` was never created (`boot` was never run):

    sub_proc = subprocess.run(
        [
            str(proto_kernel_abs_path),
            ExecOperation.command_shell.value,
            SyntaxArg.arg_c,
            "echo should_not_run",
        ],
        capture_output=True,
        text=True,
    )

    # then:

    assert sub_proc.returncode != 0
    assert ExecOperation.op_boot.value in sub_proc.stderr


def test_shell_command_execution(tmp_path: Path):

    assert_test_func_name_embeds_str(ExecOperation.command_shell.value)

    # given:

    (
        proto_kernel_abs_path,
        ref_root_abs_path,
        project_dir_abs_path,
    ) = create_max_leaps_shape(tmp_path)

    # Bootstrap the env before running `shell` - it assumes `venv` already exists:
    run_primer_main([str(proto_kernel_abs_path)])

    output_file = ref_root_abs_path / "test_file.txt"
    assert not output_file.exists()

    # when:

    subprocess.run(
        [
            str(proto_kernel_abs_path),
            ExecOperation.command_shell.value,
            SyntaxArg.arg_c,
            f"touch {output_file}",
        ],
        check=True,
    )

    # then:

    assert output_file.exists()


def test_shell_does_not_reinstall_dependencies(tmp_path: Path):
    """
    `ExecOperation.command_shell` is a fast path (like `ExecOperation.op_start`):
    unlike `boot`, it must not re-install/re-pin dependencies into the existing `venv`.
    """

    assert_test_func_name_embeds_str(ExecOperation.command_shell.value)

    # given:

    ref_root_abs_path = switch_to_ref_root_abs_path(tmp_path)

    proto_code_dir_abs_path = ref_root_abs_path / ConfConstInput.default_proto_conf_dir_rel_path
    proto_kernel_abs_path = create_plain_proto_code(proto_code_dir_abs_path)
    create_conf_primer_file(
        ref_root_abs_path,
        proto_code_dir_abs_path,
    )

    project_dir_abs_path = ref_root_abs_path / test_pyproject_src_dir_rel_path
    create_test_pyproject_toml(
        project_dir_abs_path,
        [
            # NOTE: Install `pip` to query package versions below (even if it might be a `venv` created with `uv`):
            ConfConstGeneral.name_pip_package,
            "pyfakefs",
        ],
    )

    conf_env_dir_abs_path = ref_root_abs_path / ConfConstClient.default_default_env_dir_rel_path
    create_conf_env_file(
        ref_root_abs_path,
        conf_env_dir_abs_path,
        project_dir_abs_path,
    )

    conf_client_dir_abs_path = ref_root_abs_path / ConfConstPrimer.default_client_conf_dir_rel_path
    create_conf_client_file(
        ref_root_abs_path,
        conf_client_dir_abs_path,
        conf_env_dir_abs_path,
        project_dir_abs_path,
    )

    package_name = "pyfakefs"
    constraints_file = conf_env_dir_abs_path / ConfConstEnv.default_version_constraints_file_basename
    constraints_file.write_text(f"{package_name}==5.7.4")

    # Bootstrap the env before running `shell` - it assumes `venv` already exists:
    run_primer_main([str(proto_kernel_abs_path)])

    venv_pip: str = str(ref_root_abs_path / ConfConstEnv.default_dir_rel_path_venv / "bin" / ConfConstGeneral.name_pip_package)
    pip_freeze_output_install = get_command_output(f"{venv_pip} freeze")
    package_version_install = extract_package_version(pip_freeze_output_install, package_name)
    assert f"{package_name}==5.7.4" in pip_freeze_output_install

    # when:
    # Run the interactive shell and pipe "exit 42" to its `stdin` to make it terminate with a specific exit code.

    sub_proc = subprocess.run(
        [
            str(proto_kernel_abs_path),
            ExecOperation.command_shell.value,
        ],
        input="exit 42\n",
        text=True,
    )

    # then:

    assert sub_proc.returncode == 42

    pip_freeze_output_after_shell = get_command_output(f"{venv_pip} freeze")
    package_version_after_shell = extract_package_version(
        pip_freeze_output_after_shell,
        package_name,
    )
    assert package_version_install == package_version_after_shell


def test_shell_interactive(tmp_path: Path):
    """
    Unlike `boot -c` (`ExecOperation.op_boot`), `shell` with no command
    must still start an interactive shell.
    """

    assert_test_func_name_embeds_str(ExecOperation.command_shell.value)

    # given:

    (
        proto_kernel_abs_path,
        ref_root_abs_path,
        project_dir_abs_path,
    ) = create_max_leaps_shape(tmp_path)

    run_primer_main([str(proto_kernel_abs_path)])

    # when:
    # Run the interactive shell and pipe "exit 42" to its `stdin` to make it terminate with a specific exit code.

    sub_proc = subprocess.run(
        [
            str(proto_kernel_abs_path),
            ExecOperation.command_shell.value,
        ],
        input="exit 42\n",
        text=True,
    )

    # then:

    assert sub_proc.returncode == 42
