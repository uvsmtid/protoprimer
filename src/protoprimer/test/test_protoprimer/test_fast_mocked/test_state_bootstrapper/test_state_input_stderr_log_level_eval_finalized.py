import argparse
import logging
import os
import sys
from unittest.mock import (
    patch,
)

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.mock_verifier import (
    assert_parent_states_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_args_parsed,
    Bootstrapper_state_default_stderr_log_handler_configured,
    Bootstrapper_state_input_stderr_log_level_var_loaded,
    EnvContext,
    EnvState,
    EnvVar,
    SyntaxArg,
)


# noinspection PyPep8Naming
class ThisTestClass(BasePyfakefsTestClass):

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = EnvContext()

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_str(
            EnvState.state_input_stderr_log_level_eval_finalized.name
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_default_stderr_log_handler_configured.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_var_loaded.__name__}.eval_own_state"
    )
    def test_default_case(
        self,
        mock_state_input_stderr_log_level_var_loaded,
        mock_state_args_parsed,
        mock_state_default_stderr_logger_configured,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_input_stderr_log_level_eval_finalized.name,
        )
        default_log_level = logging.NOTSET
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(default_log_level)
        mock_state_default_stderr_logger_configured.return_value = stderr_handler
        mock_state_input_stderr_log_level_var_loaded.return_value = default_log_level
        parsed_args = argparse.Namespace(
            **{SyntaxArg.dest_silent: None},
            **{SyntaxArg.dest_quiet: None},
            **{SyntaxArg.dest_verbose: None},
        )
        mock_state_args_parsed.return_value = parsed_args
        # when:
        state_value = self.env_ctx.state_graph.eval_state(
            EnvState.state_input_stderr_log_level_eval_finalized.name
        )
        # then:
        self.assertEqual(default_log_level, state_value)

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_default_stderr_log_handler_configured.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_var_loaded.__name__}.eval_own_state"
    )
    def test_silent_only(
        self,
        mock_state_input_stderr_log_level_var_loaded,
        mock_state_args_parsed,
        mock_state_default_stderr_logger_configured,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_input_stderr_log_level_eval_finalized.name,
        )
        default_log_level = logging.NOTSET
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(default_log_level)
        mock_state_default_stderr_logger_configured.return_value = stderr_handler
        mock_state_input_stderr_log_level_var_loaded.return_value = default_log_level
        parsed_args = argparse.Namespace(
            **{SyntaxArg.dest_silent: True},
            **{SyntaxArg.dest_quiet: None},
            **{SyntaxArg.dest_verbose: None},
        )
        mock_state_args_parsed.return_value = parsed_args
        # when:
        state_value = self.env_ctx.state_graph.eval_state(
            EnvState.state_input_stderr_log_level_eval_finalized.name
        )
        # then:
        self.assertEqual(logging.CRITICAL + 1, state_value)

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_default_stderr_log_handler_configured.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_var_loaded.__name__}.eval_own_state"
    )
    def test_quiet_only(
        self,
        mock_state_input_stderr_log_level_var_loaded,
        mock_state_args_parsed,
        mock_state_default_stderr_logger_configured,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_input_stderr_log_level_eval_finalized.name,
        )
        default_log_level = logging.NOTSET
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(default_log_level)
        mock_state_default_stderr_logger_configured.return_value = stderr_handler
        mock_state_input_stderr_log_level_var_loaded.return_value = default_log_level
        parsed_args = argparse.Namespace(
            **{SyntaxArg.dest_silent: None},
            **{SyntaxArg.dest_quiet: True},
            **{SyntaxArg.dest_verbose: None},
        )
        mock_state_args_parsed.return_value = parsed_args
        # when:
        state_value = self.env_ctx.state_graph.eval_state(
            EnvState.state_input_stderr_log_level_eval_finalized.name
        )
        # then:
        self.assertEqual(logging.ERROR, state_value)

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_default_stderr_log_handler_configured.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_var_loaded.__name__}.eval_own_state"
    )
    def test_verbose_1_only(
        self,
        mock_state_input_stderr_log_level_var_loaded,
        mock_state_args_parsed,
        mock_state_default_stderr_logger_configured,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_input_stderr_log_level_eval_finalized.name,
        )
        default_log_level = logging.NOTSET
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(default_log_level)
        mock_state_default_stderr_logger_configured.return_value = stderr_handler
        mock_state_input_stderr_log_level_var_loaded.return_value = default_log_level
        parsed_args = argparse.Namespace(
            **{SyntaxArg.dest_silent: None},
            **{SyntaxArg.dest_quiet: None},
            **{SyntaxArg.dest_verbose: 1},
        )
        mock_state_args_parsed.return_value = parsed_args
        # when:
        state_value = self.env_ctx.state_graph.eval_state(
            EnvState.state_input_stderr_log_level_eval_finalized.name
        )
        # then:
        self.assertEqual(logging.DEBUG, state_value)

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_default_stderr_log_handler_configured.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_var_loaded.__name__}.eval_own_state"
    )
    def test_quiet_overrides_verbose(
        self,
        mock_state_input_stderr_log_level_var_loaded,
        mock_state_args_parsed,
        mock_state_default_stderr_logger_configured,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_input_stderr_log_level_eval_finalized.name,
        )
        default_log_level = logging.NOTSET
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(default_log_level)
        mock_state_default_stderr_logger_configured.return_value = stderr_handler
        mock_state_input_stderr_log_level_var_loaded.return_value = default_log_level
        parsed_args = argparse.Namespace(
            **{SyntaxArg.dest_silent: None},
            **{SyntaxArg.dest_quiet: True},
            **{SyntaxArg.dest_verbose: 3},
        )
        mock_state_args_parsed.return_value = parsed_args
        # when:
        state_value = self.env_ctx.state_graph.eval_state(
            EnvState.state_input_stderr_log_level_eval_finalized.name
        )
        # then:
        self.assertEqual(logging.ERROR, state_value)

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_default_stderr_log_handler_configured.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_var_loaded.__name__}.eval_own_state"
    )
    def test_silent_overrides_quiet_and_verbose(
        self,
        mock_state_input_stderr_log_level_var_loaded,
        mock_state_args_parsed,
        mock_state_default_stderr_logger_configured,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_input_stderr_log_level_eval_finalized.name,
        )
        default_log_level = logging.NOTSET
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(default_log_level)
        mock_state_default_stderr_logger_configured.return_value = stderr_handler
        mock_state_input_stderr_log_level_var_loaded.return_value = default_log_level
        parsed_args = argparse.Namespace(
            **{SyntaxArg.dest_silent: True},
            **{SyntaxArg.dest_quiet: True},
            **{SyntaxArg.dest_verbose: 3},
        )
        mock_state_args_parsed.return_value = parsed_args
        # when:
        state_value = self.env_ctx.state_graph.eval_state(
            EnvState.state_input_stderr_log_level_eval_finalized.name
        )
        # then:
        self.assertEqual(logging.CRITICAL + 1, state_value)

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_default_stderr_log_handler_configured.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_var_loaded.__name__}.eval_own_state"
    )
    @patch.dict(f"{os.__name__}.environ", {}, clear=True)
    def test_env_var_updated_after_eval(
        self,
        mock_state_input_stderr_log_level_var_loaded,
        mock_state_args_parsed,
        mock_state_default_stderr_logger_configured,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_input_stderr_log_level_eval_finalized.name,
        )
        default_log_level = logging.NOTSET
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(default_log_level)
        mock_state_default_stderr_logger_configured.return_value = stderr_handler
        mock_state_input_stderr_log_level_var_loaded.return_value = default_log_level
        parsed_args = argparse.Namespace(
            **{SyntaxArg.dest_silent: None},
            **{SyntaxArg.dest_quiet: True},
            **{SyntaxArg.dest_verbose: None},
        )
        mock_state_args_parsed.return_value = parsed_args
        # when:
        state_value = self.env_ctx.state_graph.eval_state(
            EnvState.state_input_stderr_log_level_eval_finalized.name
        )
        # then:
        self.assertEqual(logging.ERROR, state_value)
        self.assertEqual(
            os.environ[EnvVar.var_PROTOPRIMER_STDERR_LOG_LEVEL.value],
            logging.getLevelName(logging.ERROR),
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_default_stderr_log_handler_configured.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_var_loaded.__name__}.eval_own_state"
    )
    def test_verbose_2_only(
        self,
        mock_state_input_stderr_log_level_var_loaded,
        mock_state_args_parsed,
        mock_state_default_stderr_logger_configured,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_input_stderr_log_level_eval_finalized.name,
        )
        default_log_level = logging.INFO
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(default_log_level)
        mock_state_default_stderr_logger_configured.return_value = stderr_handler
        mock_state_input_stderr_log_level_var_loaded.return_value = default_log_level
        parsed_args = argparse.Namespace(
            **{SyntaxArg.dest_silent: None},
            **{SyntaxArg.dest_quiet: None},
            **{SyntaxArg.dest_verbose: 2},
        )
        mock_state_args_parsed.return_value = parsed_args
        # when:
        state_value = self.env_ctx.state_graph.eval_state(
            EnvState.state_input_stderr_log_level_eval_finalized.name
        )
        # then:
        self.assertEqual(logging.NOTSET, state_value)
