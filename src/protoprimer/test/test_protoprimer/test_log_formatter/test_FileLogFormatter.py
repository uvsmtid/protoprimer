import datetime
import logging
from unittest.mock import Mock

from freezegun import freeze_time

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import FileLogFormatter


def test_relationship():
    assert_test_module_name_embeds_str(
        FileLogFormatter.__name__,
    )


@freeze_time("2025-01-18 12:00:00")
def test_format_file_log():
    # given
    formatter = FileLogFormatter()
    record = logging.LogRecord(
        "test_name",
        logging.INFO,
        "/path/to/test.py",
        123,
        "Test message",
        None,
        None,
    )
    record.created = datetime.datetime.now(datetime.timezone.utc).timestamp()
    record.process = 12345
    # This attribute is added by the PythonExecutableFilter
    record.py_exec_name = "test_exec"
    record.state_stride = "test_stride"

    # when
    formatted_log = formatter.format(record)

    # then
    expected = "2025-01-18T12:00:00.000Z pid:12345 INFO py:test_exec s:test_stride test.py:123 Test message"
    assert formatted_log == expected
