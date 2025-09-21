from io import StringIO
from unittest.mock import patch

from local_test.base_test_class import BaseTestClass
from local_test.line_number import line_no
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    EnvContext,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        EnvContext.report_success_status.__name__,
    )


class ThisTestClass(BaseTestClass):

    def test_report_success_status(self):

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

                # when:

                with patch("sys.stderr", new=StringIO()) as fake_stderr:
                    env_ctx.report_success_status(given_success_status)

                # then:

                stderr_text = fake_stderr.getvalue()
                self.assertIn(
                    expected_status_keyword,
                    stderr_text,
                )
