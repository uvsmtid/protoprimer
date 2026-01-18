import datetime
import logging
from unittest.mock import Mock

from freezegun import freeze_time

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import UtcTimeFormatter


def test_relationship():
    assert_test_module_name_embeds_str(
        UtcTimeFormatter.__name__,
    )


@freeze_time("2025-01-18 12:00:00")
def test_format_time_with_date_and_time():
    # given
    formatter = UtcTimeFormatter(print_date=True, print_time=True)
    record = Mock(spec=logging.LogRecord)
    record.created = datetime.datetime.now(datetime.timezone.utc).timestamp()

    # when
    formatted_time = formatter.formatTime(record)

    # then
    assert formatted_time == "2025-01-18T12:00:00.000Z"


@freeze_time("2025-01-18 12:00:00")
def test_format_time_with_date_only():
    # given
    formatter = UtcTimeFormatter(print_date=True, print_time=False)
    record = Mock(spec=logging.LogRecord)
    record.created = datetime.datetime.now(datetime.timezone.utc).timestamp()

    # when
    formatted_time = formatter.formatTime(record)

    # then
    assert formatted_time == "2025-01-18"


@freeze_time("2025-01-18 12:00:00")
def test_format_time_with_time_only():
    # given
    formatter = UtcTimeFormatter(print_date=False, print_time=True)
    record = Mock(spec=logging.LogRecord)
    record.created = datetime.datetime.now(datetime.timezone.utc).timestamp()

    # when
    formatted_time = formatter.formatTime(record)

    # then
    assert formatted_time == "12:00:00.000Z"


@freeze_time("2025-01-18 12:00:00")
def test_format_time_with_neither_date_nor_time():
    # given
    formatter = UtcTimeFormatter(print_date=False, print_time=False)
    record = Mock(spec=logging.LogRecord)
    record.created = datetime.datetime.now(datetime.timezone.utc).timestamp()

    # when
    formatted_time = formatter.formatTime(record)

    # then
    assert formatted_time == ""
