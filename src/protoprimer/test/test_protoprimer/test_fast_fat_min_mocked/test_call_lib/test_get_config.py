import os

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from local_test.repo_tree import change_to_known_repo_path
from protoprimer.primer_kernel import (
    ConfField,
    ConfLeap,
    EnvState,
    VenvDriverType,
    get_config,
)

_lconf_expected_target = "dst/default_env"


def test_relationship():
    assert_test_module_name_embeds_str(get_config.__name__)


@pytest.fixture
def proto_kernel_abs_path():
    with change_to_known_repo_path("."):
        if not os.path.islink("./lconf") or os.readlink("./lconf") != _lconf_expected_target:
            pytest.skip(f"`./lconf` does not point to {_lconf_expected_target}")
        yield os.path.abspath("./cmd/proto_code/proto_kernel.py")


def test_get_config_with_leap_primer(proto_kernel_abs_path):

    # given:

    # when:

    conf_data = get_config(proto_kernel_abs_path, ConfLeap.leap_primer)

    # then:

    assert conf_data[ConfField.field_ref_root_dir_rel_path.value] == "../.."

    assert conf_data[ConfField.field_global_conf_dir_rel_path.value] == "gconf"


def test_get_config_with_leap_client(proto_kernel_abs_path):

    # given:

    # when:

    conf_data = get_config(proto_kernel_abs_path, ConfLeap.leap_client)

    # then:

    assert conf_data[ConfField.field_local_conf_symlink_rel_path.value] == "lconf"

    assert conf_data[ConfField.field_default_env_dir_rel_path.value] == "dst/default_env"

    assert conf_data[ConfField.field_required_python_version.value] == "3.14.0"

    assert conf_data[ConfField.field_python_selector_file_rel_path.value] == "cmd/proto_code/python_selector_same.py"

    assert conf_data[ConfField.field_venv_driver.value] == "venv_uv"

    assert conf_data[ConfField.field_local_venv_dir_rel_path.value] == "venv"

    assert conf_data[ConfField.field_local_log_dir_rel_path.value] == "log"

    assert conf_data[ConfField.field_local_tmp_dir_rel_path.value] == "tmp"

    assert conf_data[ConfField.field_project_descriptors.value] == [
        {
            ConfField.field_build_root_dir_rel_path.value: "src/local_auth",
            ConfField.field_install_extras.value: [],
            ConfField.field_install_group.value: "install_auth",
        },
        {
            ConfField.field_build_root_dir_rel_path.value: "src/local_doc",
            ConfField.field_install_extras.value: [],
            ConfField.field_install_group.value: "install_main",
        },
        {
            ConfField.field_build_root_dir_rel_path.value: "src/local_repo",
            ConfField.field_install_extras.value: [],
            ConfField.field_install_group.value: "install_main",
        },
        {
            ConfField.field_build_root_dir_rel_path.value: "src/local_test",
            ConfField.field_install_extras.value: [],
            ConfField.field_install_group.value: "install_main",
        },
        {
            ConfField.field_build_root_dir_rel_path.value: "src/metaprimer",
            ConfField.field_install_extras.value: [],
            ConfField.field_install_group.value: "install_main",
        },
        {
            ConfField.field_build_root_dir_rel_path.value: "src/protoprimer",
            ConfField.field_install_extras.value: ["test"],
            ConfField.field_install_group.value: "install_main",
        },
    ]

    assert conf_data[ConfField.field_install_specs.value] == [
        {
            "install_auth": {
                ConfField.field_extra_command_args.value: [],
            },
        },
        {
            "install_main": {
                ConfField.field_extra_command_args.value: [],
            },
        },
    ]


def test_get_config_with_leap_env(proto_kernel_abs_path):

    # given:

    # when:

    conf_data = get_config(proto_kernel_abs_path, ConfLeap.leap_env)

    # then:

    assert conf_data[ConfField.field_python_selector_file_rel_path.value] == "cmd/proto_code/python_selector_py.py"


def test_get_config_with_leap_derived(proto_kernel_abs_path):

    # given:

    # when:

    conf_data = get_config(proto_kernel_abs_path, ConfLeap.leap_derived)

    # then:

    assert conf_data.keys() == {
        EnvState.state_proto_code_file_abs_path_inited.name,
        EnvState.state_primer_conf_file_abs_path_inited.name,
        EnvState.state_ref_root_dir_abs_path_inited.name,
        EnvState.state_global_conf_dir_abs_path_inited.name,
        EnvState.state_global_conf_file_abs_path_inited.name,
        EnvState.state_selected_env_dir_rel_path_inited.name,
        EnvState.state_local_conf_symlink_abs_path_inited.name,
        EnvState.state_local_conf_file_abs_path_inited.name,
        EnvState.state_required_python_version_inited.name,
        EnvState.state_selected_python_file_abs_path_inited.name,
        EnvState.state_local_venv_dir_abs_path_inited.name,
        EnvState.state_local_log_dir_abs_path_inited.name,
        EnvState.state_local_tmp_dir_abs_path_inited.name,
        EnvState.state_local_cache_dir_abs_path_inited.name,
        EnvState.state_venv_driver_inited.name,
        EnvState.state_project_descriptors_inited.name,
    }

    assert conf_data[EnvState.state_selected_env_dir_rel_path_inited.name] == "dst/default_env"

    assert conf_data[EnvState.state_required_python_version_inited.name] == "3.14.0"

    assert conf_data[EnvState.state_venv_driver_inited.name] == VenvDriverType.venv_uv.name

    assert conf_data[EnvState.state_project_descriptors_inited.name] == [
        {
            ConfField.field_build_root_dir_rel_path.value: "src/local_auth",
            ConfField.field_install_extras.value: [],
            ConfField.field_install_group.value: "install_auth",
        },
        {
            ConfField.field_build_root_dir_rel_path.value: "src/local_doc",
            ConfField.field_install_extras.value: [],
            ConfField.field_install_group.value: "install_main",
        },
        {
            ConfField.field_build_root_dir_rel_path.value: "src/local_repo",
            ConfField.field_install_extras.value: [],
            ConfField.field_install_group.value: "install_main",
        },
        {
            ConfField.field_build_root_dir_rel_path.value: "src/local_test",
            ConfField.field_install_extras.value: [],
            ConfField.field_install_group.value: "install_main",
        },
        {
            ConfField.field_build_root_dir_rel_path.value: "src/metaprimer",
            ConfField.field_install_extras.value: [],
            ConfField.field_install_group.value: "install_main",
        },
        {
            ConfField.field_build_root_dir_rel_path.value: "src/protoprimer",
            ConfField.field_install_extras.value: ["test"],
            ConfField.field_install_group.value: "install_main",
        },
    ]
