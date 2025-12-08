import argparse
import io
import os
import sys
from unittest.mock import patch

from local_test.base_test_class import BaseTestClass
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    init_arg_parser,
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
            os.path.basename(primer_kernel.__file__),
            SyntaxArg.arg_env,
            "first",
            SyntaxArg.arg_env,
            "second",
            SyntaxArg.arg_env,
            "third",
        ]

        # when:

        with patch.object(sys, "argv", test_args):
            arg_parser = init_arg_parser()
            parsed_args = arg_parser.parse_args()

        # then:

        assert (
            getattr(
                parsed_args,
                ParsedArg.name_selected_env_dir.value,
            )
            == "third"
        )

    def test_multiple_mutually_exclusive_options(self):

        # given:

        test_args = [
            os.path.basename(primer_kernel.__file__),
            SyntaxArg.arg_mode_prime,
            SyntaxArg.arg_mode_config,
        ]

        # when:

        with patch.object(sys, "argv", test_args):
            arg_parser = init_arg_parser()
            with patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
                with self.assertRaises(SystemExit) as exc_ctx:
                    arg_parser.parse_args(args=test_args)
                self.assertEqual(exc_ctx.exception.code, 2)
                self.assertIn("not allowed with argument", mock_stderr.getvalue())
