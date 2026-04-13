import io
import json
import logging
import os
from logging import WARNING
from unittest.mock import patch

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.mock_verifier import (
    assert_parent_factories_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_input_exec_mode_arg_loaded,
    Bootstrapper_state_local_conf_file_abs_path_inited,
    EnvContext,
    EnvState,
    StateStride,
)


# noinspection PyPep8Naming
class ThisTestClass(BasePyfakefsTestClass):

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = EnvContext()

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_str(EnvState.state_env_conf_file_data_loaded.name)

    @patch(f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_stderr_log_level_eval_finalized.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_exec_mode_arg_loaded.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_file_abs_path_inited.__name__}.create_state_node")
    def test_state_env_conf_file_data_loaded_exists(
        self,
        mock_state_local_conf_file_abs_path_inited,
        mock_state_input_exec_mode_arg_loaded,
        mock_state_input_stderr_log_level_eval_finalized,
    ):

        # given:

        assert_parent_factories_mocked(
            self.env_ctx,
            EnvState.state_env_conf_file_data_loaded.name,
        )

        mock_conf_file = "/mock/path/to/env_conf.json"
        mock_state_local_conf_file_abs_path_inited.return_value.eval_own_state.return_value = mock_conf_file

        mock_data = {"test": "data"}
        self.fs.create_file(mock_conf_file, contents=json.dumps(mock_data))

        # when:

        state_value = self.env_ctx.state_graph.eval_state(EnvState.state_env_conf_file_data_loaded.name, self.env_ctx)

        # then:

        self.assertEqual(state_value, mock_data)

    @patch(f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_stderr_log_level_eval_finalized.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_exec_mode_arg_loaded.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_file_abs_path_inited.__name__}.create_state_node")
    def test_state_env_conf_file_data_loaded_missing(
        self,
        mock_state_local_conf_file_abs_path_inited,
        mock_state_input_exec_mode_arg_loaded,
        mock_state_input_stderr_log_level_eval_finalized,
    ):

        # given:

        assert_parent_factories_mocked(
            self.env_ctx,
            EnvState.state_env_conf_file_data_loaded.name,
        )

        mock_conf_file = "/mock/path/to/env_conf.json"
        self.fs.create_dir("/mock/path/to")
        mock_state_local_conf_file_abs_path_inited.return_value.eval_own_state.return_value = mock_conf_file

        self.assertFalse(os.path.exists(mock_conf_file))

        # when:
        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)
        logger = primer_kernel.logger
        logger.addHandler(handler)
        try:
            state_value = self.env_ctx.state_graph.eval_state(EnvState.state_env_conf_file_data_loaded.name, self.env_ctx)
        finally:
            logger.removeHandler(handler)

        # then:
        self.assertEqual({}, state_value)
        self.assertNotIn("does not exist", log_stream.getvalue())

    @patch(f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_stderr_log_level_eval_finalized.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_exec_mode_arg_loaded.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_file_abs_path_inited.__name__}.create_state_node")
    def test_state_env_conf_file_data_loaded_malformed(
        self,
        mock_state_local_conf_file_abs_path_inited,
        mock_state_input_exec_mode_arg_loaded,
        mock_state_input_stderr_log_level_eval_finalized,
    ):

        # given:

        assert_parent_factories_mocked(
            self.env_ctx,
            EnvState.state_env_conf_file_data_loaded.name,
        )

        mock_conf_file = "/mock/path/to/env_conf.json"
        mock_state_local_conf_file_abs_path_inited.return_value.eval_own_state.return_value = mock_conf_file

        self.fs.create_file(mock_conf_file, contents="not a valid json")

        # when/then:
        with self.assertRaises(json.decoder.JSONDecodeError):
            self.env_ctx.state_graph.eval_state(EnvState.state_env_conf_file_data_loaded.name, self.env_ctx)
