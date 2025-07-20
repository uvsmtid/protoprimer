"""
This module defines naming metadata which enforces naming convention.
"""

import enum

from protoprimer.primer_kernel import EnvState


class CompletedAction(enum.Enum):

    action_verified = "verified"


class FilesystemObjectType(enum.Enum):

    fs_object_file = "file"

    fs_object_dir = "dir"


class PathType(enum.Enum):

    # If both paths are possible (absolute or relative):
    path_any = "path"

    # Relative path:
    path_rel = "rel_path"

    # Absolute path:
    path_abs = "abs_path"


class PathName(enum.Enum):

    value_proto_kernel_code = "proto_kernel_code"

    value_proto_kernel_conf = "proto_kernel_conf"

    value_client_ref = "client_ref"

    value_client_conf = "client_conf"

    value_env_conf = "env_conf"

    value_target_env = "target_env"

    value_local_python = "local_python"

    value_local_venv = "local_venv"


class ValueName(enum.Enum):

    value_stderr_log_level = "stderr_log_level"

    value_run_mode = "run_mode"

    value_target_state_name = "target_state_name"

    value_py_exec = "py_exec"

    value_project_path_list = "project_path_list"


class ValueStage(enum.Enum):
    """
    Each value may be specified in the config, by env var, on the command line, etc.

    There is a general rule how the same value is overridden (defaults -> config -> env var -> CLI arg).

    However, this process is more complicated during bootstrap - override may happen more than once.
    For example, log level may be overridden twice (first by global client config, then by local client config).
    """

    # A hard-coded value (not specifically "hard", may be "soft" with any logic to set initial value):
    value_coded = "coded"

    # A value set by env var:
    value_var = "var"

    # The value is overridden via command line args.
    value_arg = "arg"

    # The value configured in global client config (not specific to the local environment):
    value_global = "global"

    # The value configured in local client config (specific to the local environment):
    value_local = "local"

    # A value computed based on:
    # *  `value_inited`, `value_arg`
    value_finalized = "finalized"


class StateCategoryMeta:
    def __init__(
        self,
        name_enums: list[enum.Enum],
    ):
        self.name_enums: list[enum.Enum] = name_enums


class StateCategoryItem(enum.Enum):
    """
    Depending on the category, different naming (the component set and the order) should apply.
    """

    # Some loaded data (e.g., command line args, config file, etc.)
    category_loaded_data = StateCategoryMeta(
        name_enums=[],
    )

    # Some value is read or computed:
    category_named_value = StateCategoryMeta(
        name_enums=[
            ValueName,
            ValueStage,
        ],
    )

    # More specific than `category_named_value`: value representing a filesystem path is read or computed:
    category_path_value = StateCategoryMeta(
        name_enums=[
            # The first sub-list is synced with `category_path_action`:
            PathName,
            FilesystemObjectType,
            PathType,
            #
            ValueStage,
        ],
    )

    # An action on `category_path_value`:
    category_path_action = StateCategoryMeta(
        name_enums=[
            # The first sub-list is synced with `category_path_value`:
            PathName,
            FilesystemObjectType,
            PathType,
            #
            CompletedAction,
        ],
    )

    # Every time persistent state changes:
    # *   directly (e.g., via file modification)
    # *   indirectly (e.g., via external command)
    # Whether it actually causes a mutation is not strictly necessary, only a possibility.
    category_state_mutation = StateCategoryMeta(
        name_enums=[],
    )

    # Every time `PythonExecutable` is switched:
    category_python_exec = StateCategoryMeta(
        name_enums=[],
    )


class StateMeta:

    def __init__(
        self,
        env_state: EnvState,
        category_meta: StateCategoryMeta,
    ):
        # Specified at ctor call site (primarily, for quick navigation in the IDE):
        self.env_state: EnvState = env_state

        self.category_meta: StateCategoryMeta = category_meta


