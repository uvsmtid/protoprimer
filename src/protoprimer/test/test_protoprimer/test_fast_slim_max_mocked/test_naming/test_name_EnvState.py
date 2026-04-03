from __future__ import annotations

import enum

from local_test.name_assertion import (
    assert_test_module_name_embeds_str,
)
from protoprimer.primer_kernel import (
    CommandAction,
    ConfConstGeneral,
    ConfLeap,
    EnvState,
    FilesystemObject,
    KeyWord,
    PathName,
    PathType,
    StateStride,
    ValueName,
)
from test_protoprimer.test_fast_slim_max_mocked.test_naming.naming_metadata import (
    AbstractMeta,
    CompletedAction,
    NameCategory,
    ValueSource,
)
from test_protoprimer.test_fast_slim_max_mocked.test_naming.naming_test_base import (
    NamingTestBase,
)


class StateMeta(AbstractMeta):

    def __init__(
        self,
        env_state: EnvState,
        name_category: NameCategory,
        name_components: list[str],
    ):
        # Specified at ctor call site (primarily, for quick navigation in the IDE):
        self.env_state: EnvState = env_state
        self.name_category: NameCategory = name_category
        self.name_components: list[str] = name_components

    def get_prod_item(self):
        return self.env_state

    def extract_prod_item_value_name(self) -> str:
        return self.env_state.value.__name__

    def get_name(self):
        return self.env_state.name

    def get_category(self):
        return self.name_category

    def get_name_components(self) -> list[str]:
        return self.name_components


