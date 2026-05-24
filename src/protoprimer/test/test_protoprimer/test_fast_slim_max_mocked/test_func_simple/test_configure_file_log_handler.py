import logging
from unittest.mock import patch

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import DefaultFileLogFormatter
from metaprimer.script_lib import configure_file_log_handler


def test_relationship():
    assert_test_module_name_embeds_str(configure_file_log_handler.__name__)


@patch("metaprimer.script_lib.logger")
def test_configure_file_log_handler(
    mock_logger,
    tmp_path,
):
    # given:

    log_level = logging.DEBUG
    file_path = str(tmp_path / "test.log")

    # when:

    log_handler = configure_file_log_handler(
        file_path,
        log_level,
    )

    # then:

    assert isinstance(log_handler, logging.FileHandler)
    mock_logger.addHandler.assert_called_once_with(log_handler)
    assert isinstance(log_handler.formatter, DefaultFileLogFormatter)
    assert log_handler.level == log_level

    log_handler.close()
