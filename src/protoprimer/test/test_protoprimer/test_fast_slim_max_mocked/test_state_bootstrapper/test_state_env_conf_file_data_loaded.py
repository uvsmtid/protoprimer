import json
import os
from logging import WARNING
from unittest.mock import patch

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.mock_verifier import (
    assert_parent_states_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_local_conf_file_abs_path_inited,
    Bootstrapper_state_input_py_exec_var_loaded,
    Bootstrapper_state_input_run_mode_arg_loaded,
    EnvContext,
    EnvState,
)


# noinspection PyPep8Naming
class ThisTestClass(BasePyfakefsTestClass):

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = EnvContext()

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_str(
            EnvState.state_env_conf_file_data_loaded.name
        )

    @patch(
        f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_stderr_log_level_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_run_mode_arg_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_py_exec_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_file_abs_path_inited.__name__}.eval_own_state"
    )
    def test_state_env_conf_file_data_loaded_exists(
        self,
        mock_state_local_conf_file_abs_path_inited,
        mock_state_input_py_exec_var_loaded,
        mock_state_input_run_mode_arg_loaded,
        mock_state_input_stderr_log_level_eval_finalized,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_env_conf_file_data_loaded.name,
        )

        mock_conf_file = "/mock/path/to/env_conf.json"
        mock_state_local_conf_file_abs_path_inited.return_value = mock_conf_file

        mock_data = {"test": "data"}
        self.fs.create_file(mock_conf_file, contents=json.dumps(mock_data))

        # when:

        state_value = self.env_ctx.state_graph.eval_state(
            EnvState.state_env_conf_file_data_loaded.name
        )

        # then:

        self.assertEqual(state_value, mock_data)

    @patch(
        f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_stderr_log_level_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_run_mode_arg_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_py_exec_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_file_abs_path_inited.__name__}.eval_own_state"
    )
    def test_state_env_conf_file_data_loaded_missing(
        self,
        mock_state_local_conf_file_abs_path_inited,
        mock_state_input_py_exec_var_loaded,
        mock_state_input_run_mode_arg_loaded,
        mock_state_input_stderr_log_level_eval_finalized,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_env_conf_file_data_loaded.name,
        )

        mock_conf_file = "/mock/path/to/env_conf.json"
        self.fs.create_dir("/mock/path/to")
        mock_state_local_conf_file_abs_path_inited.return_value = mock_conf_file

        self.assertFalse(os.path.exists(mock_conf_file))

        # when:

        with self.assertLogs(primer_kernel.logger, level=WARNING) as log_dst:
            state_value = self.env_ctx.state_graph.eval_state(
                EnvState.state_env_conf_file_data_loaded.name
            )

        # then:

        self.assertIn("does not exist", log_dst.output[0])
        self.assertEqual(
            {"project_descriptors": [{"build_root_dir_rel_path": "."}]}, state_value
        )

    @patch(
        f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_stderr_log_level_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_run_mode_arg_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_py_exec_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_file_abs_path_inited.__name__}.eval_own_state"
    )
    def test_state_env_conf_file_data_loaded_malformed(
        self,
        mock_state_local_conf_file_abs_path_inited,
        mock_state_input_py_exec_var_loaded,
        mock_state_input_run_mode_arg_loaded,
        mock_state_input_stderr_log_level_eval_finalized,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_env_conf_file_data_loaded.name,
        )

        mock_conf_file = "/mock/path/to/env_conf.json"
        mock_state_local_conf_file_abs_path_inited.return_value = mock_conf_file

        self.fs.create_file(mock_conf_file, contents="not a valid json")

        # when/then:
        with self.assertRaises(json.decoder.JSONDecodeError):
            self.env_ctx.state_graph.eval_state(
                EnvState.state_env_conf_file_data_loaded.name
            )
