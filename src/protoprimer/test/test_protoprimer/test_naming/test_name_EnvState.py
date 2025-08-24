from __future__ import annotations

import enum

from local_test.consistent_naming import verify_name_enum_order_in_name
from local_test.name_assertion import (
    assert_test_func_name_embeds_str,
    assert_test_module_name_embeds_str,
)
from protoprimer.primer_kernel import (
    EnvState,
)
from test_protoprimer.test_naming.naming_metadata import (
    AbstractMeta,
    NameCategory,
)
from test_protoprimer.test_naming.naming_test_base import NamingTestBase


class StateMeta(AbstractMeta):

    def __init__(
        self,
        env_state: EnvState,
        name_category: NameCategory,
    ):
        # Specified at ctor call site (primarily, for quick navigation in the IDE):
        self.env_state: EnvState = env_state
        self.name_category: NameCategory = name_category

    def get_prod_item(self):
        return self.env_state

    def extract_prod_item_value_name(self) -> str:
        return self.env_state.value.__name__

    def get_name(self):
        return self.env_state.name

    def get_category(self):
        return self.name_category


class StateName(enum.Enum):
    """
    This enum re-lists all items from the `EnvState` enum with metadata to verify their naming.
    """

    state_process_status_initialized = StateMeta(
        EnvState.state_process_status_initialized,
        NameCategory.category_state_mutation,
    )

    state_input_stderr_log_level_var_loaded = StateMeta(
        EnvState.state_input_stderr_log_level_var_loaded,
        NameCategory.category_named_value,
    )

    state_default_stderr_log_handler_configured = StateMeta(
        EnvState.state_default_stderr_log_handler_configured,
        NameCategory.category_state_mutation,
    )

    state_args_parsed = StateMeta(
        EnvState.state_args_parsed,
        NameCategory.category_loaded_data,
    )

    state_input_wizard_stage_arg_loaded = StateMeta(
        EnvState.state_input_wizard_stage_arg_loaded,
        NameCategory.category_named_value,
    )

    state_input_stderr_log_level_eval_finalized_gconf = StateMeta(
        EnvState.state_input_stderr_log_level_eval_finalized_gconf,
        NameCategory.category_named_value,
    )

    state_input_run_mode_arg_loaded_gconf = StateMeta(
        EnvState.state_input_run_mode_arg_loaded_gconf,
        NameCategory.category_named_value,
    )

    state_input_target_state_eval_finalized = StateMeta(
        EnvState.state_input_target_state_eval_finalized,
        NameCategory.category_named_value,
    )

    state_run_mode_executed = StateMeta(
        EnvState.state_run_mode_executed,
        NameCategory.category_state_mutation,
    )

    state_input_py_exec_arg_loaded = StateMeta(
        EnvState.state_input_py_exec_arg_loaded,
        NameCategory.category_named_value,
    )

    state_input_proto_code_file_abs_path_eval_finalized = StateMeta(
        EnvState.state_input_proto_code_file_abs_path_eval_finalized,
        NameCategory.category_path_value,
    )

    state_input_proto_code_dir_abs_path_eval_finalized = StateMeta(
        EnvState.state_input_proto_code_dir_abs_path_eval_finalized,
        NameCategory.category_path_value,
    )

    state_input_proto_conf_primer_file_abs_path_eval_finalized = StateMeta(
        EnvState.state_input_proto_conf_primer_file_abs_path_eval_finalized,
        NameCategory.category_path_value,
    )

    state_proto_conf_file_data = StateMeta(
        EnvState.state_proto_conf_file_data,
        NameCategory.category_loaded_data,
    )

    state_primer_ref_root_dir_abs_path_eval_finalized = StateMeta(
        EnvState.state_primer_ref_root_dir_abs_path_eval_finalized,
        NameCategory.category_path_value,
    )

    state_primer_conf_client_file_abs_path_eval_finalized = StateMeta(
        EnvState.state_primer_conf_client_file_abs_path_eval_finalized,
        NameCategory.category_path_value,
    )

    state_client_conf_file_data = StateMeta(
        EnvState.state_client_conf_file_data,
        NameCategory.category_loaded_data,
    )

    state_client_conf_env_dir_abs_path_eval_finalized = StateMeta(
        EnvState.state_client_conf_env_dir_abs_path_eval_finalized,
        NameCategory.category_path_value,
    )

    state_client_local_env_dir_rel_path_eval_finalized = StateMeta(
        EnvState.state_client_local_env_dir_rel_path_eval_finalized,
        NameCategory.category_path_value,
    )

    state_client_local_env_dir_rel_path_eval_verified = StateMeta(
        EnvState.state_client_local_env_dir_rel_path_eval_verified,
        NameCategory.category_path_value,
    )

    state_client_conf_env_dir_abs_path_eval_verified = StateMeta(
        EnvState.state_client_conf_env_dir_abs_path_eval_verified,
        NameCategory.category_path_value,
    )

    state_client_link_name_dir_rel_path_eval_finalized = StateMeta(
        EnvState.state_client_link_name_dir_rel_path_eval_finalized,
        NameCategory.category_path_value,
    )

    state_client_conf_env_file_abs_path_eval_finalized = StateMeta(
        EnvState.state_client_conf_env_file_abs_path_eval_finalized,
        NameCategory.category_path_value,
    )

    state_env_conf_file_data = StateMeta(
        EnvState.state_env_conf_file_data,
        NameCategory.category_loaded_data,
    )

    state_env_local_python_file_abs_path_eval_finalized = StateMeta(
        EnvState.state_env_local_python_file_abs_path_eval_finalized,
        NameCategory.category_path_value,
    )

    state_env_local_venv_dir_abs_path_eval_finalized = StateMeta(
        EnvState.state_env_local_venv_dir_abs_path_eval_finalized,
        NameCategory.category_path_value,
    )

    state_env_project_descriptors_eval_finalized = StateMeta(
        EnvState.state_env_project_descriptors_eval_finalized,
        NameCategory.category_named_value,
    )

    state_py_exec_selected = StateMeta(
        EnvState.state_py_exec_selected,
        NameCategory.category_python_exec,
    )

    state_protoprimer_package_installed = StateMeta(
        EnvState.state_protoprimer_package_installed,
        NameCategory.category_state_mutation,
    )

    state_py_exec_updated_protoprimer_package_reached = StateMeta(
        EnvState.state_py_exec_updated_protoprimer_package_reached,
        NameCategory.category_python_exec,
    )

    state_proto_code_updated = StateMeta(
        EnvState.state_proto_code_updated,
        NameCategory.category_state_mutation,
    )

    state_py_exec_updated_proto_code = StateMeta(
        EnvState.state_py_exec_updated_proto_code,
        NameCategory.category_python_exec,
    )

    state_process_status_reported = StateMeta(
        EnvState.state_process_status_reported,
        NameCategory.category_state_mutation,
    )


class TestStateName(NamingTestBase):
    prod_enum = EnvState
    test_enum = StateName
    enum_prefix: str = "state_"

    def test_module_naming(self):
        assert_test_module_name_embeds_str(
            self.prod_enum.__name__,
        )

    def test_state_client_local_env_dir_rel_path_eval_finalized(self):
        """
        A sample for debugging.
        """
        assert_test_func_name_embeds_str(
            self.test_enum.state_client_local_env_dir_rel_path_eval_finalized.name,
        )

        ret_val: enum.Enum | None = verify_name_enum_order_in_name(
            self.test_enum.state_client_local_env_dir_rel_path_eval_finalized.value.get_category().value.name_enums,
            self.test_enum.state_client_local_env_dir_rel_path_eval_finalized.name,
        )

        assert ret_val is None
