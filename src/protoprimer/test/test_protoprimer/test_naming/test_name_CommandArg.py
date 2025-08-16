from __future__ import annotations

import enum

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import CommandArg
from test_protoprimer.test_naming.naming_metadata import (
    AbstractMeta,
    NameCategory,
)
from test_protoprimer.test_naming.naming_test_base import NamingTestBase


class ArgMeta(AbstractMeta):

    def __init__(
        self,
        command_arg: CommandArg,
        name_category: NameCategory,
    ):
        self.command_arg: CommandArg = command_arg
        self.name_category: NameCategory = name_category

    def get_prod_item(self):
        return self.command_arg

    def extract_prod_item_value_name(self) -> str:
        return self.command_arg.value

    def get_name(self):
        return self.command_arg.value

    def get_category(self):
        return self.name_category


class ArgName(enum.Enum):

    name_proto_code = ArgMeta(
        CommandArg.name_proto_code,
        NameCategory.category_path_arg_value,
    )

    name_local_env = ArgMeta(
        CommandArg.name_local_env,
        NameCategory.category_path_arg_value,
    )

    name_ref_root = ArgMeta(
        CommandArg.name_ref_root,
        NameCategory.category_path_arg_value,
    )

    name_py_exec = ArgMeta(
        CommandArg.name_py_exec,
        NameCategory.category_named_arg_value,
    )

    name_primer_runtime = ArgMeta(
        CommandArg.name_primer_runtime,
        NameCategory.category_named_arg_value,
    )

    name_run_mode = ArgMeta(
        CommandArg.name_run_mode,
        NameCategory.category_named_arg_value,
    )

    name_wizard_stage = ArgMeta(
        CommandArg.name_wizard_stage,
        NameCategory.category_named_arg_value,
    )

    name_target_state = ArgMeta(
        CommandArg.name_target_state,
        NameCategory.category_named_arg_value,
    )


class TestArgName(NamingTestBase):
    prod_enum = CommandArg
    test_enum = ArgName
    enum_prefix: str = "name_"

    def test_module_naming(self):
        assert_test_module_name_embeds_str(
            self.prod_enum.__name__,
        )
