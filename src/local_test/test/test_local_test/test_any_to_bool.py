import argparse

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from local_test.case_condition import any_to_bool


def test_relationship():
    assert_test_module_name_embeds_str(
        any_to_bool.__name__,
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
def test_any_to_bool_true_from_str(input_value):
    # given:
    # A string that should result in True.

    # when:
    result = any_to_bool(input_value)

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
        "",
    ],
)
def test_any_to_bool_false_from_str(input_value):
    # given:
    # A string that should result in False.

    # when:
    result = any_to_bool(input_value)

    # then:
    assert result is False


def test_any_to_bool_true_from_bool():
    # given:
    # A boolean True value.

    # when:
    result = any_to_bool(True)

    # then:
    assert result is True


def test_any_to_bool_false_from_bool():
    # given:
    # A boolean False value.

    # when:
    result = any_to_bool(False)

    # then:
    assert result is False


def test_any_to_bool_false_from_none():
    # given:
    # A None value.

    # when:
    result = any_to_bool(None)

    # then:
    assert result is False


@pytest.mark.parametrize(
    "input_value",
    [
        123,
        0.0,
        [],
        {},
    ],
)
def test_any_to_bool_invalid_type(input_value):
    # given:
    # An invalid type.

    # when/then:
    with pytest.raises(argparse.ArgumentTypeError) as exc_info:
        any_to_bool(input_value)

    # then:
    assert f"Unable to convert type [{type(input_value)}] to [{bool.__name__}]" in str(
        exc_info.value
    )
