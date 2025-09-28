import logging
import os
import sys
from unittest.mock import (
    call,
    patch,
)

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    ConfConstInput,
    log_python_context,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        log_python_context.__name__,
    )


@patch("protoprimer.primer_kernel.logger")
def test_log_python_context(mock_logger):
    # given:
    log_level = logging.DEBUG
    virtual_env = "/path/to/venv"
    python_path = "/path/to/python"
    sys_prefix = "/path/to/prefix"

    # when:
    with patch.dict(
        os.environ,
        {
            ConfConstInput.ext_env_var_VIRTUAL_ENV: virtual_env,
            ConfConstInput.ext_env_var_PYTHONPATH: python_path,
        },
    ):
        with patch.object(sys, "prefix", sys_prefix):
            log_python_context(log_level)

    # then:
    expected_calls = [
        call(log_level, f"`{ConfConstInput.ext_env_var_VIRTUAL_ENV}`: {virtual_env}"),
        call(
            log_level,
            f"`{ConfConstInput.ext_env_var_PATH}`: {os.environ.get(ConfConstInput.ext_env_var_PATH, None)}",
        ),
        call(log_level, f"`{ConfConstInput.ext_env_var_PYTHONPATH}`: {python_path}"),
        call(log_level, f"`sys.path`: {sys.path}"),
        call(log_level, f"`sys.prefix`: {sys_prefix}"),
    ]
    mock_logger.log.assert_has_calls(expected_calls, any_order=True)
