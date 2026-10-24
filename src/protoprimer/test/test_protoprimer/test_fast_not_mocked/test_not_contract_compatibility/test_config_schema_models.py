"""
Tests of the `local_config_schema` models themselves (not a contract test):
a new field passes, a wrong type fails.

FT_78_72_23_04.backward_compatibility.md
"""

import pytest

from local_test.case_condition import requires_max_python
from local_test.name_assertion import assert_test_module_name_embeds_str


def test_relationship():
    assert_test_module_name_embeds_str("config_schema_models")


@requires_max_python
def test_extra_fields_are_ignored():
    from local_config_schema.schema import ConfClient

    conf_data = {
        "required_python_version": "3.14.0",
        "brand_new_field": "x",
        "project_descriptors": [{"build_root_dir_rel_path": "a", "brand_new_nested_field": 1}],
    }
    assert ConfClient.model_validate(conf_data).required_python_version == "3.14.0"


@requires_max_python
def test_wrong_type_fails():
    from pydantic import ValidationError

    from local_config_schema.schema import ConfClient

    with pytest.raises(ValidationError):
        ConfClient.model_validate({"project_descriptors": "not_a_list"})
