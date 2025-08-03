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
    ArgConst,
    Bootstrapper_state_args_parsed,
    Bootstrapper_state_default_stderr_log_handler_configured,
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
            EnvState.state_input_stderr_log_level_eval_finalized_gconf.name
        )

    def test_not_yet_at_required_python(
        self,
    ):

        default_log_level = logging.NOTSET

        test_cases = [
            (
                line_no(),
                None,
                None,
                None,
                default_log_level,
                "default case",
            ),
            (
                line_no(),
                True,
                None,
                None,
                logging.CRITICAL + 1,
                "silent only",
            ),
            (
                line_no(),
                None,
                True,
                None,
                logging.ERROR,
                "quiet only",
            ),
            (
                line_no(),
                None,
                None,
                0,
                default_log_level,
                "verbose 0 only",
            ),
            (
                line_no(),
                None,
                None,
                1,
                logging.DEBUG,
                "verbose 1 only",
            ),
            (
                line_no(),
                None,
                None,
                2,
                logging.NOTSET,
                "verbose 2 only",
            ),
            (
                line_no(),
                None,
                None,
                3,
                logging.NOTSET,
                "verbose 3 only",
            ),
            (
                line_no(),
                None,
                True,
                3,
                logging.ERROR,
                "quiet overrides verbose",
            ),
            (
                line_no(),
                True,
                True,
                3,
                logging.CRITICAL + 1,
                "silent overrides overrides quiet and verbose",
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    stderr_log_level_silent,
                    stderr_log_level_quiet,
                    stderr_log_level_verbose,
                    expected_state_input_stderr_log_level_eval_finalized_gconf,
                    case_comment,
                ) = test_case

                # given:

                self.env_ctx = EnvContext()

                stderr_handler = logging.StreamHandler(sys.stderr)
                stderr_handler.setLevel(default_log_level)

                parsed_args = argparse.Namespace(
                    **{ArgConst.dest_silent: stderr_log_level_silent},
                    **{ArgConst.dest_quiet: stderr_log_level_quiet},
                    **{ArgConst.dest_verbose: stderr_log_level_verbose},
                )

                # when:

                with patch(
                    f"{primer_kernel.__name__}.{Bootstrapper_state_default_stderr_log_handler_configured.__name__}._bootstrap_once"
                ) as mock_state_default_stderr_logger_configured:
                    mock_state_default_stderr_logger_configured.return_value = (
                        stderr_handler
                    )
                    with patch(
                        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}._bootstrap_once"
                    ) as mock_state_args_parsed:
                        mock_state_args_parsed.return_value = parsed_args
                        actual_state_input_stderr_log_level_eval_finalized_gconf = self.env_ctx.bootstrap_state(
                            EnvState.state_input_stderr_log_level_eval_finalized_gconf.name
                        )

                # then:

                self.assertEqual(
                    expected_state_input_stderr_log_level_eval_finalized_gconf,
                    actual_state_input_stderr_log_level_eval_finalized_gconf,
                )
