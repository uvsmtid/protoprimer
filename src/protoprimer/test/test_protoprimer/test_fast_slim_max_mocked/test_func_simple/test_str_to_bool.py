import argparse

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import str_to_bool


def test_relationship():
    assert_test_module_name_embeds_str(
        str_to_bool.__name__,
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
def test_str_to_bool_true(input_value):
    # given:
    # A string that should result in True.

    # when:
    result = str_to_bool(input_value)

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
def test_str_to_bool_false(input_value):
    # given:
    # A string that should result in False.

    # when:
    result = str_to_bool(input_value)

    # then:
    assert result is False


def test_str_to_bool_invalid_string():
    # given:
    # An invalid string.
    invalid_string = "invalid"

    # when/then:
    with pytest.raises(argparse.ArgumentTypeError) as exc_info:
        str_to_bool(invalid_string)

    # then:
    assert "[bool]-like value expected." in str(exc_info.value)
