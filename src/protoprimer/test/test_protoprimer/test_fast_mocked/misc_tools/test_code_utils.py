import enum

from test_protoprimer.test_fast_mocked.misc_tools.code_utils import (
    get_class_line_number,
    get_enum_item_line_number,
)


class DummyEnumForTest(enum.Enum):
    FIRST_ITEM_FOR_TEST = 1
    SECOND_ITEM_FOR_TEST = 2
    THIRD_ITEM_FOR_TEST = 3


class BaseDummyClassForTest:
    pass


class DerivedDummyClassForTest(BaseDummyClassForTest):
    pass


def test_get_enum_item_line_number() -> None:
    assert get_enum_item_line_number(DummyEnumForTest.SECOND_ITEM_FOR_TEST) == 11


def test_get_class_line_number() -> None:
    assert get_class_line_number(DummyEnumForTest) == 9
    assert get_class_line_number(BaseDummyClassForTest) == 15
    assert get_class_line_number(DerivedDummyClassForTest) == 19
