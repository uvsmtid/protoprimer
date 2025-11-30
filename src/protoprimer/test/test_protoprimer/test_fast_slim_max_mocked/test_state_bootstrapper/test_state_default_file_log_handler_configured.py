import logging
import os
from unittest.mock import patch

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.mock_verifier import assert_parent_states_mocked
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_args_parsed,
    Bootstrapper_state_derived_local_log_dir_abs_path_eval_finalized,
    Bootstrapper_state_input_start_id_var_loaded,
    Bootstrapper_state_input_stderr_log_level_eval_finalized,
    EnvContext,
    EnvState,
    PythonExecutableFilter,
    RegularFormatter,
)


# noinspection PyPep8Naming
class ThisTestClass(BasePyfakefsTestClass):

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = EnvContext()
        self.mock_log_dir = "/mock_log_dir"
        self.mock_start_id = "mock_start_id"

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_str(
            EnvState.state_default_file_log_handler_configured.name
        )

    @patch("sys.argv", ["/path/to/script.py"])
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_derived_local_log_dir_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_eval_finalized.__name__}.eval_own_state"
    )
    def test_success_creation(
        self,
        mock_state_input_stderr_log_level_eval_finalized,
        mock_state_derived_local_log_dir_abs_path_eval_finalized,
        mock_state_args_parsed,
        mock_state_input_start_id_var_loaded,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_default_file_log_handler_configured.name,
        )
        mock_state_input_start_id_var_loaded.return_value = self.mock_start_id
        mock_state_args_parsed.return_value = primer_kernel.argparse.Namespace()
        mock_state_derived_local_log_dir_abs_path_eval_finalized.return_value = (
            self.mock_log_dir
        )
        mock_state_input_stderr_log_level_eval_finalized.return_value = logging.INFO
        self.fs.create_dir(self.mock_log_dir)

        # when:
        file_handler = self.env_ctx.state_graph.eval_state(
            EnvState.state_default_file_log_handler_configured.name
        )

        # then:
        self.assertIsInstance(file_handler, logging.FileHandler)

        expected_log_file = os.path.join(
            self.mock_log_dir, f"script.py.{self.mock_start_id}.log"
        )
        self.assertEqual(file_handler.baseFilename, expected_log_file)
        self.assertTrue(self.fs.exists(expected_log_file))

        self.assertEqual(file_handler.level, logging.INFO)
        self.assertIsInstance(file_handler.formatter, RegularFormatter)

        self.assertTrue(
            any(isinstance(f, PythonExecutableFilter) for f in file_handler.filters)
        )
        self.assertIn(file_handler, logging.getLogger().handlers)

    @patch("sys.argv", ["/path/to/script.py"])
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_derived_local_log_dir_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_eval_finalized.__name__}.eval_own_state"
    )
    def test_log_level_lower_than_default(
        self,
        mock_state_input_stderr_log_level_eval_finalized,
        mock_state_derived_local_log_dir_abs_path_eval_finalized,
        mock_state_args_parsed,
        mock_state_input_start_id_var_loaded,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_default_file_log_handler_configured.name,
        )
        mock_state_input_start_id_var_loaded.return_value = self.mock_start_id
        mock_state_args_parsed.return_value = primer_kernel.argparse.Namespace()
        mock_state_derived_local_log_dir_abs_path_eval_finalized.return_value = (
            self.mock_log_dir
        )
        # Stderr log level is lower (more verbose) than the default file log level (INFO)
        mock_state_input_stderr_log_level_eval_finalized.return_value = logging.DEBUG
        self.fs.create_dir(self.mock_log_dir)

        # when:
        file_handler = self.env_ctx.state_graph.eval_state(
            EnvState.state_default_file_log_handler_configured.name
        )

        # then:
        # File log level should be set to the more verbose level
        self.assertEqual(file_handler.level, logging.DEBUG)

    @patch("sys.argv", ["/path/to/script.py"])
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_derived_local_log_dir_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_eval_finalized.__name__}.eval_own_state"
    )
    def test_log_level_higher_than_default(
        self,
        mock_state_input_stderr_log_level_eval_finalized,
        mock_state_derived_local_log_dir_abs_path_eval_finalized,
        mock_state_args_parsed,
        mock_state_input_start_id_var_loaded,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_default_file_log_handler_configured.name,
        )
        mock_state_input_start_id_var_loaded.return_value = self.mock_start_id
        mock_state_args_parsed.return_value = primer_kernel.argparse.Namespace()
        mock_state_derived_local_log_dir_abs_path_eval_finalized.return_value = (
            self.mock_log_dir
        )
        # Stderr log level is higher (less verbose) than the default file log level (INFO)
        mock_state_input_stderr_log_level_eval_finalized.return_value = logging.WARNING
        self.fs.create_dir(self.mock_log_dir)

        # when:
        file_handler = self.env_ctx.state_graph.eval_state(
            EnvState.state_default_file_log_handler_configured.name
        )

        # then:
        # File log level should remain at the default (INFO)
        self.assertEqual(file_handler.level, logging.INFO)
