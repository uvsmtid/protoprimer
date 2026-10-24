"""
The configs written for the current `protoprimer` must validate against the schema of the tree this test belongs to.

Under `old_tests_on_new_changes` the schema (`local_config_schema`) and the helpers come from the baseline,
while the field names (`ConfField`) come from the current `protoprimer`: a new field is ignored by the old schema (not a break).

A renamed or removed field is detected by the frozen `ConfField` values (`test_ConfField_values.py`).

FT_78_72_23_04.backward_compatibility.md
"""

import json
import pathlib

import pytest

from local_test.case_condition import requires_max_python
from local_test.integrated_helper import (
    create_conf_client_file,
    create_conf_env_file,
    create_conf_primer_file,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    ConfConstClient,
    ConfConstInput,
    ConfConstPrimer,
    ConfLeap,
)


def test_relationship():
    assert_test_module_name_embeds_str("config_schema")


def create_conf_file(
    tmp_path: pathlib.Path,
    conf_leap: ConfLeap,
) -> dict:
    ref_root_abs_path = tmp_path / "ref_root"
    proto_kernel_dir_abs_path = ref_root_abs_path / "proto_code"
    conf_client_dir_abs_path = ref_root_abs_path / "gconf"
    conf_env_dir_abs_path = ref_root_abs_path / "dst" / "default_env"
    project_dir_abs_path = ref_root_abs_path / "src" / "some_project"
    for dir_abs_path in [proto_kernel_dir_abs_path, project_dir_abs_path]:
        dir_abs_path.mkdir(parents=True)

    if conf_leap is ConfLeap.leap_primer:
        create_conf_primer_file(ref_root_abs_path, proto_kernel_dir_abs_path)
        conf_file_abs_path = proto_kernel_dir_abs_path / ConfConstInput.default_file_basename_conf_primer
    elif conf_leap is ConfLeap.leap_client:
        create_conf_client_file(ref_root_abs_path, conf_client_dir_abs_path, conf_env_dir_abs_path, project_dir_abs_path)
        conf_file_abs_path = conf_client_dir_abs_path / ConfConstPrimer.default_file_basename_leap_client
    elif conf_leap is ConfLeap.leap_env:
        create_conf_env_file(
            ref_root_abs_path,
            conf_env_dir_abs_path,
            project_dir_abs_path,
            python_selector_rel_path=pathlib.Path("src/proto_code/python_selector_same.py"),
        )
        conf_file_abs_path = conf_env_dir_abs_path / ConfConstClient.default_file_basename_leap_env
    else:
        raise AssertionError(f"[{conf_leap}] has no config file")
    return json.loads(conf_file_abs_path.read_text())


@requires_max_python
@pytest.mark.parametrize(
    "conf_leap, model_name",
    [
        (ConfLeap.leap_primer, "ConfPrimer"),
        (ConfLeap.leap_client, "ConfClient"),
        (ConfLeap.leap_env, "ConfEnv"),
    ],
)
def test_conf_file_matches_schema(
    tmp_path: pathlib.Path,
    conf_leap: ConfLeap,
    model_name: str,
):

    # given:

    # `pydantic` requires newer `python` than min: import it only when the test runs.
    from local_config_schema import schema

    model_class = getattr(schema, model_name)
    conf_data = create_conf_file(tmp_path, conf_leap)

    # when:

    validated_conf = model_class.model_validate(conf_data)

    # then:

    assert isinstance(validated_conf, model_class)
