from __future__ import annotations

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    ConfField,
    RenderConfigVisitor,
    RootNode_client,
    TermColor,
)


def test_relationship():
    assert_test_module_name_embeds_str(RootNode_client.__name__)


def test_render_client_config_data_with_unused_fields():

    state_primer_conf_client_file_abs_path_eval_finalized = "/abs/path/to/file.json"

    config_data = {
        ConfField.field_client_link_name_dir_rel_path.value: "lconf",
        ConfField.field_client_default_env_dir_rel_path.value: "dst/default_env",
        ConfField.field_required_python_file_abs_path.value: "/usr/bin/python3",
        ConfField.field_local_venv_dir_rel_path.value: "venv",
        ConfField.field_local_log_dir_rel_path.value: "log",
        ConfField.field_local_tmp_dir_rel_path.value: "tmp",
        "whatever_test": 5,
    }

    root_node = RootNode_client(
        node_indent=0,
        orig_data=config_data,
        state_primer_conf_client_file_abs_path_eval_finalized=state_primer_conf_client_file_abs_path_eval_finalized,
    )

    expected_output = f"""
{TermColor.config_comment.value}# The `leap_client` data is loaded from the [/abs/path/to/file.json] file.{TermColor.reset_style.value}
leap_client = (
    \n\
    {{
        \n\
        {TermColor.config_comment.value}# Field `client_link_name_dir_rel_path` points to local config dir (as opposed to the global config dir `primer_conf_client_dir_rel_path`).{TermColor.reset_style.value}
        {TermColor.config_comment.value}# The path is relative to the `ref_root` dir specified in the `primer_ref_root_dir_rel_path` field.{TermColor.reset_style.value}
        {TermColor.config_comment.value}# The basename of this path is a symlink set to the actual dir with environment-specific config.{TermColor.reset_style.value}
        {TermColor.config_comment.value}# If the symlink does not exist yet, its target is set from:{TermColor.reset_style.value}
        {TermColor.config_comment.value}# *   either field `client_default_env_dir_rel_path`,{TermColor.reset_style.value}
        {TermColor.config_comment.value}# *   or arg `--env` which can also be used to re-set the symlink target to a new path.{TermColor.reset_style.value}
        {TermColor.config_comment.value}# See `state_primer_conf_client_dir_abs_path_eval_finalized` in `leap_derived` -{TermColor.reset_style.value}
        {TermColor.config_comment.value}# normally, the resolved local config dir contains all local environment-specific config files.{TermColor.reset_style.value}
        "client_link_name_dir_rel_path": "lconf",
        \n\
        {TermColor.config_comment.value}# Field `client_default_env_dir_rel_path` is the default path where `client_link_name_dir_rel_path` symlink can point to.{TermColor.reset_style.value}
        {TermColor.config_comment.value}# The path is relative to the `ref_root` dir specified in the `primer_ref_root_dir_rel_path` field.{TermColor.reset_style.value}
        {TermColor.config_comment.value}# The path is ignored when the `client_link_name_dir_rel_path` symlink already exists.{TermColor.reset_style.value}
        {TermColor.config_comment.value}# Arg `--env` overrides this `client_default_env_dir_rel_path` field.{TermColor.reset_style.value}
        "client_default_env_dir_rel_path": "dst/default_env",
        \n\
        {TermColor.config_comment.value}# Field `required_python_file_abs_path` selects `python` version.{TermColor.reset_style.value}
        {TermColor.config_comment.value}# The value specifies absolute path to `python` interpreter which is used to create `venv`.{TermColor.reset_style.value}
        {TermColor.config_comment.value}# This field can be specified in global config (see `leap_client`) but it is override-able by local environment-specific config (see `leap_env`).{TermColor.reset_style.value}
        "required_python_file_abs_path": "/usr/bin/python3",
        \n\
        {TermColor.config_comment.value}# Field `local_venv_dir_rel_path` points to the dir where `venv` (`python` virtual environment) is created.{TermColor.reset_style.value}
        {TermColor.config_comment.value}# The path is relative to the `ref_root` dir specified in the `primer_ref_root_dir_rel_path` field.{TermColor.reset_style.value}
        {TermColor.config_comment.value}# This field can be specified in global config (see `leap_client`) but it is override-able by local environment-specific config (see `leap_env`).{TermColor.reset_style.value}
        "local_venv_dir_rel_path": "venv",
        \n\
        {TermColor.config_comment.value}# Field `local_log_dir_rel_path` points to the dir with log files created for each script execution.{TermColor.reset_style.value}
        {TermColor.config_comment.value}# The path is relative to the `ref_root` dir specified in the `primer_ref_root_dir_rel_path` field.{TermColor.reset_style.value}
        {TermColor.config_comment.value}# This field can be specified in global config (see `leap_client`) but it is override-able by local environment-specific config (see `leap_env`).{TermColor.reset_style.value}
        "local_log_dir_rel_path": "log",
        \n\
        {TermColor.config_comment.value}# Field `local_tmp_dir_rel_path` points to the dir with temporary files created for some commands.{TermColor.reset_style.value}
        {TermColor.config_comment.value}# The path is relative to the `ref_root` dir specified in the `primer_ref_root_dir_rel_path` field.{TermColor.reset_style.value}
        {TermColor.config_comment.value}# This field can be specified in global config (see `leap_client`) but it is override-able by local environment-specific config (see `leap_env`).{TermColor.reset_style.value}
        "local_tmp_dir_rel_path": "tmp",
        \n\
        {TermColor.config_missing.value}# Field `local_cache_dir_rel_path` points to the dir with cached files created for some commands.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# The path is relative to the `ref_root` dir specified in the `primer_ref_root_dir_rel_path` field.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# This field can be specified in global config (see `leap_client`) but it is override-able by local environment-specific config (see `leap_env`).{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "local_cache_dir_rel_path": None,{TermColor.reset_style.value}
        \n\
        {TermColor.config_missing.value}# Field `package_driver` selects a tool to manage packages:{TermColor.reset_style.value}
        {TermColor.config_missing.value}# *   specify "driver_pip" to use native `pip`,{TermColor.reset_style.value}
        {TermColor.config_missing.value}# *   specify "driver_uv" to use fast `uv`.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# This field can be specified in global config (see `leap_client`) but it is override-able by local environment-specific config (see `leap_env`).{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "package_driver": None,{TermColor.reset_style.value}
        \n\
        {TermColor.config_missing.value}# Field `project_descriptors` lists `python` projects and their installation details.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# This field can be specified in global config (see `leap_client`) but it is override-able by local environment-specific config (see `leap_env`).{TermColor.reset_style.value}
        {TermColor.config_missing.value}# Note that the `protoprimer` does not manage package dependencies itself.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# Instead, the `protoprimer` relies on `pyproject.toml` file per `python` project to specify these dependencies.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# See `state_derived_project_descriptors_eval_finalized` in `leap_derived`.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "project_descriptors": [{TermColor.reset_style.value}
        {TermColor.config_missing.value}# ],{TermColor.reset_style.value}
        \n\
        {TermColor.config_unused.value}# This value is not used by the `protoprimer`.{TermColor.reset_style.value}
        "whatever_test": 5,
    }}
)\
"""
    assert RenderConfigVisitor().render_node(root_node) == expected_output


