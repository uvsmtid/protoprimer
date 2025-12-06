from __future__ import annotations

import json

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    ConfField,
    RenderConfigVisitor,
    RootNode_env,
    TermColor,
)


def test_relationship():
    assert_test_module_name_embeds_str(RootNode_env.__name__)


def test_render_env_config_data_with_unused_fields():
    state_input_proto_conf_env_file_abs_path_eval_finalized = "/abs/path/to/file.json"

    config_data = {
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
        0,
        config_data,
        state_input_proto_conf_env_file_abs_path_eval_finalized,
    )

    expected_output = f"""
{TermColor.config_comment.value}# The data is loaded from the [/abs/path/to/file.json] file.{TermColor.reset_style.value}
leap_env = (
    \n\
    {{
        \n\
        {TermColor.config_missing.value}# Field `required_python_file_abs_path` selects `python` version.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# The value specifies absolute path to `python` interpreter which is used to create `venv`.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# This field can be specified in global config (see `client`) but it is override-able by local environment-specific config (see `env`).{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "required_python_file_abs_path": None,{TermColor.reset_style.value}
        \n\
        {TermColor.config_missing.value}# Field `local_venv_dir_rel_path` points to the dir where `venv` (`python` virtual environment) is created.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# The path is relative to the `ref_root` dir specified in the `primer_ref_root_dir_rel_path` field.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# This field can be specified in global config (see `client`) but it is override-able by local environment-specific config (see `env`).{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "local_venv_dir_rel_path": None,{TermColor.reset_style.value}
        \n\
        {TermColor.config_missing.value}# Field `local_log_dir_rel_path` points to the dir with log files created for each script execution.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# The path is relative to the `ref_root` dir specified in the `primer_ref_root_dir_rel_path` field.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# This field can be specified in global config (see `client`) but it is override-able by local environment-specific config (see `env`).{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "local_log_dir_rel_path": None,{TermColor.reset_style.value}
        \n\
        {TermColor.config_missing.value}# Field `local_tmp_dir_rel_path` points to the dir with temporary files created for some commands.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# The path is relative to the `ref_root` dir specified in the `primer_ref_root_dir_rel_path` field.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# This field can be specified in global config (see `client`) but it is override-able by local environment-specific config (see `env`).{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "local_tmp_dir_rel_path": None,{TermColor.reset_style.value}
        \n\
        {TermColor.config_missing.value}# Field `local_cache_dir_rel_path` points to the dir with cached files created for some commands.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# The path is relative to the `ref_root` dir specified in the `primer_ref_root_dir_rel_path` field.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# This field can be specified in global config (see `client`) but it is override-able by local environment-specific config (see `env`).{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "local_cache_dir_rel_path": None,{TermColor.reset_style.value}
        \n\
        {TermColor.config_missing.value}# Field `package_driver` selects a tool to manage packages:{TermColor.reset_style.value}
        {TermColor.config_missing.value}# *   specify "driver_pip" to use native `pip`,{TermColor.reset_style.value}
        {TermColor.config_missing.value}# *   specify "driver_uv" to use fast `uv`.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# This field can be specified in global config (see `client`) but it is override-able by local environment-specific config (see `env`).{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "package_driver": None,{TermColor.reset_style.value}
        \n\
        {TermColor.config_comment.value}# Field `project_descriptors` lists `python` projects and their installation details.{TermColor.reset_style.value}
        {TermColor.config_comment.value}# This field can be specified in global config (see `client`) but it is override-able by local environment-specific config (see `env`).{TermColor.reset_style.value}
        {TermColor.config_comment.value}# Note that the `protoprimer` does not manage package dependencies itself.{TermColor.reset_style.value}
        {TermColor.config_comment.value}# Instead, the `protoprimer` relies on `pyproject.toml` file per `python` project to specify these dependencies.{TermColor.reset_style.value}
        {TermColor.config_comment.value}# See `state_derived_project_descriptors_eval_finalized` in `derived`.{TermColor.reset_style.value}
        "{ConfField.field_project_descriptors.value}": [
            \n\
            {{
                \n\
                {TermColor.config_comment.value}# This is similar to specifying where `pyproject.toml` is:{TermColor.reset_style.value}
                {TermColor.config_comment.value}# pip install path/to/project{TermColor.reset_style.value}
                "{ConfField.field_build_root_dir_rel_path.value}": "src/test_project",
                \n\
                {TermColor.config_comment.value}# This is similar to specifying a list of `extra_item`-s per `path/to/project`:{TermColor.reset_style.value}
                {TermColor.config_comment.value}# pip install path/to/project[extra_item_1,extra_item_2,...]{TermColor.reset_style.value}
                "{ConfField.field_install_extras.value}": [
                    \n\
                    "test",
                ],
                \n\
                {TermColor.config_unused.value}# This `list` is not used by the `protoprimer`.{TermColor.reset_style.value}
                "whatever_test": [
                    \n\
                    7,
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


def test_render_empty_env_config_data():
    state_input_proto_conf_env_file_abs_path_eval_finalized = "/abs/path/to/file.json"

    config_data = {}

    root_node = RootNode_env(
        0,
        config_data,
        state_input_proto_conf_env_file_abs_path_eval_finalized,
    )

    expected_output = f"""
{TermColor.config_comment.value}# The data is loaded from the [/abs/path/to/file.json] file.{TermColor.reset_style.value}
leap_env = (
    \n\
    {{
        \n\
        {TermColor.config_missing.value}# Field `required_python_file_abs_path` selects `python` version.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# The value specifies absolute path to `python` interpreter which is used to create `venv`.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# This field can be specified in global config (see `client`) but it is override-able by local environment-specific config (see `env`).{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "required_python_file_abs_path": None,{TermColor.reset_style.value}
        \n\
        {TermColor.config_missing.value}# Field `local_venv_dir_rel_path` points to the dir where `venv` (`python` virtual environment) is created.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# The path is relative to the `ref_root` dir specified in the `primer_ref_root_dir_rel_path` field.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# This field can be specified in global config (see `client`) but it is override-able by local environment-specific config (see `env`).{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "local_venv_dir_rel_path": None,{TermColor.reset_style.value}
        \n\
        {TermColor.config_missing.value}# Field `local_log_dir_rel_path` points to the dir with log files created for each script execution.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# The path is relative to the `ref_root` dir specified in the `primer_ref_root_dir_rel_path` field.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# This field can be specified in global config (see `client`) but it is override-able by local environment-specific config (see `env`).{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "local_log_dir_rel_path": None,{TermColor.reset_style.value}
        \n\
        {TermColor.config_missing.value}# Field `local_tmp_dir_rel_path` points to the dir with temporary files created for some commands.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# The path is relative to the `ref_root` dir specified in the `primer_ref_root_dir_rel_path` field.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# This field can be specified in global config (see `client`) but it is override-able by local environment-specific config (see `env`).{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "local_tmp_dir_rel_path": None,{TermColor.reset_style.value}
        \n\
        {TermColor.config_missing.value}# Field `local_cache_dir_rel_path` points to the dir with cached files created for some commands.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# The path is relative to the `ref_root` dir specified in the `primer_ref_root_dir_rel_path` field.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# This field can be specified in global config (see `client`) but it is override-able by local environment-specific config (see `env`).{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "local_cache_dir_rel_path": None,{TermColor.reset_style.value}
        \n\
        {TermColor.config_missing.value}# Field `package_driver` selects a tool to manage packages:{TermColor.reset_style.value}
        {TermColor.config_missing.value}# *   specify "driver_pip" to use native `pip`,{TermColor.reset_style.value}
        {TermColor.config_missing.value}# *   specify "driver_uv" to use fast `uv`.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# This field can be specified in global config (see `client`) but it is override-able by local environment-specific config (see `env`).{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "package_driver": None,{TermColor.reset_style.value}
        \n\
        {TermColor.config_missing.value}# Field `project_descriptors` lists `python` projects and their installation details.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# This field can be specified in global config (see `client`) but it is override-able by local environment-specific config (see `env`).{TermColor.reset_style.value}
        {TermColor.config_missing.value}# Note that the `protoprimer` does not manage package dependencies itself.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# Instead, the `protoprimer` relies on `pyproject.toml` file per `python` project to specify these dependencies.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# See `state_derived_project_descriptors_eval_finalized` in `derived`.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "project_descriptors": [{TermColor.reset_style.value}
        {TermColor.config_missing.value}# ],{TermColor.reset_style.value}
    }}
)\
"""
    assert RenderConfigVisitor().render_node(root_node) == expected_output
