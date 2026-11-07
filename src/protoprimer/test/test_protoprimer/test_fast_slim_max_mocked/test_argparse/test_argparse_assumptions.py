import argparse

from local_test.base_test_class import BaseTestClass
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    _parse_args,
    _ParsedArg,
    _SyntaxArg,
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
            "boot",
            _SyntaxArg.arg_env,
            "first",
            _SyntaxArg.arg_env,
            "second",
            _SyntaxArg.arg_env,
            "third",
        ]

        # when:
        parsed_args = _parse_args(test_args)

        # then:
        self.assertEqual(
            "third",
            getattr(
                parsed_args,
                _ParsedArg.name_selected_env_dir.value,
            ),
        )
