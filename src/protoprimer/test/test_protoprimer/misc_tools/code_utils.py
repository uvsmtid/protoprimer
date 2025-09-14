import enum
import inspect
from typing import (
    Type,
    List,
    Union,
)


def _get_line_number_from_source(
    given_obj: Union[enum.Enum, Type],
    search_patterns: List[str],
    obj_name: str,
) -> int:
    """
    Helper function to get the line number of an object (enum item or class)
    in its source file based on a search pattern.
    """
    source_file_path = inspect.getsourcefile(
        given_obj.__class__ if isinstance(given_obj, enum.Enum) else given_obj
    )
    if not source_file_path:
        raise ValueError(f"Could not find source file for `{obj_name}` [{given_obj}]")

    with open(source_file_path, "r") as source_file:
        source_lines = source_file.readlines()

    for i, source_line in enumerate(source_lines):
        for search_pattern in search_patterns:
            if search_pattern in source_line:
                return i + 1

    raise ValueError(
        f"Could not find `{obj_name}` [{given_obj}] with any of patterns [{search_patterns}] in source file [{source_file_path}]"
    )


def get_enum_item_line_number(
    enum_item: enum.Enum,
) -> int:
    """
    Given an enum item, returns its line number in the source file.
    """
    item_name = enum_item.name
    search_pattern = f"{item_name} ="
    return _get_line_number_from_source(
        enum_item,
        [search_pattern],
        f"enum item",
    )


def get_class_line_number(
    given_class: type,
) -> int:
    """
    Given a class, returns its line number in the source file.
    """
    class_name = given_class.__name__
    search_patterns = [
        f"class {class_name}:",
        f"class {class_name}(",
    ]
    return _get_line_number_from_source(
        given_class,
        search_patterns,
        f"class",
    )
