import logging
from unittest.mock import patch

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import DefaultStderrLogFormatter
from metaprimer.script_lib import configure_stderr_log_handler


def test_relationship():
    assert_test_module_name_embeds_str(configure_stderr_log_handler.__name__)


@patch("metaprimer.script_lib.logger")
def test_configure_stderr_log_handler(mock_logger):
    # given:

    log_level = logging.INFO

    # when:

    log_handler = configure_stderr_log_handler(log_level)

    # then:

    assert isinstance(log_handler, logging.StreamHandler)
    mock_logger.setLevel.assert_called_once_with(logging.NOTSET)
    mock_logger.addHandler.assert_called_once_with(log_handler)
    assert isinstance(log_handler.formatter, DefaultStderrLogFormatter)
    assert log_handler.formatter.verbosity_level == log_level
    assert log_handler.level == log_level
