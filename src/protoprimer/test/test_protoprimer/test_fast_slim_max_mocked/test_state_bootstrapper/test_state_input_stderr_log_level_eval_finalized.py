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
    ConfConstInput,
    EnvContext,
    EnvState,
    EnvVar,
    StderrLogFormatter,
    SyntaxArg,
)


# noinspection PyPep8Naming
class ThisTestClass(BasePyfakefsTestClass):

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = EnvContext()
        self.stderr_handler = logging.StreamHandler(sys.stderr)
        self.stderr_handler.setFormatter(
            StderrLogFormatter(
                verbosity_level=logging.WARNING,
            )
        )

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
    def test_default_case_no_flags_uses_default_from_var(
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
        self.stderr_handler.setLevel(default_log_level)
        mock_state_default_stderr_logger_configured.return_value = self.stderr_handler
        mock_state_input_stderr_log_level_var_loaded.return_value = default_log_level
        parsed_args = argparse.Namespace(
            **{SyntaxArg.dest_quiet: 0},
            **{SyntaxArg.dest_verbose: 0},
        )
        mock_state_args_parsed.return_value = parsed_args
        # when:
        state_value = self.env_ctx.state_graph.eval_state(
            EnvState.state_input_stderr_log_level_eval_finalized.name
        )
        # then:
        self.assertEqual(logging.INFO, state_value)

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_default_stderr_log_handler_configured.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_var_loaded.__name__}.eval_own_state"
    )
    def test_default_case_no_flags_uses_warning(
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
        default_log_level: int = getattr(
            logging,
            ConfConstInput.default_PROTOPRIMER_STDERR_LOG_LEVEL,
        )
        self.stderr_handler.setLevel(default_log_level)
        mock_state_default_stderr_logger_configured.return_value = self.stderr_handler
        mock_state_input_stderr_log_level_var_loaded.return_value = default_log_level
        parsed_args = argparse.Namespace(
            **{SyntaxArg.dest_quiet: 0},
            **{SyntaxArg.dest_verbose: 0},
        )
        mock_state_args_parsed.return_value = parsed_args
        # when:
        state_value = self.env_ctx.state_graph.eval_state(
            EnvState.state_input_stderr_log_level_eval_finalized.name
        )
        # then:
        self.assertEqual(logging.WARNING, state_value)

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_default_stderr_log_handler_configured.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_var_loaded.__name__}.eval_own_state"
    )
    def test_quiet_1_only(
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
        default_log_level: int = getattr(
            logging,
            ConfConstInput.default_PROTOPRIMER_STDERR_LOG_LEVEL,
        )
        self.stderr_handler.setLevel(default_log_level)
        mock_state_default_stderr_logger_configured.return_value = self.stderr_handler
        mock_state_input_stderr_log_level_var_loaded.return_value = default_log_level
        parsed_args = argparse.Namespace(
            **{SyntaxArg.dest_quiet: 1},
            **{SyntaxArg.dest_verbose: 0},
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
    def test_quiet_2_only(
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
        default_log_level: int = getattr(
            logging,
            ConfConstInput.default_PROTOPRIMER_STDERR_LOG_LEVEL,
        )
        self.stderr_handler.setLevel(default_log_level)
        mock_state_default_stderr_logger_configured.return_value = self.stderr_handler
        mock_state_input_stderr_log_level_var_loaded.return_value = default_log_level
        parsed_args = argparse.Namespace(
            **{SyntaxArg.dest_quiet: 2},
            **{SyntaxArg.dest_verbose: 0},
        )
        mock_state_args_parsed.return_value = parsed_args
        # when:
        state_value = self.env_ctx.state_graph.eval_state(
            EnvState.state_input_stderr_log_level_eval_finalized.name
        )
        # then:
        self.assertEqual(logging.CRITICAL, state_value)

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_default_stderr_log_handler_configured.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_var_loaded.__name__}.eval_own_state"
    )
    def test_quiet_5_only(
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
        default_log_level: int = getattr(
            logging,
            ConfConstInput.default_PROTOPRIMER_STDERR_LOG_LEVEL,
        )
        self.stderr_handler.setLevel(default_log_level)
        mock_state_default_stderr_logger_configured.return_value = self.stderr_handler
        mock_state_input_stderr_log_level_var_loaded.return_value = default_log_level
        parsed_args = argparse.Namespace(
            **{SyntaxArg.dest_quiet: 5},
            **{SyntaxArg.dest_verbose: 0},
        )
        mock_state_args_parsed.return_value = parsed_args
        # when:
        state_value = self.env_ctx.state_graph.eval_state(
            EnvState.state_input_stderr_log_level_eval_finalized.name
        )
        # then:
        self.assertEqual(80, state_value)

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
        default_log_level: int = getattr(
            logging,
            ConfConstInput.default_PROTOPRIMER_STDERR_LOG_LEVEL,
        )
        self.stderr_handler.setLevel(default_log_level)
        mock_state_default_stderr_logger_configured.return_value = self.stderr_handler
        mock_state_input_stderr_log_level_var_loaded.return_value = default_log_level
        parsed_args = argparse.Namespace(
            **{SyntaxArg.dest_quiet: 0},
            **{SyntaxArg.dest_verbose: 1},
        )
        mock_state_args_parsed.return_value = parsed_args
        # when:
        state_value = self.env_ctx.state_graph.eval_state(
            EnvState.state_input_stderr_log_level_eval_finalized.name
        )
        # then:
        self.assertEqual(logging.INFO, state_value)

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
        default_log_level: int = getattr(
            logging,
            ConfConstInput.default_PROTOPRIMER_STDERR_LOG_LEVEL,
        )
        self.stderr_handler.setLevel(default_log_level)
        mock_state_default_stderr_logger_configured.return_value = self.stderr_handler
        mock_state_input_stderr_log_level_var_loaded.return_value = default_log_level
        parsed_args = argparse.Namespace(
            **{SyntaxArg.dest_quiet: 0},
            **{SyntaxArg.dest_verbose: 2},
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
    def test_verbose_3_only(
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
        default_log_level: int = getattr(
            logging,
            ConfConstInput.default_PROTOPRIMER_STDERR_LOG_LEVEL,
        )
        self.stderr_handler.setLevel(default_log_level)
        mock_state_default_stderr_logger_configured.return_value = self.stderr_handler
        mock_state_input_stderr_log_level_var_loaded.return_value = default_log_level
        parsed_args = argparse.Namespace(
            **{SyntaxArg.dest_quiet: 0},
            **{SyntaxArg.dest_verbose: 3},
        )
        mock_state_args_parsed.return_value = parsed_args
        # when:
        state_value = self.env_ctx.state_graph.eval_state(
            EnvState.state_input_stderr_log_level_eval_finalized.name
        )
        # then:
        self.assertEqual(logging.NOTSET, state_value)

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_default_stderr_log_handler_configured.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_var_loaded.__name__}.eval_own_state"
    )
    def test_verbose_4_only(
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
        default_log_level: int = getattr(
            logging,
            ConfConstInput.default_PROTOPRIMER_STDERR_LOG_LEVEL,
        )
        self.stderr_handler.setLevel(default_log_level)
        mock_state_default_stderr_logger_configured.return_value = self.stderr_handler
        mock_state_input_stderr_log_level_var_loaded.return_value = default_log_level
        parsed_args = argparse.Namespace(
            **{SyntaxArg.dest_quiet: 0},
            **{SyntaxArg.dest_verbose: 4},
        )
        mock_state_args_parsed.return_value = parsed_args
        # when:
        state_value = self.env_ctx.state_graph.eval_state(
            EnvState.state_input_stderr_log_level_eval_finalized.name
        )
        # then:
        self.assertEqual(logging.NOTSET, state_value)

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_default_stderr_log_handler_configured.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_var_loaded.__name__}.eval_own_state"
    )
    def test_quiet_and_verbose(
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
        default_log_level: int = getattr(
            logging,
            ConfConstInput.default_PROTOPRIMER_STDERR_LOG_LEVEL,
        )
        self.stderr_handler.setLevel(default_log_level)
        mock_state_default_stderr_logger_configured.return_value = self.stderr_handler
        mock_state_input_stderr_log_level_var_loaded.return_value = default_log_level
        parsed_args = argparse.Namespace(
            **{SyntaxArg.dest_quiet: 2},
            **{SyntaxArg.dest_verbose: 1},
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
    @patch.dict(f"{os.__name__}.environ", {}, clear=True)
    def test_env_var_not_updated_read_only(
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
        default_log_level: int = getattr(
            logging,
            ConfConstInput.default_PROTOPRIMER_STDERR_LOG_LEVEL,
        )
        self.stderr_handler.setLevel(default_log_level)
        mock_state_default_stderr_logger_configured.return_value = self.stderr_handler
        mock_state_input_stderr_log_level_var_loaded.return_value = default_log_level
        parsed_args = argparse.Namespace(
            **{SyntaxArg.dest_quiet: 1},
            **{SyntaxArg.dest_verbose: 0},
        )
        mock_state_args_parsed.return_value = parsed_args

        # when:

        state_value = self.env_ctx.state_graph.eval_state(
            EnvState.state_input_stderr_log_level_eval_finalized.name
        )

        # then:

        self.assertEqual(logging.ERROR, state_value)
        self.assertIsNone(
            os.environ.get(EnvVar.var_PROTOPRIMER_STDERR_LOG_LEVEL.value, None)
        )
