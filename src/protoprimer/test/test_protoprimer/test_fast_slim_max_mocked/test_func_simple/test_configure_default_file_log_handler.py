import logging
import os
from unittest.mock import (
    patch,
)

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    DefaultFileLogFormatter,
    configure_default_file_log_handler,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        configure_default_file_log_handler.__name__,
    )


@patch("protoprimer.primer_kernel.logger")
@patch("logging.FileHandler")
@patch("os.makedirs")
def test_configure_default_file_log_handler(
    mock_makedirs,
    mock_file_handler_class,
    mock_logger,
):
    # given:

    log_file_abs_path = "/path/to/logfile.log"
    log_level = logging.DEBUG
    mock_handler = mock_file_handler_class.return_value

    # when:

    result = configure_default_file_log_handler(log_file_abs_path, log_level)

    # then:

    assert result == mock_handler
    mock_makedirs.assert_called_once_with(os.path.dirname(log_file_abs_path), exist_ok=True)
    mock_file_handler_class.assert_called_once_with(log_file_abs_path)

    # Verify formatter:
    new_formatter = mock_handler.setFormatter.call_args[0][0]
    assert isinstance(new_formatter, DefaultFileLogFormatter)

    mock_handler.setLevel.assert_called_once_with(log_level)
    mock_logger.addHandler.assert_called_once_with(mock_handler)
