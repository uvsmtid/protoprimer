from __future__ import annotations

import enum


class ModeId(enum.Enum):
    """
    FT_78_72_23_04.backward_compatibility.md
    """

    new_tests_on_new_changes = "new_tests_on_new_changes"

    old_tests_on_new_changes = "old_tests_on_new_changes"

    old_proto_on_new_venv = "old_proto_on_new_venv"

    old_entry_on_new_proto = "old_entry_on_new_proto"
