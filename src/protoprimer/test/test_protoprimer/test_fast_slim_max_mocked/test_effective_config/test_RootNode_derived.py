from __future__ import annotations

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    ConfField,
    RenderConfigVisitor,
    RootNode_derived,
    TermColor,
    EnvState,
)


def test_relationship():
    assert_test_module_name_embeds_str(RootNode_derived.__name__)


def test_render_derived_config_data_with_unused_fields():

    config_data = {
        EnvState.state_derived_project_descriptors_eval_finalized.name: [
            {
                ConfField.field_build_root_dir_rel_path.value: "src/test_project",
                ConfField.field_install_extras.value: [
                    "test",
                ],
            },
        ],
        EnvState.state_input_proto_code_file_abs_path_eval_finalized.name: "/abs/path/to/proto.py",
        "whatever_test": 5,
    }

    root_node = RootNode_derived(
        node_indent=0,
        orig_data=config_data,
    )

    expected_output = f"""
{TermColor.config_comment.value}# The `leap_derived` data is derived from other data - it is computed by:{TermColor.reset_style.value}
{TermColor.config_comment.value}# *   applying defaults to missing field values{TermColor.reset_style.value}
{TermColor.config_comment.value}# *   combining with other field values{TermColor.reset_style.value}
{TermColor.config_comment.value}# Effectively, this is what ultimately used by the `protoprimer`.{TermColor.reset_style.value}
leap_derived = (
    \n\
    {{
        \n\
        {TermColor.config_comment.value}# This value is derived from `state_input_proto_code_file_abs_path_eval_finalized` - see description in `leap_input`.{TermColor.reset_style.value}
        "{EnvState.state_input_proto_code_file_abs_path_eval_finalized.name}": "/abs/path/to/proto.py",
        \n\
        {TermColor.config_missing.value}# This value is derived from `state_input_proto_conf_primer_file_abs_path_eval_finalized` - see description in `leap_input`.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "state_input_proto_conf_primer_file_abs_path_eval_finalized": None,{TermColor.reset_style.value}
        \n\
        {TermColor.config_missing.value}# This value is derived from `primer_ref_root_dir_rel_path` - see description in `leap_primer`.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "state_primer_ref_root_dir_abs_path_eval_finalized": None,{TermColor.reset_style.value}
        \n\
        {TermColor.config_missing.value}# This value is derived from `primer_conf_client_dir_rel_path` - see description in `leap_primer`.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "state_primer_conf_client_dir_abs_path_eval_finalized": None,{TermColor.reset_style.value}
        \n\
        {TermColor.config_missing.value}# This value is derived from `state_input_proto_conf_primer_file_abs_path_eval_finalized` - see description in `leap_input`.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "state_primer_conf_client_file_abs_path_eval_finalized": None,{TermColor.reset_style.value}
        \n\
        {TermColor.config_missing.value}# This value is derived from `client_default_env_dir_rel_path` - see description in `leap_client`.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "state_client_local_env_conf_dir_rel_path_eval_finalized": None,{TermColor.reset_style.value}
        \n\
        {TermColor.config_missing.value}# This value is derived from `client_link_name_dir_rel_path` - see description in `leap_client`.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "state_client_conf_env_dir_abs_path_eval_finalized": None,{TermColor.reset_style.value}
        \n\
        {TermColor.config_missing.value}# This value is derived from `state_input_proto_conf_primer_file_abs_path_eval_finalized` - see description in `leap_input`.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "state_client_conf_env_file_abs_path_eval_finalized": None,{TermColor.reset_style.value}
        \n\
        {TermColor.config_missing.value}# This value is derived from `required_python_file_abs_path` in `leap_client` (override-able in `leap_env`) - see description there.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "state_derived_required_python_file_abs_path_eval_finalized": None,{TermColor.reset_style.value}
        \n\
        {TermColor.config_missing.value}# This value is derived from `local_venv_dir_rel_path` in `leap_client` (override-able in `leap_env`) - see description there.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "state_derived_local_venv_dir_abs_path_eval_finalized": None,{TermColor.reset_style.value}
        \n\
        {TermColor.config_missing.value}# This value is derived from `local_log_dir_rel_path` in `leap_client` (override-able in `leap_env`) - see description there.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "state_derived_local_log_dir_abs_path_eval_finalized": None,{TermColor.reset_style.value}
        \n\
        {TermColor.config_missing.value}# This value is derived from `local_tmp_dir_rel_path` in `leap_client` (override-able in `leap_env`) - see description there.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "state_derived_local_tmp_dir_abs_path_eval_finalized": None,{TermColor.reset_style.value}
        \n\
        {TermColor.config_missing.value}# This value is derived from `local_cache_dir_rel_path` in `leap_client` (override-able in `leap_env`) - see description there.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "state_derived_local_cache_dir_abs_path_eval_finalized": None,{TermColor.reset_style.value}
        \n\
        {TermColor.config_missing.value}# This value is derived from `package_driver` in `leap_client` (override-able in `leap_env`) - see description there.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "state_derived_package_driver_eval_finalized": None,{TermColor.reset_style.value}
        \n\
        {TermColor.config_comment.value}# This value is derived from `project_descriptors` in `leap_client` (override-able in `leap_env`) - see description there.{TermColor.reset_style.value}
        "{EnvState.state_derived_project_descriptors_eval_finalized.name}": [
            \n\
            {{
                \n\
                {TermColor.config_comment.value}# This is similar to specifying the dir of `pyproject.toml` for `pip`:{TermColor.reset_style.value}
                {TermColor.config_comment.value}# pip install path/to/project{TermColor.reset_style.value}
                {TermColor.config_comment.value}# The path is relative to the `ref_root` dir specified in the `primer_ref_root_dir_rel_path` field.{TermColor.reset_style.value}
                "{ConfField.field_build_root_dir_rel_path.value}": "src/test_project",
                \n\
                {TermColor.config_comment.value}# This is similar to specifying a list of `extra_item`-s per `path/to/project` for `pip`:{TermColor.reset_style.value}
                {TermColor.config_comment.value}# pip install path/to/project[extra_item_1,extra_item_2,...]{TermColor.reset_style.value}
                "{ConfField.field_install_extras.value}": [
                    \n\
                    "test",
                ],
            }},
        ],
        \n\
        {TermColor.config_unused.value}# This value is not used by the `protoprimer`.{TermColor.reset_style.value}
        "whatever_test": 5,
    }}
)\
"""
    assert RenderConfigVisitor().render_node(root_node) == expected_output
