import argparse

from local_test.base_test_class import BaseTestClass
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    parse_args,
    ParsedArg,
    SyntaxArg,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        argparse.__name__,
    )


# noinspection PyMethodMayBeStatic
class ThisTestClass(BaseTestClass):

    def test_last_repeated_named_arg_overrides_previous(self):
        # given:
        test_args = [
            "prime",
            SyntaxArg.arg_env,
            "first",
            SyntaxArg.arg_env,
            "second",
            SyntaxArg.arg_env,
            "third",
        ]

        # when:
        parsed_args = parse_args(test_args)

        # then:
        self.assertEqual(
            "third",
            getattr(
                parsed_args,
                ParsedArg.name_selected_env_dir.value,
            ),
        )
