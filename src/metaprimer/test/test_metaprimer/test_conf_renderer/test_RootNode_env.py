from __future__ import annotations

from local_test.integrated_helper import test_python_version
from local_test.name_assertion import assert_test_module_name_embeds_str
from metaprimer.conf_renderer import (
    RenderConfigVisitor,
    RootNode_env,
)
from protoprimer.primer_kernel import (
    ConfField,
    _TermColor,
)


def test_relationship():
    assert_test_module_name_embeds_str(RootNode_env.__name__)


def test_render_env_config_data_with_unused_fields():
    state_input_proto_conf_env_file_abs_path_eval_finalized = "/abs/path/to/file.json"

    config_data = {
        ConfField.field_required_python_version.value: test_python_version,
        ConfField.field_project_descriptors.value: [
            {
                ConfField.field_build_root_dir_rel_path.value: "src/test_project",
                ConfField.field_install_extras.value: [
                    "test",
                ],
                "whatever_test": [
                    7,
                ],
            },
        ],
        "whatever_test": 5,
    }

    root_node = RootNode_env(
        node_indent=0,
        orig_data=config_data,
        state_local_conf_file_abs_path_inited=state_input_proto_conf_env_file_abs_path_eval_finalized,
    )

    expected_output = f"""
{_TermColor.config_comment.value}# The `leap_env` data is loaded from the [/abs/path/to/file.json] file.{_TermColor.reset_style.value}
leap_env = (
    \n\
    {{
        \n\
        {_TermColor.config_comment.value}# This local environment-specific field overrides the global one (see description in `leap_client`).{_TermColor.reset_style.value}
        "required_python_version": "{test_python_version}",
        \n\
        {_TermColor.config_missing.value}# This local environment-specific field overrides the global one (see description in `leap_client`).{_TermColor.reset_style.value}
        {_TermColor.config_missing.value}# "python_selector_file_rel_path": None,{_TermColor.reset_style.value}
        \n\
        {_TermColor.config_missing.value}# This local environment-specific field overrides the global one (see description in `leap_client`).{_TermColor.reset_style.value}
        {_TermColor.config_missing.value}# "local_venv_dir_rel_path": None,{_TermColor.reset_style.value}
        \n\
        {_TermColor.config_missing.value}# This local environment-specific field overrides the global one (see description in `leap_client`).{_TermColor.reset_style.value}
        {_TermColor.config_missing.value}# "local_log_dir_rel_path": None,{_TermColor.reset_style.value}
        \n\
        {_TermColor.config_missing.value}# This local environment-specific field overrides the global one (see description in `leap_client`).{_TermColor.reset_style.value}
        {_TermColor.config_missing.value}# "local_tmp_dir_rel_path": None,{_TermColor.reset_style.value}
        \n\
        {_TermColor.config_missing.value}# This local environment-specific field overrides the global one (see description in `leap_client`).{_TermColor.reset_style.value}
        {_TermColor.config_missing.value}# "local_cache_dir_rel_path": None,{_TermColor.reset_style.value}
        \n\
        {_TermColor.config_missing.value}# This local environment-specific field overrides the global one (see description in `leap_client`).{_TermColor.reset_style.value}
        {_TermColor.config_missing.value}# "venv_driver": None,{_TermColor.reset_style.value}
        \n\
        {_TermColor.config_comment.value}# This local environment-specific field overrides the global one (see description in `leap_client`).{_TermColor.reset_style.value}
        "{ConfField.field_project_descriptors.value}": [
            \n\
            {{
                \n\
                "build_root_dir_rel_path": "src/test_project",
                \n\
                "install_extras": [
                    \n\
                    "test",
                ],
                \n\
                {_TermColor.config_unused.value}# This `list` is not used by the `protoprimer`.{_TermColor.reset_style.value}
                "whatever_test": [
                    \n\
                    7,
                ],
            }},
        ],
        \n\
        {_TermColor.config_unused.value}# This value is not used by the `protoprimer`.{_TermColor.reset_style.value}
        "whatever_test": 5,
    }}
)\
"""
    assert RenderConfigVisitor().render_node(root_node) == expected_output


