from io import StringIO
from unittest.mock import (
    patch,
    MagicMock,
)

from local_test.base_test_class import BaseTestClass
from local_test.line_number import line_no
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_default_stderr_log_handler_configured,
    Bootstrapper_state_process_status_initialized,
    EnvContext,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        EnvContext.print_status_line.__name__,
    )


class ThisTestClass(BaseTestClass):

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_default_stderr_log_handler_configured.__name__}._eval_state_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_process_status_initialized.__name__}._eval_state_once"
    )
    def test_print_status_line(
        self,
        mock_state_process_status_initialized,
        mock_state_default_stderr_log_handler_configured,
    ):

        test_cases = [
            (
                line_no(),
                0,
                "SUCCESS",
            ),
            (
                line_no(),
                1,
                "FAILURE",
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    given_success_status,
                    expected_status_keyword,
                ) = test_case

                # given:

                env_ctx = EnvContext()

                mock_stderr_handler = MagicMock()
                mock_stderr_handler.level = 0
                mock_state_default_stderr_log_handler_configured.return_value = (
                    mock_stderr_handler
                )
                mock_state_process_status_initialized.return_value = 0

                # when:

                with patch("sys.stderr", new=StringIO()) as fake_stderr:
                    env_ctx.print_status_line(given_success_status)

                # then:

                stderr_text = fake_stderr.getvalue()
                self.assertIn(
                    expected_status_keyword,
                    stderr_text,
                )
