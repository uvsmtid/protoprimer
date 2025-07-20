import enum

from local_test.consistent_naming import verify_name_enum_order_in_name


class Color(enum.Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


class Shape(enum.Enum):
    CIRCLE = "circle"
    SQUARE = "square"
    TRIANGLE = "triangle"


class Size(enum.Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class Fruit(enum.Enum):
    APPLE = "apple"
    BANANA = "banana"
    ORANGE = "orange"


class Animal(enum.Enum):
    DOG = "dog"
    CAT = "cat"
    BIRD = "bird"


def test_success_simple_order():
    meta_types = [Color, Shape, Size]
    name_string = "The red circle is small."
    assert verify_name_enum_order_in_name(meta_types, name_string) is None


def test_fail_missing_meta_type():
    meta_types = [Color, Shape, Size]
    # `Shape` is missing:
    name_string = "The red object is small."
    assert verify_name_enum_order_in_name(meta_types, name_string) is not None


def test_fail_incorrect_order():
    meta_types = [Color, Shape, Size]
    # `Shape` appears before `Color`:
    name_string = "A circle that is red and small."
    assert verify_name_enum_order_in_name(meta_types, name_string) is not None


def test_empty_meta_types_list():
    meta_types = []
    name_string = "Any string will do."
    assert verify_name_enum_order_in_name(meta_types, name_string) is None


def test_empty_name_string_with_meta_types():
    meta_types = [Color]
    name_string = ""
    assert verify_name_enum_order_in_name(meta_types, name_string) is not None
