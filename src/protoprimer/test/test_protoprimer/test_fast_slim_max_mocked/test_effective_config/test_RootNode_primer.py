from __future__ import annotations

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    ConfConstPrimer,
    ConfField,
    RenderConfigVisitor,
    RootNode_primer,
    TermColor,
)


def test_relationship():
    assert_test_module_name_embeds_str(RootNode_primer.__name__)


def test_render_primer_config_data_with_unused_fields():

    state_primer_conf_file_abs_path_inited = "/abs/path/to/file.json"

    config_data = {
        ConfField.field_ref_root_dir_rel_path.value: "../..",
        ConfField.field_global_conf_dir_rel_path.value: ConfConstPrimer.default_client_conf_dir_rel_path,
        "whatever_test": 5,
    }

    root_node = RootNode_primer(
        node_indent=0,
        orig_data=config_data,
        state_primer_conf_file_abs_path_inited=state_primer_conf_file_abs_path_inited,
    )

    expected_output = f"""
{TermColor.config_comment.value}# The `leap_primer` data is loaded from the [/abs/path/to/file.json] file.{TermColor.reset_style.value}
leap_primer = (
    \n\
    {{
        \n\
        {TermColor.config_comment.value}# Field `ref_root_dir_rel_path` points to the dir called `ref_root`.{TermColor.reset_style.value}
        {TermColor.config_comment.value}# The path is relative to the `proto_code` file [/abs/path/to/file.json].{TermColor.reset_style.value}
        {TermColor.config_comment.value}# Normally, the `ref_root` dir is the client repo root, but it can be anything.{TermColor.reset_style.value}
        {TermColor.config_comment.value}# See `state_ref_root_dir_abs_path_inited` in `leap_derived` -{TermColor.reset_style.value}
        {TermColor.config_comment.value}# the derived abs path is the base path for all the configured relative paths (except for this field itself, obviously).{TermColor.reset_style.value}
        "ref_root_dir_rel_path": "../..",
        \n\
        {TermColor.config_comment.value}# Field `global_conf_dir_rel_path` points to the global config dir (as opposed to local config dir `local_conf_symlink_rel_path`).{TermColor.reset_style.value}
        {TermColor.config_comment.value}# The path is relative to the `ref_root` dir specified in the `ref_root_dir_rel_path` field.{TermColor.reset_style.value}
        {TermColor.config_comment.value}# See `state_global_conf_dir_abs_path_inited` in `leap_derived` -{TermColor.reset_style.value}
        {TermColor.config_comment.value}# normally, the resolved global config dir contains all other global client config files.{TermColor.reset_style.value}
        "global_conf_dir_rel_path": "gconf",
        \n\
        {TermColor.config_unused.value}# This value is not used by the `protoprimer`.{TermColor.reset_style.value}
        "whatever_test": 5,
    }}
)\
"""
    assert RenderConfigVisitor().render_node(root_node) == expected_output


def test_render_empty_primer_config_data():
    state_primer_conf_file_abs_path_inited = "/abs/path/to/empty_file.json"

    config_data = {}

    root_node = RootNode_primer(
        node_indent=0,
        orig_data=config_data,
        state_primer_conf_file_abs_path_inited=state_primer_conf_file_abs_path_inited,
    )

    expected_output = f"""
{TermColor.config_comment.value}# The `leap_primer` data is loaded from the [/abs/path/to/empty_file.json] file.{TermColor.reset_style.value}
leap_primer = (
    \n\
    {{
        \n\
        {TermColor.config_missing.value}# Field `ref_root_dir_rel_path` points to the dir called `ref_root`.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# The path is relative to the `proto_code` file [/abs/path/to/empty_file.json].{TermColor.reset_style.value}
        {TermColor.config_missing.value}# Normally, the `ref_root` dir is the client repo root, but it can be anything.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# See `state_ref_root_dir_abs_path_inited` in `leap_derived` -{TermColor.reset_style.value}
        {TermColor.config_missing.value}# the derived abs path is the base path for all the configured relative paths (except for this field itself, obviously).{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "ref_root_dir_rel_path": None,{TermColor.reset_style.value}
        \n\
        {TermColor.config_missing.value}# Field `global_conf_dir_rel_path` points to the global config dir (as opposed to local config dir `local_conf_symlink_rel_path`).{TermColor.reset_style.value}
        {TermColor.config_missing.value}# The path is relative to the `ref_root` dir specified in the `ref_root_dir_rel_path` field.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# See `state_global_conf_dir_abs_path_inited` in `leap_derived` -{TermColor.reset_style.value}
        {TermColor.config_missing.value}# normally, the resolved global config dir contains all other global client config files.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "global_conf_dir_rel_path": None,{TermColor.reset_style.value}
    }}
)\
"""
    assert RenderConfigVisitor().render_node(root_node) == expected_output