class StateItem(enum.Enum):
    """
    This enum re-list all items from `EnvState` enum with metadata to verify their naming.
    """

    state_stderr_log_level_var = StateMeta(
        EnvState.state_stderr_log_level_var,
        StateCategoryItem.category_named_value.value,
    )

    state_default_stderr_logger_configured = StateMeta(
        EnvState.state_default_stderr_logger_configured,
        StateCategoryItem.category_state_mutation.value,
    )

    state_args_parsed = StateMeta(
        EnvState.state_args_parsed,
        StateCategoryItem.category_loaded_data.value,
    )

    state_stderr_log_level_finalized = StateMeta(
        EnvState.state_stderr_log_level_finalized,
        StateCategoryItem.category_named_value.value,
    )

    state_run_mode_finalized = StateMeta(
        EnvState.state_run_mode_finalized,
        StateCategoryItem.category_named_value.value,
    )

    state_target_state_name_finalized = StateMeta(
        EnvState.state_target_state_name_finalized,
        StateCategoryItem.category_named_value.value,
    )

    state_run_mode_executed = StateMeta(
        EnvState.state_run_mode_executed,
        StateCategoryItem.category_state_mutation.value,
    )

    state_py_exec_arg = StateMeta(
        EnvState.state_py_exec_arg,
        StateCategoryItem.category_named_value.value,
    )

    state_proto_kernel_code_file_abs_path_finalized = StateMeta(
        EnvState.state_proto_kernel_code_file_abs_path_finalized,
        StateCategoryItem.category_path_value.value,
    )

    state_proto_kernel_code_dir_abs_path_finalized = StateMeta(
        EnvState.state_proto_kernel_code_dir_abs_path_finalized,
        StateCategoryItem.category_path_value.value,
    )

    state_proto_kernel_conf_abs_file_path_finalized = StateMeta(
        EnvState.state_proto_kernel_conf_abs_file_path_finalized,
        StateCategoryItem.category_path_value.value,
    )

    state_client_ref_dir_path_arg = StateMeta(
        EnvState.state_client_ref_dir_path_arg,
        StateCategoryItem.category_path_value.value,
    )

    state_proto_kernel_conf_file_data = StateMeta(
        EnvState.state_proto_kernel_conf_file_data,
        StateCategoryItem.category_loaded_data.value,
    )

    state_client_ref_dir_abs_path_global = StateMeta(
        EnvState.state_client_ref_dir_abs_path_global,
        StateCategoryItem.category_path_value.value,
    )

    state_client_conf_file_abs_path_global = StateMeta(
        EnvState.state_client_conf_file_abs_path_global,
        StateCategoryItem.category_path_value.value,
    )

    state_client_conf_file_data = StateMeta(
        EnvState.state_client_conf_file_data,
        StateCategoryItem.category_loaded_data.value,
    )

    state_env_conf_dir_abs_path_local = StateMeta(
        EnvState.state_env_conf_dir_abs_path_local,
        StateCategoryItem.category_path_value.value,
    )

    state_target_env_dir_rel_path_finalized = StateMeta(
        EnvState.state_target_env_dir_rel_path_finalized,
        StateCategoryItem.category_path_value.value,
    )

    state_target_env_dir_rel_path_verified = StateMeta(
        EnvState.state_target_env_dir_rel_path_verified,
        StateCategoryItem.category_path_action.value,
    )

    state_env_conf_dir_path_verified = StateMeta(
        EnvState.state_env_conf_dir_path_verified,
        StateCategoryItem.category_path_action.value,
    )

    state_env_conf_file_path_local = StateMeta(
        EnvState.state_env_conf_file_path_local,
        StateCategoryItem.category_path_value.value,
    )

    state_env_conf_file_data = StateMeta(
        EnvState.state_env_conf_file_data,
        StateCategoryItem.category_loaded_data.value,
    )

    state_local_python_file_abs_path_finalized = StateMeta(
        EnvState.state_local_python_file_abs_path_finalized,
        StateCategoryItem.category_path_value.value,
    )

    state_local_venv_dir_path_finalized = StateMeta(
        EnvState.state_local_venv_dir_path_finalized,
        StateCategoryItem.category_path_value.value,
    )

    state_project_path_list_finalized = StateMeta(
        EnvState.state_project_path_list_finalized,
        StateCategoryItem.category_named_value.value,
    )

    state_py_exec_selected = StateMeta(
        EnvState.state_py_exec_selected,
        StateCategoryItem.category_python_exec.value,
    )

    state_protoprimer_package_installed = StateMeta(
        EnvState.state_protoprimer_package_installed,
        StateCategoryItem.category_state_mutation.value,
    )

    state_py_exec_updated_protoprimer_package_reached = StateMeta(
        EnvState.state_py_exec_updated_protoprimer_package_reached,
        StateCategoryItem.category_python_exec.value,
    )

    state_proto_kernel_updated = StateMeta(
        EnvState.state_proto_kernel_updated,
        StateCategoryItem.category_state_mutation.value,
    )

    state_py_exec_updated_proto_kernel_code = StateMeta(
        EnvState.state_py_exec_updated_proto_kernel_code,
        StateCategoryItem.category_python_exec.value,
    )
