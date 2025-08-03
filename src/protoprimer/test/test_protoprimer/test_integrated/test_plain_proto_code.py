import os
import pathlib
from os.path import basename

import pytest

import protoprimer
from local_repo.sub_proc_util import (
    get_command_code,
    get_command_output,
)
from local_test.toml_handler import save_toml_data
from protoprimer.primer_kernel import (
    ConfConstClient,
    ConfConstInput,
    ConfConstPrimer,
    ConfDst,
    ConfField,
    ValueName,
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


# TODO: Fix this stest to be run-able in CI:
@pytest.mark.skipif(IS_CI, reason="TODO: Fix this stest to be run-able in CI.")
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
                f"protoprimer @ file:{protoprimer_project_dir}",
            ],
        }
    }
    save_toml_data(tmp_path / "pyproject" / "pyproject.toml", toml_data)

    json_data = {
        ConfField.field_env_project_rel_path_to_extras_dict.value: {
            "pyproject": [],
        }
    }
    write_json_file(
        tmp_path / ConfConstClient.default_file_basename_leap_env,
        json_data,
    )

    # when:

    # TODO: This is not how it is supposed to work.
    #       Instead of running bootstrap/prime directly with missing values passed as args,
    #       create a wizard collecting that info from user and capturing it inside config files.
    get_command_code(" ./primer_kernel.py --ref_root_dir . --local_env_dir . ")

    # then:

    gconf_dir = tmp_path / ConfDst.dst_global.value
    lconf_dir = tmp_path / ConfDst.dst_local.value

    conf_primer_file = tmp_path / ConfConstInput.default_file_basename_conf_proto
    conf_client_file = tmp_path / ConfConstPrimer.default_client_conf_file_rel_path
    conf_env_file = tmp_path / ConfConstClient.default_file_basename_leap_env

    assert os.path.isdir(gconf_dir) and not os.path.islink(gconf_dir)
    assert os.path.isdir(lconf_dir) and os.path.islink(lconf_dir)

    assert os.path.isfile(conf_primer_file)
    assert os.path.isfile(conf_client_file)
    assert os.path.isfile(conf_env_file)
