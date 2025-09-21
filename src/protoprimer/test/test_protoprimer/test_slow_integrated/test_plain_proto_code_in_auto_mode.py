import os
import pathlib

from local_repo.sub_proc_util import (
    get_command_code,
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
from protoprimer.primer_kernel import (
    ConfConstClient,
    ConfConstGeneral,
    ConfConstInput,
    ConfConstPrimer,
    ConfDst,
)

IS_CI = os.getenv("CI") == "true"


def test_prime(tmp_path: pathlib.Path):

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

    # TODO: Figure out how can minimal layout be achieved (when `pyproject.toml` is in the ref root)?
    project_dir_abs_path = ref_root_abs_path / test_pyproject_src_dir_rel_path
    create_test_pyproject_toml(project_dir_abs_path)

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

    # when:

    # TODO: This is not how it is supposed to work.
    #       Instead of running bootstrap/prime directly with missing values passed as args,
    #       create a wizard collecting that info from user and capturing it inside config files.
    get_command_code(" ./proto_code/proto_kernel.py ")

    # then:

    gconf_dir = ref_root_abs_path / ConfDst.dst_global.value
    lconf_dir = ref_root_abs_path / ConfDst.dst_local.value

    # TODO: Unify names for default conf files:
    conf_primer_file = (
        ref_root_abs_path
        / ConfConstGeneral.name_proto_code
        / ConfConstInput.default_file_basename_conf_primer
    )
    conf_client_file = (
        ref_root_abs_path / ConfConstPrimer.default_client_conf_file_rel_path
    )
    conf_env_file = ref_root_abs_path / ConfConstClient.default_env_conf_file_rel_path

    assert os.path.isdir(gconf_dir) and not os.path.islink(gconf_dir)
    assert os.path.isdir(lconf_dir) and os.path.islink(lconf_dir)

    assert os.path.isfile(conf_primer_file)
    assert os.path.isfile(conf_client_file)
    assert os.path.isfile(conf_env_file)
