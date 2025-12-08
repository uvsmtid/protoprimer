from __future__ import annotations

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    ConfConstGeneral,
    ConfConstInput,
    EnvState,
    RenderConfigVisitor,
    RootNode_input,
    TermColor,
)


def test_relationship():
    assert_test_module_name_embeds_str(RootNode_input.__name__)


def test_render_input_config_data_with_unused_fields():
    config_data = {
        EnvState.state_proto_code_file_abs_path_inited.name: f"/{ConfConstGeneral.default_proto_code_basename}",
        EnvState.state_primer_conf_file_abs_path_inited.name: f"/{ConfConstGeneral.name_protoprimer_package}.{ConfConstInput.conf_file_ext}",
        "some_string": "some_value",
        "some_int": 123,
    }

    root_node = RootNode_input(
        node_indent=0,
        orig_data=config_data,
    )

    expected_output = f"""
{TermColor.config_comment.value}# The `leap_input` data is taken from the `proto_code` process input (not configured in files):{TermColor.reset_style.value}
{TermColor.config_comment.value}# *   CLI args, environment variables, current directory, ...{TermColor.reset_style.value}
{TermColor.config_comment.value}# *   combination of the above with applied defaults.{TermColor.reset_style.value}
leap_input = (
    \n\
    {{
        \n\
        {TermColor.config_comment.value}# Value `state_proto_code_file_abs_path_inited` is an absolute path to `proto_code`.{TermColor.reset_style.value}
        {TermColor.config_comment.value}# It allows resolving all other relative paths (via `ref_root` - see field `ref_root_dir_rel_path`).{TermColor.reset_style.value}
        "state_proto_code_file_abs_path_inited": "/{ConfConstGeneral.default_proto_code_basename}",
        \n\
        {TermColor.config_comment.value}# Value `state_primer_conf_file_abs_path_inited` is an absolute path to `ConfLeap.leap_primer` config file.{TermColor.reset_style.value}
        {TermColor.config_comment.value}# The config file is selected from the list of possible candidates (whichever is found first, replacing extension to `.json`):{TermColor.reset_style.value}
        {TermColor.config_comment.value}# *   basename of the entry script,{TermColor.reset_style.value}
        {TermColor.config_comment.value}# *   basename of the `proto_code` file,{TermColor.reset_style.value}
        {TermColor.config_comment.value}# *   default `protoprimer.json`.{TermColor.reset_style.value}
        {TermColor.config_comment.value}# Note that the selected config file basename is subsequently re-used for others:{TermColor.reset_style.value}
        {TermColor.config_comment.value}# *   see `state_global_conf_file_abs_path_inited` for `leap_client`,{TermColor.reset_style.value}
        {TermColor.config_comment.value}# *   see `state_local_conf_file_abs_path_inited` for `leap_env`.{TermColor.reset_style.value}
        "state_primer_conf_file_abs_path_inited": "/{ConfConstGeneral.name_protoprimer_package}.{ConfConstInput.conf_file_ext}",
        \n\
        {TermColor.config_unused.value}# This value is not used by the `protoprimer`.{TermColor.reset_style.value}
        "some_string": "some_value",
        \n\
        {TermColor.config_unused.value}# This value is not used by the `protoprimer`.{TermColor.reset_style.value}
        "some_int": 123,
    }}
)\
"""
    assert RenderConfigVisitor().render_node(root_node) == expected_output


def test_render_empty_input_config_data():
    config_data = {}

    root_node = RootNode_input(
        node_indent=0,
        orig_data=config_data,
    )

    expected_output = f"""
{TermColor.config_comment.value}# The `leap_input` data is taken from the `proto_code` process input (not configured in files):{TermColor.reset_style.value}
{TermColor.config_comment.value}# *   CLI args, environment variables, current directory, ...{TermColor.reset_style.value}
{TermColor.config_comment.value}# *   combination of the above with applied defaults.{TermColor.reset_style.value}
leap_input = (
    \n\
    {{
        \n\
        {TermColor.config_missing.value}# Value `state_proto_code_file_abs_path_inited` is an absolute path to `proto_code`.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# It allows resolving all other relative paths (via `ref_root` - see field `ref_root_dir_rel_path`).{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "state_proto_code_file_abs_path_inited": None,{TermColor.reset_style.value}
        \n\
        {TermColor.config_missing.value}# Value `state_primer_conf_file_abs_path_inited` is an absolute path to `ConfLeap.leap_primer` config file.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# The config file is selected from the list of possible candidates (whichever is found first, replacing extension to `.json`):{TermColor.reset_style.value}
        {TermColor.config_missing.value}# *   basename of the entry script,{TermColor.reset_style.value}
        {TermColor.config_missing.value}# *   basename of the `proto_code` file,{TermColor.reset_style.value}
        {TermColor.config_missing.value}# *   default `protoprimer.json`.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# Note that the selected config file basename is subsequently re-used for others:{TermColor.reset_style.value}
        {TermColor.config_missing.value}# *   see `state_global_conf_file_abs_path_inited` for `leap_client`,{TermColor.reset_style.value}
        {TermColor.config_missing.value}# *   see `state_local_conf_file_abs_path_inited` for `leap_env`.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "state_primer_conf_file_abs_path_inited": None,{TermColor.reset_style.value}
    }}
)\
"""
    assert RenderConfigVisitor().render_node(root_node) == expected_output
