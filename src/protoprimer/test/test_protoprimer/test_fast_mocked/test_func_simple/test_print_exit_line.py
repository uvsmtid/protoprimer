from io import StringIO
from unittest.mock import (
    patch,
)

from local_test.base_test_class import BaseTestClass
from local_test.line_number import line_no
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    EnvContext,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        EnvContext.print_exit_line.__name__,
    )


class ThisTestClass(BaseTestClass):

    def test_print_status_line(
        self,
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
                    given_exit_code,
                    expected_status_keyword,
                ) = test_case

                # given:

                env_ctx = EnvContext()

                # when:

                with patch("sys.stderr", new=StringIO()) as fake_stderr:
                    env_ctx.print_exit_line(given_exit_code)

                # then:

                stderr_text = fake_stderr.getvalue()
                self.assertIn(
                    expected_status_keyword,
                    stderr_text,
                )
                self.assertIn(
                    f"[{given_exit_code}]",
                    stderr_text,
                )
