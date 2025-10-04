import pathlib
import shutil
import os

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
    ConfConstPrimer,
    ConfConstEnv,
    ConfConstInput,
    SyntaxArg,
)


def test_env_selection(tmp_path: pathlib.Path):

    # given:

    ref_root_abs_path = switch_to_ref_root_abs_path(tmp_path)

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

    default_env_dir_name = "default_env"
    default_env_dir_abs_path = ref_root_abs_path / default_env_dir_name
    default_venv_rel_path = "venv_default"
    create_conf_env_file(
        ref_root_abs_path,
        default_env_dir_abs_path,
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

    # === create `ConfLeap.leap_client`

    conf_client_dir_abs_path = (
        ref_root_abs_path / ConfConstPrimer.default_client_conf_dir_rel_path
    )
    create_conf_client_file(
        ref_root_abs_path,
        conf_client_dir_abs_path,
        default_env_dir_abs_path,
    )

    # when:
    # bootstrap with `default_env`

    get_command_code("./proto_code/proto_kernel.py")

    # then:
    # assert `default_env` created

    default_venv_abs_path = ref_root_abs_path / default_venv_rel_path
    special_venv_abs_path = ref_root_abs_path / special_venv_rel_path
    assert default_venv_abs_path.exists()
    assert not special_venv_abs_path.exists()

    # clean:
    # remove `default_env`

    shutil.rmtree(default_venv_abs_path)
    os.remove(
        ref_root_abs_path / ConfConstClient.default_dir_rel_path_leap_env_link_name
    )

    # when:
    # bootstrap with `special_env`

    get_command_code(
        f"./proto_code/proto_kernel.py {SyntaxArg.arg_env} {special_env_dir_name}"
    )

    # then:

    assert not default_venv_abs_path.exists()
    assert special_venv_abs_path.exists()
