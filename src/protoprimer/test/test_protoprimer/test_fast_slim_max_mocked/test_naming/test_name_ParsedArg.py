from __future__ import annotations

import enum

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    CommandAction,
    FilesystemObject,
    KeyWord,
    ParsedArg,
    PathName,
    ValueName,
)
from test_protoprimer.test_fast_slim_max_mocked.test_naming.naming_metadata import (
    AbstractMeta,
    NameCategory,
)
from test_protoprimer.test_fast_slim_max_mocked.test_naming.naming_test_base import (
    NamingTestBase,
)


class ArgMeta(AbstractMeta):

    def __init__(
        self,
        command_arg: ParsedArg,
        name_category: NameCategory,
        name_components: list[str],
    ):
        self.command_arg: ParsedArg = command_arg
        self.name_category: NameCategory = name_category
        self.name_components: list[str] = name_components

    def get_prod_item(self):
        return self.command_arg

    def extract_prod_item_value_name(self) -> str:
        return self.command_arg.value

    def get_name(self):
        return self.command_arg.value

    def get_category(self):
        return self.name_category

    def get_name_components(self) -> list[str]:
        return self.name_components


class ArgName(enum.Enum):

    name_selected_env_dir = ArgMeta(
        command_arg=ParsedArg.name_selected_env_dir,
        name_category=NameCategory.category_path_arg_value,
        name_components=[
            PathName.path_selected_env.value,
            FilesystemObject.fs_object_dir.value,
        ],
    )

    name_reinstall = ArgMeta(
        command_arg=ParsedArg.name_reinstall,
        name_category=NameCategory.category_named_arg_action,
        name_components=[
            KeyWord.key_do.value,
            CommandAction.action_reinstall.value,
        ],
    )

    name_command = ArgMeta(
        command_arg=ParsedArg.name_command,
        name_category=NameCategory.category_named_arg_action,
        name_components=[
            KeyWord.key_run.value,
            CommandAction.action_command.value,
        ],
    )

    name_exec_mode = ArgMeta(
        command_arg=ParsedArg.name_exec_mode,
        name_category=NameCategory.category_named_arg_value,
        name_components=[
            ValueName.value_exec_mode.value,
        ],
    )

    name_final_state = ArgMeta(
        command_arg=ParsedArg.name_final_state,
        name_category=NameCategory.category_named_arg_value,
        name_components=[
            ValueName.value_final_state.value,
        ],
    )


class TestParsedArgName(NamingTestBase):
    prod_enum = ParsedArg
    test_enum = ArgName
    enum_prefix: str = "name_"

    def test_module_naming(self):
        assert_test_module_name_embeds_str(
            self.prod_enum.__name__,
        )
