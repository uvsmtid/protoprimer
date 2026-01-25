import datetime
import logging
from unittest.mock import Mock

from freezegun import freeze_time

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import StderrLogFormatter, TermColor


def test_relationship():
    assert_test_module_name_embeds_str(
        StderrLogFormatter.__name__,
    )


def _create_log_record(level, msg):
    record = logging.LogRecord(
        "test_name",
        level,
        "/path/to/test.py",
        123,
        msg,
        None,
        None,
    )
    record.created = datetime.datetime.now(datetime.timezone.utc).timestamp()
    record.process = 12345
    record.py_exec_name = "test_exec"
    record.state_stride = "test_stride"
    return record


@freeze_time("2025-01-18 12:00:00")
def test_format_stderr_default_verbosity():
    # given
    formatter = StderrLogFormatter(verbosity_level=logging.WARNING)
    record = _create_log_record(logging.WARNING, "Test message")

    # when
    formatted_log = formatter.format(record)

    # then
    expected_msg = "WARNING Test message"
    expected_color = StderrLogFormatter.color_set.get("WARNING")
    expected = f"{expected_color}{expected_msg}{TermColor.reset_style.value}"
    assert formatted_log == expected


@freeze_time("2025-01-18 12:00:00")
def test_format_stderr_info_verbosity():
    # given
    formatter = StderrLogFormatter(verbosity_level=logging.INFO)
    record = _create_log_record(logging.INFO, "Test message")

    # when
    formatter.set_verbosity_level(logging.INFO)
    formatted_log = formatter.format(record)

    # then
    expected_msg = (
        "12:00:00.000Z pid:12345 INFO py:test_exec s:test_stride Test message"
    )
    expected_color = StderrLogFormatter.color_set.get("INFO")
    expected = f"{expected_color}{expected_msg}{TermColor.reset_style.value}"
    assert formatted_log == expected


@freeze_time("2025-01-18 12:00:00")
def test_format_stderr_debug_verbosity():
    # given
    formatter = StderrLogFormatter(verbosity_level=logging.DEBUG)
    record = _create_log_record(logging.DEBUG, "Test message")

    # when
    formatter.set_verbosity_level(logging.DEBUG)
    formatted_log = formatter.format(record)

    # then
    expected_msg = "2025-01-18T12:00:00.000Z pid:12345 DEBUG py:test_exec s:test_stride test.py:123 Test message"
    expected_color = StderrLogFormatter.color_set.get("DEBUG")
    expected = f"{expected_color}{expected_msg}{TermColor.reset_style.value}"
    assert formatted_log == expected


def test_set_verbosity_level():
    # given
    formatter = StderrLogFormatter(verbosity_level=logging.WARNING)
    assert formatter.verbosity_level == logging.WARNING

    # when
    formatter.set_verbosity_level(logging.DEBUG)

    # then
    assert formatter.verbosity_level == logging.DEBUG