def test_render_empty_client_config_data():
    state_primer_conf_client_file_abs_path_eval_finalized = (
        "/abs/path/to/empty_file.json"
    )

    config_data = {}

    root_node = RootNode_client(
        node_indent=0,
        orig_data=config_data,
        state_primer_conf_client_file_abs_path_eval_finalized=state_primer_conf_client_file_abs_path_eval_finalized,
    )

    expected_output = f"""
{TermColor.config_comment.value}# The `leap_client` data is loaded from the [/abs/path/to/empty_file.json] file.{TermColor.reset_style.value}
leap_client = (
    \n\
    {{
        \n\
        {TermColor.config_missing.value}# Field `client_link_name_dir_rel_path` points to local config dir (as opposed to the global config dir `primer_conf_client_dir_rel_path`).{TermColor.reset_style.value}
        {TermColor.config_missing.value}# The path is relative to the `ref_root` dir specified in the `primer_ref_root_dir_rel_path` field.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# The basename of this path is a symlink set to the actual dir with environment-specific config.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# If the symlink does not exist yet, its target is set from:{TermColor.reset_style.value}
        {TermColor.config_missing.value}# *   either field `client_default_env_dir_rel_path`,{TermColor.reset_style.value}
        {TermColor.config_missing.value}# *   or arg `--env` which can also be used to re-set the symlink target to a new path.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# See `state_primer_conf_client_dir_abs_path_eval_finalized` in `leap_derived` -{TermColor.reset_style.value}
        {TermColor.config_missing.value}# normally, the resolved local config dir contains all local environment-specific config files.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "client_link_name_dir_rel_path": None,{TermColor.reset_style.value}
        \n\
        {TermColor.config_missing.value}# Field `client_default_env_dir_rel_path` is the default path where `client_link_name_dir_rel_path` symlink can point to.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# The path is relative to the `ref_root` dir specified in the `primer_ref_root_dir_rel_path` field.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# The path is ignored when the `client_link_name_dir_rel_path` symlink already exists.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# Arg `--env` overrides this `client_default_env_dir_rel_path` field.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "client_default_env_dir_rel_path": None,{TermColor.reset_style.value}
        \n\
        {TermColor.config_missing.value}# Field `required_python_file_abs_path` selects `python` version.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# The value specifies absolute path to `python` interpreter which is used to create `venv`.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# This field can be specified in global config (see `leap_client`) but it is override-able by local environment-specific config (see `leap_env`).{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "required_python_file_abs_path": None,{TermColor.reset_style.value}
        \n\
        {TermColor.config_missing.value}# Field `local_venv_dir_rel_path` points to the dir where `venv` (`python` virtual environment) is created.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# The path is relative to the `ref_root` dir specified in the `primer_ref_root_dir_rel_path` field.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# This field can be specified in global config (see `leap_client`) but it is override-able by local environment-specific config (see `leap_env`).{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "local_venv_dir_rel_path": None,{TermColor.reset_style.value}
        \n\
        {TermColor.config_missing.value}# Field `local_log_dir_rel_path` points to the dir with log files created for each script execution.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# The path is relative to the `ref_root` dir specified in the `primer_ref_root_dir_rel_path` field.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# This field can be specified in global config (see `leap_client`) but it is override-able by local environment-specific config (see `leap_env`).{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "local_log_dir_rel_path": None,{TermColor.reset_style.value}
        \n\
        {TermColor.config_missing.value}# Field `local_tmp_dir_rel_path` points to the dir with temporary files created for some commands.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# The path is relative to the `ref_root` dir specified in the `primer_ref_root_dir_rel_path` field.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# This field can be specified in global config (see `leap_client`) but it is override-able by local environment-specific config (see `leap_env`).{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "local_tmp_dir_rel_path": None,{TermColor.reset_style.value}
        \n\
        {TermColor.config_missing.value}# Field `local_cache_dir_rel_path` points to the dir with cached files created for some commands.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# The path is relative to the `ref_root` dir specified in the `primer_ref_root_dir_rel_path` field.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# This field can be specified in global config (see `leap_client`) but it is override-able by local environment-specific config (see `leap_env`).{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "local_cache_dir_rel_path": None,{TermColor.reset_style.value}
        \n\
        {TermColor.config_missing.value}# Field `package_driver` selects a tool to manage packages:{TermColor.reset_style.value}
        {TermColor.config_missing.value}# *   specify "driver_pip" to use native `pip`,{TermColor.reset_style.value}
        {TermColor.config_missing.value}# *   specify "driver_uv" to use fast `uv`.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# This field can be specified in global config (see `leap_client`) but it is override-able by local environment-specific config (see `leap_env`).{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "package_driver": None,{TermColor.reset_style.value}
        \n\
        {TermColor.config_missing.value}# Field `project_descriptors` lists `python` projects and their installation details.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# This field can be specified in global config (see `leap_client`) but it is override-able by local environment-specific config (see `leap_env`).{TermColor.reset_style.value}
        {TermColor.config_missing.value}# Note that the `protoprimer` does not manage package dependencies itself.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# Instead, the `protoprimer` relies on `pyproject.toml` file per `python` project to specify these dependencies.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# See `state_derived_project_descriptors_eval_finalized` in `leap_derived`.{TermColor.reset_style.value}
        {TermColor.config_missing.value}# "project_descriptors": [{TermColor.reset_style.value}
        {TermColor.config_missing.value}# ],{TermColor.reset_style.value}
    }}
)\
"""
    assert RenderConfigVisitor().render_node(root_node) == expected_output
