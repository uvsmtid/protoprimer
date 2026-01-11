import logging
from io import StringIO
from unittest.mock import (
    patch,
)

import pytest

from local_test.name_assertion import (
    assert_test_func_name_embeds_str,
    assert_test_module_name_embeds_str,
)
from protoprimer.primer_kernel import (
    EnvContext,
    EnvVar,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        EnvContext.print_exit_line.__name__,
    )


@pytest.mark.parametrize(
    "given_exit_code, given_test_failure, expected_status_keyword, stderr_log_level, expect_output",
    [
        (0, False, "SUCCESS", logging.WARNING, False),
        (0, False, "SUCCESS", logging.INFO, True),
        (0, True, "SUCCESS", logging.WARNING, False),
        (0, True, "SUCCESS", logging.INFO, True),
        (1, False, "TEST_EXIT", logging.WARNING, True),
        (1, True, "FAILURE", logging.WARNING, True),
    ],
)
def test_print_exit_line(
    given_exit_code,
    given_test_failure,
    expected_status_keyword,
    stderr_log_level,
    expect_output,
    monkeypatch,
):
    assert_test_func_name_embeds_str(
        EnvContext.print_exit_line.__name__,
    )

    # given:
    monkeypatch.setenv(
        EnvVar.var_PROTOPRIMER_STDERR_LOG_LEVEL.value,
        str(stderr_log_level),
    )
    env_ctx = EnvContext()

    # when:

    with patch("sys.stderr", new=StringIO()) as fake_stderr:
        env_ctx.print_exit_line(given_exit_code, test_failure=given_test_failure)

    # then:

    stderr_text = fake_stderr.getvalue()
    if expect_output:
        assert expected_status_keyword in stderr_text
        assert f"[{given_exit_code}]" in stderr_text
    else:
        assert not stderr_text
