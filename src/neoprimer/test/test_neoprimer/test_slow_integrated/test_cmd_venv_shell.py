import pathlib
import stat
import subprocess

from local_repo.sub_proc_util import (
    get_command_code,
    get_command_output,
)
from local_test.integrated_helper import (
    create_conf_client_file,
    create_conf_env_file,
    create_conf_primer_file,
    create_plain_proto_code,
    create_test_pyproject_toml,
    switch_to_ref_root_abs_path,
    test_pyproject_src_dir_rel_path,
)
from local_test.package_version_verifier import extract_package_version
from neoprimer import cmd_venv_shell
from neoprimer.cmd_venv_shell import custom_main
from protoprimer.primer_kernel import (
    ConfConstClient,
    ConfConstEnv,
    ConfConstInput,
    ConfConstPrimer,
    EnvVar,
    RunMode,
    SyntaxArg,
)
from protoprimer.proto_generator import generate_entry_script_content


def test_venv_shell_no_update(tmp_path: pathlib.Path):

    # given:

    ref_root_abs_path = switch_to_ref_root_abs_path(tmp_path)

    # ===

    proto_code_dir_abs_path = (
        ref_root_abs_path / ConfConstInput.default_proto_conf_dir_rel_path
    )
    create_plain_proto_code(proto_code_dir_abs_path)
    create_conf_primer_file(
        ref_root_abs_path,
        proto_code_dir_abs_path,
    )

    # ===

    project_dir_abs_path = ref_root_abs_path / test_pyproject_src_dir_rel_path
    create_test_pyproject_toml(project_dir_abs_path, ["pyfakefs"])

    # ===

    conf_env_dir_abs_path = (
        ref_root_abs_path / ConfConstClient.default_default_env_dir_rel_path
    )

    create_conf_env_file(
        ref_root_abs_path,
        conf_env_dir_abs_path,
        project_dir_abs_path,
    )

    # ===

    conf_client_dir_abs_path = (
        ref_root_abs_path / ConfConstPrimer.default_client_conf_dir_rel_path
    )

    create_conf_client_file(
        ref_root_abs_path,
        conf_client_dir_abs_path,
        conf_env_dir_abs_path,
        project_dir_abs_path,
    )

    # ===

    package_name = "pyfakefs"
    constraints_file = conf_env_dir_abs_path / ConfConstEnv.constraints_txt_basename
    constraints_file.write_text(f"{package_name}==5.7.4")

    # when:

    # Bootstrap the environment before running the other commands:
    get_command_code("./proto_code/proto_kernel.py")

    # then:

    venv_pip = (
        ref_root_abs_path / ConfConstEnv.default_dir_rel_path_venv / "bin" / "pip"
    )
    pip_freeze_output_install = get_command_output(f"{venv_pip} freeze")
    package_version_install = extract_package_version(
        pip_freeze_output_install, package_name
    )
    assert f"{package_name}==5.7.4" in pip_freeze_output_install

    # given:

    venv_shell_script_content = generate_entry_script_content(
        "neoprimer.cmd_venv_shell",
        "custom_main",
        {
            "PROTOPRIMER_DO_INSTALL": "False",
        },
    )
    venv_shell_script_path = ref_root_abs_path / "venv_shell"
    with open(venv_shell_script_path, "w") as f:
        f.write(venv_shell_script_content)
    venv_shell_script_path.chmod(venv_shell_script_path.stat().st_mode | stat.S_IEXEC)

    # when:
    # Run the interactive shell and pipe "exit 42" to its `stdin` to make it terminate with a specific exit code.
    sub_proc = subprocess.run(
        "./venv_shell -vv",
        shell=True,
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


def test_venv_shell_command_execution(tmp_path: pathlib.Path):

    # given:

    ref_root_abs_path = switch_to_ref_root_abs_path(tmp_path)

    # ===

    proto_code_dir_abs_path = (
        ref_root_abs_path / ConfConstInput.default_proto_conf_dir_rel_path
    )
    create_plain_proto_code(proto_code_dir_abs_path)
    create_conf_primer_file(
        ref_root_abs_path,
        proto_code_dir_abs_path,
    )

    # ===

    project_dir_abs_path = ref_root_abs_path / test_pyproject_src_dir_rel_path
    create_test_pyproject_toml(project_dir_abs_path, [])

    # ===

    conf_env_dir_abs_path = (
        ref_root_abs_path / ConfConstClient.default_default_env_dir_rel_path
    )

    create_conf_env_file(
        ref_root_abs_path,
        conf_env_dir_abs_path,
        project_dir_abs_path,
    )

    # ===

    conf_client_dir_abs_path = (
        ref_root_abs_path / ConfConstPrimer.default_client_conf_dir_rel_path
    )

    create_conf_client_file(
        ref_root_abs_path,
        conf_client_dir_abs_path,
        conf_env_dir_abs_path,
        project_dir_abs_path,
    )

    # ===

    # Bootstraps the env before running other commands:
    get_command_code("./proto_code/proto_kernel.py")

    # ===

    venv_shell_script_content = generate_entry_script_content(
        f"{cmd_venv_shell.__name__}",
        f"{custom_main.__name__}",
        {
            f"{EnvVar.var_PROTOPRIMER_DO_INSTALL.value}": str(False),
        },
    )
    venv_shell_script_path = ref_root_abs_path / "venv_shell"
    with open(venv_shell_script_path, "w") as f:
        f.write(venv_shell_script_content)
    venv_shell_script_path.chmod(venv_shell_script_path.stat().st_mode | stat.S_IEXEC)
    output_file = ref_root_abs_path / "test_file.txt"
    assert not output_file.exists()

    # when:
    get_command_code(
        f'./venv_shell {RunMode.mode_prime.value} {SyntaxArg.arg_command} "touch {output_file}"'
    )

    # then:
    assert output_file.exists()
