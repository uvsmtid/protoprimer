import argparse
from unittest.mock import patch

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import str2bool


def test_relationship():
    assert_test_module_name_embeds_str(
        str2bool.__name__,
    )


@pytest.mark.parametrize(
    "input_value",
    [
        "true",
        "t",
        "yes",
        "y",
        "1",
        "TRUE",
        "T",
        "YES",
        "Y",
    ],
)
def test_str2bool_true(input_value):
    # given:
    # A string that should result in True.

    # when:
    result = str2bool(input_value)

    # then:
    assert result is True


@pytest.mark.parametrize(
    "input_value",
    [
        "false",
        "f",
        "no",
        "n",
        "0",
        "FALSE",
        "F",
        "NO",
        "N",
    ],
)
def test_str2bool_false(input_value):
    # given:
    # A string that should result in False.

    # when:
    result = str2bool(input_value)

    # then:
    assert result is False


def test_str2bool_boolean_true():
    # given:
    # A boolean True value.

    # when:
    result = str2bool(True)

    # then:
    assert result is True


def test_str2bool_boolean_false():
    # given:
    # A boolean False value.

    # when:
    result = str2bool(False)

    # then:
    assert result is False


def test_str2bool_invalid_string():
    # given:
    # An invalid string.
    invalid_string = "invalid"

    # when/then:
    with pytest.raises(argparse.ArgumentTypeError) as exc_info:
        str2bool(invalid_string)

    # then:
    assert "[bool] value expected." in str(exc_info.value)
