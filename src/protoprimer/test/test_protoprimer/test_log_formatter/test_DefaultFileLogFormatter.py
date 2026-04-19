import datetime
import logging

from freezegun import freeze_time

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import DefaultFileLogFormatter


def test_relationship():
    assert_test_module_name_embeds_str(
        DefaultFileLogFormatter.__name__,
    )


@freeze_time("2025-01-18 12:00:00")
def test_format_file_log():
    # given:
    formatter = DefaultFileLogFormatter()
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

    # when:
    formatted_log = formatter.format(record)

    # then:
    expected = "2025-01-18T12:00:00.000Z pid:12345 INFO test.py:123 Test message"
    assert formatted_log == expected
