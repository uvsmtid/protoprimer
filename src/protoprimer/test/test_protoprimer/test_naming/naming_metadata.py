"""
This module defines naming metadata which enforces naming convention.
"""

from __future__ import annotations

import enum

from local_test.consistent_naming import verify_name_enum_order_in_name
from protoprimer.primer_kernel import (
    ConfLeap,
    FilesystemObject,
    PathName,
    PathType,
    ValueName,
)


class CompletedAction(enum.Enum):

    # Some value loaded:
    action_loaded = "loaded"

    # Some value verified:
    action_verified = "verified"

    # Some value finalized (for the given FT_89_41_35_82.conf_leap.md):
    action_finalized = "finalized"

    # Some value applied (become effective for the current runtime):
    action_applied = "applied"


class ValueSource(enum.Enum):
    """
    Each value may be specified: in the config, by env var, on the command line, etc.

    There is a general rule how the same value is overridden (defaults -> config -> env var -> CLI arg).

    However, this process is more complicated during bootstrap - override may happen more than once.
    For example, the log level may be overridden twice (first default by global client config, then by local config).
    """

    # Default value = hard-coded value
    # (not specifically "hard"-coded, it may be "soft"-coded with any logic to set the initial value):
    value_def = "def"

    # A value set by an env var:
    value_var = "var"

    # A value provided by the command line args.
    value_arg = "arg"

    # A value loaded from the filesystem.
    value_fs = "fs"

    # A value evaluated based on multiple other values.
    value_eval = "eval"


class CategoryMeta:
    """
    Describes the category of the name (e.g., which enum items should be part of the name).
    """

    def __init__(
        self,
        name_enums: list[enum.Enum],
    ):
        self.name_enums: list[enum.Enum] = name_enums


class NameCategory(enum.Enum):
    """
    Depending on the category, different naming (the component set and the order) should apply.
    """

    # Some loaded data (e.g., command line args, config file, etc.)
    category_loaded_data = CategoryMeta(
        name_enums=[],
    )

    # Some value is read or computed:
    category_named_value = CategoryMeta(
        name_enums=[
            ConfLeap,
            ValueName,
            ValueSource,
            #
            CompletedAction,
        ],
    )

    # More specific than `category_named_value`: value representing a filesystem path is read or computed:
    category_path_value = CategoryMeta(
        name_enums=[
            # The first sub-list is synced with `category_path_action`:
            ConfLeap,
            PathName,
            FilesystemObject,
            PathType,
            ValueSource,
            #
            CompletedAction,
        ],
    )

    # Similar to `category_named_value` but for arg names:
    category_named_arg_value = CategoryMeta(
        name_enums=[
            ValueName,
        ],
    )

    # Similar:
    # to `category_named_arg_value` but for path names
    # to `category_path_value` but for arg names
    category_path_arg_value = CategoryMeta(
        name_enums=[
            PathName,
            FilesystemObject,
        ],
    )

    category_value_field = CategoryMeta(
        name_enums=[
            ConfLeap,
            ValueName,
        ],
    )

    category_path_field = CategoryMeta(
        name_enums=[
            ConfLeap,
            PathName,
            FilesystemObject,
            PathType,
        ],
    )

    # Every time a persistent state changes:
    # *   directly (e.g., via file modification)
    # *   indirectly (e.g., via external command)
    # Whether it actually causes a mutation is not strictly necessary, only a possibility.
    category_state_mutation = CategoryMeta(
        name_enums=[],
    )

    # Every time `PythonExecutable` is switched:
    category_python_exec = CategoryMeta(
        name_enums=[],
    )


class AbstractMeta:

    def get_prod_item(self):
        raise NotImplementedError

    def extract_prod_item_value_name(self) -> str:
        raise NotImplementedError

    def get_name(self) -> str:
        raise NotImplementedError

    def get_category(self) -> NameCategory:
        raise NotImplementedError


def verify_naming_convention(
    abstract_meta: AbstractMeta,
):
    naming_order = [
        f"${{{enum_type.__name__}}}"
        for enum_type in abstract_meta.get_category().value.name_enums
    ]
    given_name = abstract_meta.get_name()
    ret_val: enum.Enum | None = verify_name_enum_order_in_name(
        abstract_meta.get_category().value.name_enums,
        abstract_meta.get_name(),
    )
    if ret_val is not None:
        raise AssertionError(
            f"name [{given_name}] of category [{abstract_meta.get_category().name}] does not contain value from enum [{ret_val.__name__}] in the naming order [{'_'.join(naming_order)}]"
        )
