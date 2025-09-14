import enum

from .code_utils import get_enum_item_line_number, get_class_line_number


class DummyEnumForTest(enum.Enum):
    FIRST_ITEM_FOR_TEST = 1
    SECOND_ITEM_FOR_TEST = 2
    THIRD_ITEM_FOR_TEST = 3


class BaseDummyClassForTest:
    pass


class DerivedDummyClassForTest(BaseDummyClassForTest):
    pass


def test_get_enum_item_line_number() -> None:
    assert get_enum_item_line_number(DummyEnumForTest.SECOND_ITEM_FOR_TEST) == 8


def test_get_class_line_number() -> None:
    assert get_class_line_number(DummyEnumForTest) == 6
    assert get_class_line_number(BaseDummyClassForTest) == 12
    assert get_class_line_number(DerivedDummyClassForTest) == 16
