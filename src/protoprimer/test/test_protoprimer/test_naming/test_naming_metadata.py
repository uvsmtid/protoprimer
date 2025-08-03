import collections
import enum

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    CommandArg,
    ConfDst,
    ConfLeap,
    EnvVar,
    FilesystemObject,
    PathName,
    PathType,
    PrimerRuntime,
    RunMode,
    ValueName,
)
from test_protoprimer.test_naming import naming_metadata
from test_protoprimer.test_naming.naming_metadata import (
    ValueSource,
)


def verify_enum_string_uniqueness(
    enum_type: type[enum.Enum],
) -> None:
    seen_values = set()
    value_duplicates = set()
    for enum_item in enum_type:
        if enum_item.value in seen_values:
            value_duplicates.add(enum_item.value)
        seen_values.add(enum_item.value)

    if value_duplicates:
        raise AssertionError(
            f"Duplicate string values found in enum [{enum_type.__name__}]: {list(value_duplicates)}"
        )


def check_enum_string_uniqueness_across_all(enum_types: list[type[enum.Enum]]):
    """
    Helper function to check for unique string values across a list of Enum types.
    """
    all_values_to_enum_names = collections.defaultdict(list)

    for enum_type in enum_types:
        verify_enum_string_uniqueness(enum_type)

        for enum_item in enum_type:
            all_values_to_enum_names[enum_item.value].append(enum_type.__name__)

    # Check for duplicates across different enums:
    cross_enum_duplicates = {}
    for enum_value, enum_names in all_values_to_enum_names.items():
        if len(enum_names) > 1:
            cross_enum_duplicates[enum_value] = enum_names

    if cross_enum_duplicates:
        error_messages = []
        for enum_value, enum_names in cross_enum_duplicates.items():
            error_messages.append(
                f"Value '{enum_value}' is repeated in enums: {', '.join(enum_names)}"
            )

        raise AssertionError(
            "Duplicate string values found across different enums:\n"
            + "\n".join(error_messages)
        )


def test_relationship():
    assert_test_module_name_embeds_str(naming_metadata.__name__.rsplit(".", 1)[-1])


def test_enum_str_value_uniqueness():

    for enum_type in [
        ConfDst,
        ConfLeap,
        PrimerRuntime,
        PathName,
        ValueName,
        ValueSource,
    ]:
        verify_enum_string_uniqueness(enum_type)


def test_enum_str_value_uniqueness_across_multiple_enums():

    check_enum_string_uniqueness_across_all(
        [
            ConfLeap,
            PrimerRuntime,
            RunMode,
            FilesystemObject,
            PathType,
            EnvVar,
            ConfDst,
            ValueName,
            PathName,
            ValueSource,
        ]
        + (
            # Referencing, but not including - CommandArg duplicates values from ValueName:
            [CommandArg]
            if False
            else []
        ),
    )
