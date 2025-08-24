import os
import pathlib

import protoprimer
from local_repo.sub_proc_util import (
    get_command_code,
    get_command_output,
)
from local_test.toml_handler import save_toml_data
from protoprimer.primer_kernel import (
    ConfConstClient,
    ConfConstEnv,
    ConfConstInput,
    ConfConstPrimer,
    ConfDst,
    ConfField,
    write_json_file,
)
from test_protoprimer.test_integrated.integrated_helper import (
    switch_to_test_dir_with_plain_proto_code,
)

IS_CI = os.getenv("CI") == "true"


def test_help(tmp_path: pathlib.Path):

    # given:

    switch_to_test_dir_with_plain_proto_code(tmp_path)

    # when:

    help_output = get_command_output("./primer_kernel.py --help")

    # then:

    assert "usage: primer_kernel.py" in help_output


def test_prime(tmp_path: pathlib.Path):

    # given:

    switch_to_test_dir_with_plain_proto_code(tmp_path)

    os.mkdir(tmp_path / "pyproject")

    protoprimer_project_dir = pathlib.Path(protoprimer.__file__).parent.parent.parent

    toml_data = {
        "project": {
            "name": "whatever",
            "version": "0.0.0.dev0",
            "dependencies": [
                # Install `protoprimer` from local sources:
                f"protoprimer @ file://{protoprimer_project_dir}",
            ],
        }
    }

    # TODO: Figure out how can minimal layout be achieved (when `pyproject.toml` is in the ref root)?
    save_toml_data(
        str(tmp_path / "pyproject" / "pyproject.toml"),
        toml_data,
    )

    # ===

    prime_conf_data = {
        ConfField.field_primer_ref_root_dir_rel_path.value: ".",
        ConfField.field_primer_conf_client_file_rel_path.value: ConfConstPrimer.default_client_conf_file_rel_path,
    }
    write_json_file(
        str(tmp_path / ConfConstInput.default_file_basename_conf_primer),
        prime_conf_data,
    )

    # ===

    client_conf_data = {
        ConfField.field_client_link_name_dir_rel_path.value: ConfConstClient.default_dir_rel_path_leap_env_link_name,
        ConfField.field_client_default_target_dir_rel_path.value: ConfConstClient.default_client_default_target_dir_rel_path,
    }
    os.makedirs(
        os.path.dirname(tmp_path / ConfConstPrimer.default_client_conf_file_rel_path)
    )
    write_json_file(
        str(tmp_path / ConfConstPrimer.default_client_conf_file_rel_path),
        client_conf_data,
    )

    # ===

    env_conf_data = {
        ConfField.field_env_local_python_file_abs_path.value: ConfConstEnv.default_file_abs_path_python,
        ConfField.field_env_local_venv_dir_rel_path.value: ConfConstEnv.default_dir_rel_path_venv,
        ConfField.field_env_project_descriptors.value: [
            {
                ConfField.field_env_build_root_dir_rel_path.value: "pyproject",
                ConfField.field_env_install_extras.value: [],
            },
        ],
    }
    write_json_file(
        str(tmp_path / ConfConstClient.default_file_basename_leap_env),
        env_conf_data,
    )

    # ===

    # when:

    # TODO: This is not how it is supposed to work.
    #       Instead of running bootstrap/prime directly with missing values passed as args,
    #       create a wizard collecting that info from user and capturing it inside config files.
    get_command_code(" ./primer_kernel.py ")

    # then:

    gconf_dir = tmp_path / ConfDst.dst_global.value
    lconf_dir = tmp_path / ConfDst.dst_local.value

    # TODO: Unify names for default conf files:
    conf_primer_file = tmp_path / ConfConstInput.default_file_basename_conf_primer
    conf_client_file = tmp_path / ConfConstPrimer.default_client_conf_file_rel_path
    conf_env_file = tmp_path / ConfConstClient.default_file_basename_leap_env

    assert os.path.isdir(gconf_dir) and not os.path.islink(gconf_dir)
    assert os.path.isdir(lconf_dir) and os.path.islink(lconf_dir)

    assert os.path.isfile(conf_primer_file)
    assert os.path.isfile(conf_client_file)
    assert os.path.isfile(conf_env_file)
