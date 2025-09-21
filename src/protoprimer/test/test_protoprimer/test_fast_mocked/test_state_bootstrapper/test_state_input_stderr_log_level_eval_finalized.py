import argparse
import logging
import sys
from unittest.mock import (
    patch,
)

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.line_number import line_no
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    SyntaxArg,
    Bootstrapper_state_args_parsed,
    Bootstrapper_state_default_stderr_log_handler_configured,
    EnvContext,
    EnvState,
)
from test_protoprimer.test_fast_mocked.misc_tools.mock_verifier import (
    assert_parent_states_mocked,
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
    def test_default_case(
        self,
        mock_state_args_parsed,
        mock_state_default_stderr_logger_configured,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_input_stderr_log_level_eval_finalized,
        )
        default_log_level = logging.NOTSET
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(default_log_level)
        mock_state_default_stderr_logger_configured.return_value = stderr_handler
        parsed_args = argparse.Namespace(
            **{SyntaxArg.dest_silent: None},
            **{SyntaxArg.dest_quiet: None},
            **{SyntaxArg.dest_verbose: None},
        )
        mock_state_args_parsed.return_value = parsed_args
        # when:
        actual = self.env_ctx.state_graph.eval_state(
            EnvState.state_input_stderr_log_level_eval_finalized.name
        )
        # then:
        self.assertEqual(default_log_level, actual)

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_default_stderr_log_handler_configured.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    def test_silent_only(
        self,
        mock_state_args_parsed,
        mock_state_default_stderr_logger_configured,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_input_stderr_log_level_eval_finalized,
        )
        default_log_level = logging.NOTSET
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(default_log_level)
        mock_state_default_stderr_logger_configured.return_value = stderr_handler
        parsed_args = argparse.Namespace(
            **{SyntaxArg.dest_silent: True},
            **{SyntaxArg.dest_quiet: None},
            **{SyntaxArg.dest_verbose: None},
        )
        mock_state_args_parsed.return_value = parsed_args
        # when:
        actual = self.env_ctx.state_graph.eval_state(
            EnvState.state_input_stderr_log_level_eval_finalized.name
        )
        # then:
        self.assertEqual(logging.CRITICAL + 1, actual)

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_default_stderr_log_handler_configured.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    def test_quiet_only(
        self,
        mock_state_args_parsed,
        mock_state_default_stderr_logger_configured,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_input_stderr_log_level_eval_finalized,
        )
        default_log_level = logging.NOTSET
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(default_log_level)
        mock_state_default_stderr_logger_configured.return_value = stderr_handler
        parsed_args = argparse.Namespace(
            **{SyntaxArg.dest_silent: None},
            **{SyntaxArg.dest_quiet: True},
            **{SyntaxArg.dest_verbose: None},
        )
        mock_state_args_parsed.return_value = parsed_args
        # when:
        actual = self.env_ctx.state_graph.eval_state(
            EnvState.state_input_stderr_log_level_eval_finalized.name
        )
        # then:
        self.assertEqual(logging.ERROR, actual)

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_default_stderr_log_handler_configured.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    def test_verbose_1_only(
        self,
        mock_state_args_parsed,
        mock_state_default_stderr_logger_configured,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_input_stderr_log_level_eval_finalized,
        )
        default_log_level = logging.NOTSET
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(default_log_level)
        mock_state_default_stderr_logger_configured.return_value = stderr_handler
        parsed_args = argparse.Namespace(
            **{SyntaxArg.dest_silent: None},
            **{SyntaxArg.dest_quiet: None},
            **{SyntaxArg.dest_verbose: 1},
        )
        mock_state_args_parsed.return_value = parsed_args
        # when:
        actual = self.env_ctx.state_graph.eval_state(
            EnvState.state_input_stderr_log_level_eval_finalized.name
        )
        # then:
        self.assertEqual(logging.DEBUG, actual)

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_default_stderr_log_handler_configured.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    def test_quiet_overrides_verbose(
        self,
        mock_state_args_parsed,
        mock_state_default_stderr_logger_configured,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_input_stderr_log_level_eval_finalized,
        )
        default_log_level = logging.NOTSET
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(default_log_level)
        mock_state_default_stderr_logger_configured.return_value = stderr_handler
        parsed_args = argparse.Namespace(
            **{SyntaxArg.dest_silent: None},
            **{SyntaxArg.dest_quiet: True},
            **{SyntaxArg.dest_verbose: 3},
        )
        mock_state_args_parsed.return_value = parsed_args
        # when:
        actual = self.env_ctx.state_graph.eval_state(
            EnvState.state_input_stderr_log_level_eval_finalized.name
        )
        # then:
        self.assertEqual(logging.ERROR, actual)

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_default_stderr_log_handler_configured.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    def test_silent_overrides_quiet_and_verbose(
        self,
        mock_state_args_parsed,
        mock_state_default_stderr_logger_configured,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_input_stderr_log_level_eval_finalized,
        )
        default_log_level = logging.NOTSET
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(default_log_level)
        mock_state_default_stderr_logger_configured.return_value = stderr_handler
        parsed_args = argparse.Namespace(
            **{SyntaxArg.dest_silent: True},
            **{SyntaxArg.dest_quiet: True},
            **{SyntaxArg.dest_verbose: 3},
        )
        mock_state_args_parsed.return_value = parsed_args
        # when:
        actual = self.env_ctx.state_graph.eval_state(
            EnvState.state_input_stderr_log_level_eval_finalized.name
        )
        # then:
        self.assertEqual(logging.CRITICAL + 1, actual)
