import logging
import sys
from unittest.mock import (
    patch,
)

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    DefaultStderrLogFormatter,
    configure_default_stderr_log_handler,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        configure_default_stderr_log_handler.__name__,
    )


@patch("protoprimer.primer_kernel.logger")
@patch("logging.StreamHandler")
def test_configure_default_stderr_log_handler(
    mock_stream_handler_class,
    mock_logger,
):
    # given:

    log_level = logging.INFO
    mock_handler = mock_stream_handler_class.return_value

    # when:

    result = configure_default_stderr_log_handler(log_level)

    # then:

    assert result == mock_handler
    mock_stream_handler_class.assert_called_once_with(sys.stderr)

    # Verify formatter:
    new_formatter = mock_handler.setFormatter.call_args[0][0]
    assert isinstance(new_formatter, DefaultStderrLogFormatter)
    assert new_formatter.verbosity_level == log_level

    mock_handler.setLevel.assert_called_once_with(log_level)
    mock_logger.addHandler.assert_called_once_with(mock_handler)
    mock_logger.setLevel.assert_called_once_with(logging.NOTSET)
