import logging
from unittest.mock import (
    MagicMock,
    patch,
)

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    DefaultFileLogFormatter,
    StateStrideFilter,
    reconfigure_file_log_handler,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        reconfigure_file_log_handler.__name__,
    )


@patch("protoprimer.primer_kernel.logger")
def test_reconfigure_file_log_handler_when_no_matching_handler(
    mock_logger,
):
    # given:

    mock_logger.handlers = []

    # when:

    result = reconfigure_file_log_handler()

    # then:

    assert result is None


@patch("protoprimer.primer_kernel.logger")
def test_reconfigure_file_log_handler_when_handler_matches(
    mock_logger,
):
    # given:

    log_level = logging.DEBUG

    # We mock FileHandler because it's not a type we're patching in this test.
    mock_handler = MagicMock(spec=logging.FileHandler)

    # It must be an instance of DefaultFileLogFormatter.
    # We use a real instance to satisfy isinstance() checks.
    mock_formatter = DefaultFileLogFormatter()
    mock_handler.formatter = mock_formatter

    # It must be an instance of StateStrideFilter.
    # We use a real instance to satisfy isinstance() checks.
    mock_filter = StateStrideFilter()
    mock_handler.filters = [mock_filter]

    mock_logger.handlers = [mock_handler]

    # when:

    result = reconfigure_file_log_handler(log_level)

    # then:

    assert result == mock_handler

    # Verify that a new formatter was created and set:
    new_formatter = mock_handler.setFormatter.call_args[0][0]
    assert isinstance(new_formatter, DefaultFileLogFormatter)

    mock_handler.setLevel.assert_called_once_with(log_level)
    mock_handler.removeFilter.assert_called_once_with(mock_filter)
