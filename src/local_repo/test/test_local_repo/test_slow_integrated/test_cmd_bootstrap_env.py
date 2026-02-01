import pathlib
import stat
import subprocess

from local_repo import cmd_bootstrap_env
from local_repo.cmd_bootstrap_env import custom_main
from local_repo.sub_proc_util import get_command_code
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
    ConfConstEnv,
    ConfConstInput,
    ConfConstPrimer,
    RunMode,
)
from protoprimer.proto_generator import generate_entry_script_content


def test_bootstrap_env(tmp_path: pathlib.Path):
    """
    Runs local custom `./cmd/bootstrap_env` and checks that it installs `pre-commit`.
    """

    # given:

    ref_root_abs_path = switch_to_ref_root_abs_path(tmp_path)

    # ===

    proto_code_dir_abs_path = (
        ref_root_abs_path / ConfConstInput.default_proto_conf_dir_rel_path
    )
    proto_kernel_abs_path = create_plain_proto_code(proto_code_dir_abs_path)
    create_conf_primer_file(
        ref_root_abs_path,
        proto_code_dir_abs_path,
    )

    # ===

    project_dir_abs_path = ref_root_abs_path / test_pyproject_src_dir_rel_path
    create_test_pyproject_toml(project_dir_abs_path, ["pre-commit"])

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

    bootstrap_env_script_abs_path = ref_root_abs_path / "bootstrap_env"
    bootstrap_env_script_content = generate_entry_script_content(
        RunMode.mode_prime.value,
        str(proto_kernel_abs_path),
        str(bootstrap_env_script_abs_path),
        f"{cmd_bootstrap_env.__name__}",
        f"{custom_main.__name__}",
    )
    with open(bootstrap_env_script_abs_path, "w") as f:
        f.write(bootstrap_env_script_content)
    bootstrap_env_script_abs_path.chmod(
        bootstrap_env_script_abs_path.stat().st_mode | stat.S_IEXEC
    )

    # ===

    conf_client_dir_abs_path = conf_client_dir_abs_path.parent

    pre_commit_config_content = """
    repos:
    -   repo: https://github.com/pre-commit/pre-commit-hooks
        rev: v4.5.0
        hooks:
        -   id: trailing-whitespace
    """
    with open(conf_client_dir_abs_path / "pre_commit.yaml", "w") as f:
        f.write(pre_commit_config_content)

    # ===

    subprocess.run(
        [
            "git",
            "init",
        ],
        check=True,
        cwd=ref_root_abs_path,
    )
    subprocess.run(
        [
            "git",
            "config",
            "user.name",
            f"{test_bootstrap_env.__name__}",
        ],
        check=True,
        cwd=ref_root_abs_path,
    )
    subprocess.run(
        [
            "git",
            "config",
            "user.email",
            f"{test_bootstrap_env.__name__}@example.com",
        ],
        check=True,
        cwd=ref_root_abs_path,
    )
    subprocess.run(
        [
            "git",
            "add",
            ".",
        ],
        check=True,
        cwd=ref_root_abs_path,
    )
    subprocess.run(
        [
            "git",
            "commit",
            "-m",
            "initial commit",
        ],
        check=True,
        cwd=ref_root_abs_path,
    )

    # when:
    get_command_code("./bootstrap_env")

    # then:
    venv_dir = ref_root_abs_path / ConfConstEnv.default_dir_rel_path_venv
    pre_commit_executable = venv_dir / "bin" / "pre-commit"
    assert pre_commit_executable.exists()
