from __future__ import annotations

import enum

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import ParsedArg
from test_protoprimer.test_fast_mocked.test_naming.naming_metadata import (
    AbstractMeta,
    NameCategory,
)
from test_protoprimer.test_fast_mocked.test_naming.naming_test_base import (
    NamingTestBase,
)


class ArgMeta(AbstractMeta):

    def __init__(
        self,
        command_arg: ParsedArg,
        name_category: NameCategory,
    ):
        self.command_arg: ParsedArg = command_arg
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
        ParsedArg.name_proto_code,
        NameCategory.category_path_arg_value,
    )

    name_reinstall = ArgMeta(
        ParsedArg.name_reinstall,
        NameCategory.category_named_arg_action,
    )

    name_command = ArgMeta(
        ParsedArg.name_command,
        NameCategory.category_named_arg_action,
    )

    name_py_exec = ArgMeta(
        ParsedArg.name_py_exec,
        NameCategory.category_named_arg_value,
    )

    name_primer_runtime = ArgMeta(
        ParsedArg.name_primer_runtime,
        NameCategory.category_named_arg_value,
    )

    name_start_id = ArgMeta(
        ParsedArg.name_start_id,
        NameCategory.category_named_arg_value,
    )

    name_run_mode = ArgMeta(
        ParsedArg.name_run_mode,
        NameCategory.category_named_arg_value,
    )

    name_wizard_stage = ArgMeta(
        ParsedArg.name_wizard_stage,
        NameCategory.category_named_arg_value,
    )

    name_final_state = ArgMeta(
        ParsedArg.name_final_state,
        NameCategory.category_named_arg_value,
    )


class TestParsedArgName(NamingTestBase):
    prod_enum = ParsedArg
    test_enum = ArgName
    enum_prefix: str = "name_"

    def test_module_naming(self):
        assert_test_module_name_embeds_str(
            self.prod_enum.__name__,
        )
