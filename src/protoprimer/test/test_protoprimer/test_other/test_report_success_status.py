from io import StringIO
from unittest.mock import patch

from local_test.base_test_class import BaseTestClass
from local_test.line_number import line_no
from protoprimer.primer_kernel import (
    EnvContext,
)


class ThisTestClass(BaseTestClass):

    def test_report_success_status(self):

        test_cases = [
            (
                line_no(),
                True,
                "SUCCESS",
            ),
            (
                line_no(),
                False,
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