def test_render_empty_env_config_data():
    state_input_proto_conf_env_file_abs_path_eval_finalized = "/abs/path/to/file.json"

    config_data = {}

    root_node = RootNode_env(
        node_indent=0,
        orig_data=config_data,
        state_local_conf_file_abs_path_inited=state_input_proto_conf_env_file_abs_path_eval_finalized,
    )

    expected_output = f"""
{_TermColor.config_comment.value}# The `leap_env` data is loaded from the [/abs/path/to/file.json] file.{_TermColor.reset_style.value}
leap_env = (
    \n\
    {{
        \n\
        {_TermColor.config_missing.value}# This local environment-specific field overrides the global one (see description in `leap_client`).{_TermColor.reset_style.value}
        {_TermColor.config_missing.value}# "required_python_version": None,{_TermColor.reset_style.value}
        \n\
        {_TermColor.config_missing.value}# This local environment-specific field overrides the global one (see description in `leap_client`).{_TermColor.reset_style.value}
        {_TermColor.config_missing.value}# "python_selector_file_rel_path": None,{_TermColor.reset_style.value}
        \n\
        {_TermColor.config_missing.value}# This local environment-specific field overrides the global one (see description in `leap_client`).{_TermColor.reset_style.value}
        {_TermColor.config_missing.value}# "local_venv_dir_rel_path": None,{_TermColor.reset_style.value}
        \n\
        {_TermColor.config_missing.value}# This local environment-specific field overrides the global one (see description in `leap_client`).{_TermColor.reset_style.value}
        {_TermColor.config_missing.value}# "local_log_dir_rel_path": None,{_TermColor.reset_style.value}
        \n\
        {_TermColor.config_missing.value}# This local environment-specific field overrides the global one (see description in `leap_client`).{_TermColor.reset_style.value}
        {_TermColor.config_missing.value}# "local_tmp_dir_rel_path": None,{_TermColor.reset_style.value}
        \n\
        {_TermColor.config_missing.value}# This local environment-specific field overrides the global one (see description in `leap_client`).{_TermColor.reset_style.value}
        {_TermColor.config_missing.value}# "local_cache_dir_rel_path": None,{_TermColor.reset_style.value}
        \n\
        {_TermColor.config_missing.value}# This local environment-specific field overrides the global one (see description in `leap_client`).{_TermColor.reset_style.value}
        {_TermColor.config_missing.value}# "venv_driver": None,{_TermColor.reset_style.value}
        \n\
        {_TermColor.config_missing.value}# This local environment-specific field overrides the global one (see description in `leap_client`).{_TermColor.reset_style.value}
        {_TermColor.config_missing.value}# "project_descriptors": [{_TermColor.reset_style.value}
        {_TermColor.config_missing.value}# ],{_TermColor.reset_style.value}
    }}
)\
"""
    assert RenderConfigVisitor().render_node(root_node) == expected_output


def test_render_env_config_data_with_unused_fields_quiet():
    state_input_proto_conf_env_file_abs_path_eval_finalized = "/abs/path/to/file.json"

    config_data = {
        ConfField.field_required_python_version.value: test_python_version,
        ConfField.field_project_descriptors.value: [
            {
                ConfField.field_build_root_dir_rel_path.value: "src/test_project",
                ConfField.field_install_extras.value: [
                    "test",
                ],
                "whatever_test": [
                    7,
                ],
            },
        ],
        "whatever_test": 5,
    }

    root_node = RootNode_env(
        node_indent=0,
        orig_data=config_data,
        state_local_conf_file_abs_path_inited=state_input_proto_conf_env_file_abs_path_eval_finalized,
    )

    expected_output = f"""\
leap_env = (
    {{
        "required_python_version": "{test_python_version}",
        "project_descriptors": [
            {{
                "build_root_dir_rel_path": "src/test_project",
                "install_extras": [
                    "test",
                ],
                "whatever_test": [
                    7,
                ],
            }},
        ],
        "whatever_test": 5,
    }}
)\
"""
    assert RenderConfigVisitor(is_quiet=True).render_node(root_node) == expected_output