class StateName(enum.Enum):
    """
    This enum re-lists all items from the `EnvState` enum with metadata to verify their naming.
    """

    state_input_py_exec_var_loaded = StateMeta(
        env_state=EnvState.state_input_py_exec_var_loaded,
        name_category=NameCategory.category_named_value,
        name_components=[
            KeyWord.key_state.value,
            ConfLeap.leap_input.value,
            ValueName.value_py_exec.value,
            ValueSource.value_var.value,
            CompletedAction.action_loaded.value,
        ],
    )

    state_input_stderr_log_level_var_loaded = StateMeta(
        env_state=EnvState.state_input_stderr_log_level_var_loaded,
        name_category=NameCategory.category_named_value,
        name_components=[
            KeyWord.key_state.value,
            ConfLeap.leap_input.value,
            ValueName.value_stderr_log_level.value,
            ValueSource.value_var.value,
            CompletedAction.action_loaded.value,
        ],
    )

    state_input_do_install_var_loaded = StateMeta(
        env_state=EnvState.state_input_do_install_var_loaded,
        name_category=NameCategory.category_named_value,
        name_components=[
            KeyWord.key_state.value,
            ConfLeap.leap_input.value,
            ValueName.value_do_install.value,
            ValueSource.value_var.value,
            CompletedAction.action_loaded.value,
        ],
    )

    state_default_stderr_log_handler_configured = StateMeta(
        env_state=EnvState.state_default_stderr_log_handler_configured,
        name_category=NameCategory.category_state_mutation,
        name_components=[
            KeyWord.key_state.value,
            KeyWord.key_default.value,
            KeyWord.key_stderr.value,
            KeyWord.key_log.value,
            KeyWord.key_handler.value,
            KeyWord.key_configured.value,
        ],
    )

    state_default_file_log_handler_configured = StateMeta(
        env_state=EnvState.state_default_file_log_handler_configured,
        name_category=NameCategory.category_state_mutation,
        name_components=[
            KeyWord.key_state.value,
            KeyWord.key_default.value,
            FilesystemObject.fs_object_file.value,
            KeyWord.key_log.value,
            KeyWord.key_handler.value,
            KeyWord.key_configured.value,
        ],
    )

    state_args_parsed = StateMeta(
        env_state=EnvState.state_args_parsed,
        name_category=NameCategory.category_name_only,
        name_components=[
            KeyWord.key_state.value,
            KeyWord.key_args.value,
            KeyWord.key_parsed.value,
        ],
    )

    state_input_stderr_log_level_eval_finalized = StateMeta(
        env_state=EnvState.state_input_stderr_log_level_eval_finalized,
        name_category=NameCategory.category_named_value,
        name_components=[
            KeyWord.key_state.value,
            ConfLeap.leap_input.value,
            ValueName.value_stderr_log_level.value,
            ValueSource.value_eval.value,
            CompletedAction.action_finalized.value,
        ],
    )

    state_input_exec_mode_arg_loaded = StateMeta(
        env_state=EnvState.state_input_exec_mode_arg_loaded,
        name_category=NameCategory.category_named_value,
        name_components=[
            KeyWord.key_state.value,
            ConfLeap.leap_input.value,
            ValueName.value_exec_mode.value,
            ValueSource.value_arg.value,
            CompletedAction.action_loaded.value,
        ],
    )

    state_input_final_state_eval_finalized = StateMeta(
        env_state=EnvState.state_input_final_state_eval_finalized,
        name_category=NameCategory.category_named_value,
        name_components=[
            KeyWord.key_state.value,
            ConfLeap.leap_input.value,
            ValueName.value_final_state.value,
            ValueSource.value_eval.value,
            CompletedAction.action_finalized.value,
        ],
    )

    state_exec_mode_executed = StateMeta(
        env_state=EnvState.state_exec_mode_executed,
        name_category=NameCategory.category_state_mutation,
        name_components=[
            KeyWord.key_state.value,
            ValueName.value_exec_mode.value,
            KeyWord.key_executed.value,
        ],
    )

    state_input_start_id_var_loaded = StateMeta(
        env_state=EnvState.state_input_start_id_var_loaded,
        name_category=NameCategory.category_named_value,
        name_components=[
            KeyWord.key_state.value,
            ConfLeap.leap_input.value,
            ValueName.value_start_id.value,
            ValueSource.value_var.value,
            CompletedAction.action_loaded.value,
        ],
    )

    state_input_proto_code_file_abs_path_var_loaded = StateMeta(
        env_state=EnvState.state_input_proto_code_file_abs_path_var_loaded,
        name_category=NameCategory.category_path_value_deprecated,
        name_components=[
            KeyWord.key_state.value,
            ConfLeap.leap_input.value,
            PathName.path_proto_code.value,
            FilesystemObject.fs_object_file.value,
            PathType.path_abs.value,
            ValueSource.value_var.value,
            CompletedAction.action_loaded.value,
        ],
    )

    state_stride_py_arbitrary_reached = StateMeta(
        env_state=EnvState.state_stride_py_arbitrary_reached,
        name_category=NameCategory.category_python_exec,
        name_components=[
            KeyWord.key_state.value,
            StateStride.stride_py_arbitrary.name,
            KeyWord.key_reached.value,
        ],
    )

    state_proto_code_file_abs_path_inited = StateMeta(
        env_state=EnvState.state_proto_code_file_abs_path_inited,
        name_category=NameCategory.category_path_value,
        name_components=[
            KeyWord.key_state.value,
            PathName.path_proto_code.value,
            FilesystemObject.fs_object_file.value,
            PathType.path_abs.value,
            CompletedAction.action_inited.value,
        ],
    )

    state_primer_conf_file_abs_path_inited = StateMeta(
        env_state=EnvState.state_primer_conf_file_abs_path_inited,
        name_category=NameCategory.category_path_value,
        name_components=[
            KeyWord.key_state.value,
            PathName.path_primer_conf.value,
            FilesystemObject.fs_object_file.value,
            PathType.path_abs.value,
            CompletedAction.action_inited.value,
        ],
    )

    state_primer_conf_file_data_loaded = StateMeta(
        env_state=EnvState.state_primer_conf_file_data_loaded,
        name_category=NameCategory.category_loaded_data,
        name_components=[
            KeyWord.key_state.value,
            ConfLeap.leap_primer.value,
            KeyWord.key_conf.value,
            FilesystemObject.fs_object_file.value,
            KeyWord.key_data.value,
            CompletedAction.action_loaded.value,
        ],
    )

    state_ref_root_dir_abs_path_inited = StateMeta(
        env_state=EnvState.state_ref_root_dir_abs_path_inited,
        name_category=NameCategory.category_path_value,
        name_components=[
            KeyWord.key_state.value,
            PathName.path_ref_root.value,
            FilesystemObject.fs_object_dir.value,
            PathType.path_abs.value,
            CompletedAction.action_inited.value,
        ],
    )

    state_global_conf_dir_abs_path_inited = StateMeta(
        env_state=EnvState.state_global_conf_dir_abs_path_inited,
        name_category=NameCategory.category_path_value,
        name_components=[
            KeyWord.key_state.value,
            PathName.path_global_conf.value,
            FilesystemObject.fs_object_dir.value,
            PathType.path_abs.value,
            CompletedAction.action_inited.value,
        ],
    )

    state_global_conf_file_abs_path_inited = StateMeta(
        env_state=EnvState.state_global_conf_file_abs_path_inited,
        name_category=NameCategory.category_path_value,
        name_components=[
            KeyWord.key_state.value,
            PathName.path_global_conf.value,
            FilesystemObject.fs_object_file.value,
            PathType.path_abs.value,
            CompletedAction.action_inited.value,
        ],
    )

    state_client_conf_file_data_loaded = StateMeta(
        env_state=EnvState.state_client_conf_file_data_loaded,
        name_category=NameCategory.category_loaded_data,
        name_components=[
            KeyWord.key_state.value,
            ConfLeap.leap_client.value,
            KeyWord.key_conf.value,
            FilesystemObject.fs_object_file.value,
            KeyWord.key_data.value,
            CompletedAction.action_loaded.value,
        ],
    )

    state_local_conf_symlink_abs_path_inited = StateMeta(
        env_state=EnvState.state_local_conf_symlink_abs_path_inited,
        name_category=NameCategory.category_path_value,
        name_components=[
            KeyWord.key_state.value,
            PathName.path_local_conf.value,
            FilesystemObject.fs_object_symlink.value,
            PathType.path_abs.value,
            CompletedAction.action_inited.value,
        ],
    )

    state_selected_env_dir_rel_path_inited = StateMeta(
        env_state=EnvState.state_selected_env_dir_rel_path_inited,
        name_category=NameCategory.category_path_value,
        name_components=[
            KeyWord.key_state.value,
            PathName.path_selected_env.value,
            FilesystemObject.fs_object_dir.value,
            PathType.path_rel.value,
            CompletedAction.action_inited.value,
        ],
    )

    state_local_conf_file_abs_path_inited = StateMeta(
        env_state=EnvState.state_local_conf_file_abs_path_inited,
        name_category=NameCategory.category_path_value,
        name_components=[
            KeyWord.key_state.value,
            PathName.path_local_conf.value,
            FilesystemObject.fs_object_file.value,
            PathType.path_abs.value,
            CompletedAction.action_inited.value,
        ],
    )

    state_env_conf_file_data_loaded = StateMeta(
        env_state=EnvState.state_env_conf_file_data_loaded,
        name_category=NameCategory.category_loaded_data,
        name_components=[
            KeyWord.key_state.value,
            ConfLeap.leap_env.value,
            KeyWord.key_conf.value,
            FilesystemObject.fs_object_file.value,
            KeyWord.key_data.value,
            CompletedAction.action_loaded.value,
        ],
    )

    state_required_python_version_inited = StateMeta(
        env_state=EnvState.state_required_python_version_inited,
        name_category=NameCategory.category_value_field_action,
        name_components=[
            KeyWord.key_state.value,
            PathName.path_required_python.value,
            ValueName.value_version.value,
            CompletedAction.action_inited.value,
        ],
    )

    state_python_selector_file_abs_path_inited = StateMeta(
        env_state=EnvState.state_python_selector_file_abs_path_inited,
        name_category=NameCategory.category_path_value,
        name_components=[
            KeyWord.key_state.value,
            PathName.path_python_selector.value,
            FilesystemObject.fs_object_file.value,
            PathType.path_abs.value,
            CompletedAction.action_inited.value,
        ],
    )

    state_selected_python_file_abs_path_inited = StateMeta(
        env_state=EnvState.state_selected_python_file_abs_path_inited,
        name_category=NameCategory.category_path_value,
        name_components=[
            KeyWord.key_state.value,
            PathName.path_selected_python.value,
            FilesystemObject.fs_object_file.value,
            PathType.path_abs.value,
            CompletedAction.action_inited.value,
        ],
    )

    state_local_venv_dir_abs_path_inited = StateMeta(
        env_state=EnvState.state_local_venv_dir_abs_path_inited,
        name_category=NameCategory.category_path_value,
        name_components=[
            KeyWord.key_state.value,
            PathName.path_local_venv.value,
            FilesystemObject.fs_object_dir.value,
            PathType.path_abs.value,
            CompletedAction.action_inited.value,
        ],
    )

    state_local_log_dir_abs_path_inited = StateMeta(
        env_state=EnvState.state_local_log_dir_abs_path_inited,
        name_category=NameCategory.category_path_value,
        name_components=[
            KeyWord.key_state.value,
            PathName.path_local_log.value,
            FilesystemObject.fs_object_dir.value,
            PathType.path_abs.value,
            CompletedAction.action_inited.value,
        ],
    )

    state_local_tmp_dir_abs_path_inited = StateMeta(
        env_state=EnvState.state_local_tmp_dir_abs_path_inited,
        name_category=NameCategory.category_path_value,
        name_components=[
            KeyWord.key_state.value,
            PathName.path_local_tmp.value,
            FilesystemObject.fs_object_dir.value,
            PathType.path_abs.value,
            CompletedAction.action_inited.value,
        ],
    )

    state_local_cache_dir_abs_path_inited = StateMeta(
        env_state=EnvState.state_local_cache_dir_abs_path_inited,
        name_category=NameCategory.category_path_value,
        name_components=[
            KeyWord.key_state.value,
            PathName.path_local_cache.value,
            FilesystemObject.fs_object_dir.value,
            PathType.path_abs.value,
            CompletedAction.action_inited.value,
        ],
    )

    state_project_descriptors_inited = StateMeta(
        env_state=EnvState.state_project_descriptors_inited,
        name_category=NameCategory.category_value_field_action,
        name_components=[
            KeyWord.key_state.value,
            ValueName.value_project_descriptors.value,
            CompletedAction.action_inited.value,
        ],
    )

    state_install_specs_inited = StateMeta(
        env_state=EnvState.state_install_specs_inited,
        name_category=NameCategory.category_value_field_action,
        name_components=[
            KeyWord.key_state.value,
            ValueName.value_install_specs.value,
            CompletedAction.action_inited.value,
        ],
    )

    state_venv_driver_inited = StateMeta(
        env_state=EnvState.state_venv_driver_inited,
        name_category=NameCategory.category_value_field_action,
        name_components=[
            KeyWord.key_state.value,
            ValueName.value_venv_driver.value,
            CompletedAction.action_inited.value,
        ],
    )

    state_derived_conf_data_loaded = StateMeta(
        env_state=EnvState.state_derived_conf_data_loaded,
        name_category=NameCategory.category_state_mutation,
        name_components=[
            KeyWord.key_state.value,
            KeyWord.key_derived.value,
            KeyWord.key_conf.value,
            KeyWord.key_data.value,
            CompletedAction.action_loaded.value,
        ],
    )

    state_effective_config_data_printed = StateMeta(
        env_state=EnvState.state_effective_config_data_printed,
        name_category=NameCategory.category_state_mutation,
        name_components=[
            KeyWord.key_state.value,
            KeyWord.key_effective.value,
            KeyWord.key_config.value,
            KeyWord.key_data.value,
            KeyWord.key_printed.value,
        ],
    )

    state_stride_py_required_reached = StateMeta(
        env_state=EnvState.state_stride_py_required_reached,
        name_category=NameCategory.category_python_exec,
        name_components=[
            KeyWord.key_state.value,
            StateStride.stride_py_required.name,
            KeyWord.key_reached.value,
        ],
    )

    state_reinstall_triggered = StateMeta(
        env_state=EnvState.state_reinstall_triggered,
        name_category=NameCategory.category_state_mutation,
        name_components=[
            KeyWord.key_state.value,
            CommandAction.action_reinstall.value,
            KeyWord.key_triggered.value,
        ],
    )

    state_stride_py_venv_reached = StateMeta(
        env_state=EnvState.state_stride_py_venv_reached,
        name_category=NameCategory.category_python_exec,
        name_components=[
            KeyWord.key_state.value,
            StateStride.stride_py_venv.name,
            KeyWord.key_reached.value,
        ],
    )

    state_protoprimer_package_installed = StateMeta(
        env_state=EnvState.state_protoprimer_package_installed,
        name_category=NameCategory.category_state_mutation,
        name_components=[
            KeyWord.key_state.value,
            ConfConstGeneral.name_protoprimer_package,
            KeyWord.key_package.value,
            KeyWord.key_installed.value,
        ],
    )

    state_version_constraints_generated = StateMeta(
        env_state=EnvState.state_version_constraints_generated,
        name_category=NameCategory.category_state_mutation,
        name_components=[
            KeyWord.key_state.value,
            ValueName.value_version.value,
            KeyWord.key_constraints.value,
            KeyWord.key_generated.value,
        ],
    )

    state_stride_deps_updated_reached = StateMeta(
        env_state=EnvState.state_stride_deps_updated_reached,
        name_category=NameCategory.category_python_exec,
        name_components=[
            KeyWord.key_state.value,
            StateStride.stride_deps_updated.name,
            KeyWord.key_reached.value,
        ],
    )

    state_proto_code_updated = StateMeta(
        env_state=EnvState.state_proto_code_updated,
        name_category=NameCategory.category_state_mutation,
        name_components=[
            KeyWord.key_state.value,
            PathName.path_proto_code.value,
            KeyWord.key_updated.value,
        ],
    )

    state_stride_src_updated_reached = StateMeta(
        env_state=EnvState.state_stride_src_updated_reached,
        name_category=NameCategory.category_python_exec,
        name_components=[
            KeyWord.key_state.value,
            StateStride.stride_src_updated.name,
            KeyWord.key_reached.value,
        ],
    )

    state_command_executed = StateMeta(
        env_state=EnvState.state_command_executed,
        name_category=NameCategory.category_state_mutation,
        name_components=[
            KeyWord.key_state.value,
            CommandAction.action_command.value,
            KeyWord.key_executed.value,
        ],
    )

    state_venv_driver_prepared = StateMeta(
        env_state=EnvState.state_venv_driver_prepared,
        name_category=NameCategory.category_state_mutation,
        name_components=[
            KeyWord.key_state.value,
            ValueName.value_venv_driver.value,
            KeyWord.key_prepared.value,
        ],
    )


class TestStateName(NamingTestBase):
    prod_enum = EnvState
    test_enum = StateName
    enum_prefix: str = "state_"

    def test_module_naming(self):
        assert_test_module_name_embeds_str(
            self.prod_enum.__name__,
        )
