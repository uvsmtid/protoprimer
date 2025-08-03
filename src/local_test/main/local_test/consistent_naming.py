from __future__ import annotations

import enum


def verify_name_enum_order_in_name(
    name_enums: list[enum.Enum],
    given_name: str,
) -> enum.Enum | None:
    """
    This function verifies consistent naming.

    The naming is defined by a list of enums `name_enums`.
    The `given_name` should contain sub-strings from enum items of the `name_enums`
    once from each of the `name_enums` and in the same order specified them.

    @return: the first `name_enum` which items were not found in the `given_name`, otherwise, `None` (success).
    """
    current_search_start_index = 0

    for name_enum in name_enums:

        found_index: int = -1

        # Find the first matching string from the given enum `name_enum`:
        meta_item = list(name_enum)[0]
        for meta_item in name_enum:
            assert type(meta_item.value) is str
            found_index = given_name.find(meta_item.value, current_search_start_index)

            # ensure the found name component is the one separated by `_` (underscore):
            if found_index >= 1 and given_name[found_index - 1] != "_":
                found_index = -1

            if found_index >= 0:
                break

        if found_index == -1:
            return name_enum
        else:
            current_search_start_index = found_index + len(meta_item.value)

    return None
