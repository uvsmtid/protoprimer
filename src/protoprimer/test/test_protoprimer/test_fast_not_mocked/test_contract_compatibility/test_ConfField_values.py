"""
Config field names (written into and read from config files) are frozen: a rename is a break
which the schema check (`test_config_schema.py`) cannot see for fields it never writes.

FT_78_72_23_04.backward_compatibility.md
"""

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import ConfField

# The config field names are frozen here: they can be added, but must not be removed or renamed:
frozen_conf_field_values = [
    "ref_root_dir_rel_path",
    "global_conf_dir_rel_path",
    "local_conf_symlink_rel_path",
    "default_env_dir_rel_path",
    "required_python_version",
    "python_selector_file_rel_path",
    "local_venv_dir_rel_path",
    "local_log_dir_rel_path",
    "local_run_dir_rel_path",
    "local_tmp_dir_rel_path",
    "local_cache_dir_rel_path",
    "venv_driver",
    "version_constraints_file_basename",
    "project_descriptors",
    "install_specs",
    "build_root_dir_rel_path",
    "install_extras",
    "install_group",
    "extra_command_args",
]


def test_relationship():
    assert_test_module_name_embeds_str(
        ConfField.__name__,
    )


@pytest.mark.parametrize("frozen_conf_field_value", frozen_conf_field_values)
def test_frozen_conf_field_value_exists(frozen_conf_field_value):

    # given:
    current_conf_field_values = {conf_field.value for conf_field in ConfField}

    # then:
    assert frozen_conf_field_value in current_conf_field_values
