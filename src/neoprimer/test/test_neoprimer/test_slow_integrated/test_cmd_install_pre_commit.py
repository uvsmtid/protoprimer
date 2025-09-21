import pathlib
import stat

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
)


def test_install_pre_commit(tmp_path: pathlib.Path):

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
    create_test_pyproject_toml(project_dir_abs_path, ["pre-commit"])

    # ===

    conf_env_dir_abs_path = (
        ref_root_abs_path / ConfConstClient.default_client_default_env_dir_rel_path
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
    )

    # ===

    install_pre_commit_script_content = """#!/usr/bin/env python3

if __name__ == "__main__":

    proto_kernel_rel_path = "./proto_code/proto_kernel.py"

    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    # Boilerplate to import `proto_kernel` from `protoprimer`
    import os
    import sys

    # Import `proto_kernel` from `./proto_code` dir relative to curr file:
    sys.path.append(
        os.path.join(
            os.path.dirname(__file__),
            os.path.dirname(proto_kernel_rel_path),
        ),
    )
    import proto_kernel

    sys.path.pop()
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    proto_kernel.run_main(
        "neoprimer.cmd_install_pre_commit",
        "custom_main",
    )
"""
    install_pre_commit_script_path = ref_root_abs_path / "install_pre_commit"
    with open(install_pre_commit_script_path, "w") as f:
        f.write(install_pre_commit_script_content)
    install_pre_commit_script_path.chmod(
        install_pre_commit_script_path.stat().st_mode | stat.S_IEXEC
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

    # when:
    get_command_code("./install_pre_commit")

    # then:
    venv_dir = ref_root_abs_path / ConfConstEnv.default_dir_rel_path_venv
    pre_commit_executable = venv_dir / "bin" / "pre-commit"
    assert pre_commit_executable.exists()
