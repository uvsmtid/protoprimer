from __future__ import annotations

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    ConfField,
    RenderConfigVisitor,
    RootNode_primer,
    TermColor,
)


def test_relationship():
    assert_test_module_name_embeds_str(RootNode_primer.__name__)


def test_render_primer_config_data_with_unused_fields():

    state_input_proto_conf_primer_file_abs_path_eval_finalized = (
        "/abs/path/to/file.json"
    )

    config_data = {
        ConfField.field_primer_ref_root_dir_rel_path.value: "../..",
        ConfField.field_primer_conf_client_file_rel_path.value: "client.json",
        "whatever_test": 5,
    }

    root_node = RootNode_primer(
        0,
        config_data,
        state_input_proto_conf_primer_file_abs_path_eval_finalized,
    )

    expected_output = f"""
{TermColor.config_comment.value}# The data is loaded from the [/abs/path/to/file.json] file.{TermColor.reset_style.value}
leap_primer = (
    \n\
    {{
        \n\
        {TermColor.config_comment.value}# Field [primer_ref_root_dir_rel_path] (or [ref_root] for short) points to the client reference root dir.{TermColor.reset_style.value}
        {TermColor.config_comment.value}# Subsequently, the resolved client reference root dir [ref_root] is used as a base path for the most of the configured relative paths.{TermColor.reset_style.value}
        {TermColor.config_comment.value}# The specified path is relative to dir [/abs/path/to].{TermColor.reset_style.value}
        "primer_ref_root_dir_rel_path": "../..",
        \n\
        {TermColor.config_comment.value}# Field [primer_conf_client_file_rel_path] (or [conf_client] for short) leads to the client global config file.{TermColor.reset_style.value}
        {TermColor.config_comment.value}# The path is relative to the dir specified in the [primer_ref_root_dir_rel_path] field.{TermColor.reset_style.value}
        "primer_conf_client_file_rel_path": "client.json",
        \n\
        {TermColor.config_unused.value}# This value is not used by the `protoprimer`.{TermColor.reset_style.value}
        "whatever_test": 5,
    }}
)\
"""
    assert RenderConfigVisitor().render_node(root_node) == expected_output


def test_render_empty_primer_config_data():
    state_input_proto_conf_primer_file_abs_path_eval_finalized = (
        "/abs/path/to/empty_file.json"
    )

    config_data = {}

    root_node = RootNode_primer(
        0,
        config_data,
        state_input_proto_conf_primer_file_abs_path_eval_finalized,
    )

    expected_output = f"""
{TermColor.config_comment.value}# The data is loaded from the [/abs/path/to/empty_file.json] file.{TermColor.reset_style.value}
leap_primer = (
    \n\
    {{
        \n\
        {TermColor.config_missing.value}# Field [primer_ref_root_dir_rel_path] (or [ref_root] for short) points to the client reference root dir.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# Subsequently, the resolved client reference root dir [ref_root] is used as a base path for the most of the configured relative paths.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# The specified path is relative to dir [/abs/path/to].{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "primer_ref_root_dir_rel_path": None,{TermColor.reset_style.value}
        \n\
        {TermColor.config_missing.value}# Field [primer_conf_client_file_rel_path] (or [conf_client] for short) leads to the client global config file.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# The path is relative to the dir specified in the [primer_ref_root_dir_rel_path] field.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "primer_conf_client_file_rel_path": None,{TermColor.reset_style.value}
    }}
)\
"""
    assert RenderConfigVisitor().render_node(root_node) == expected_output
