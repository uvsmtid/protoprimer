import argparse
import io
import os
import sys
from unittest.mock import patch

from local_test.base_test_class import BaseTestClass
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    ArgConst,
    CommandArg,
    init_arg_parser,
    PythonExecutable,
    RunMode,
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
            ArgConst.arg_py_exec,
            PythonExecutable.py_exec_arbitrary.name,
            ArgConst.arg_py_exec,
            PythonExecutable.py_exec_required.name,
            ArgConst.arg_py_exec,
            PythonExecutable.py_exec_venv.name,
        ]

        # when:

        with patch.object(sys, "argv", test_args):
            arg_parser = init_arg_parser()
            parsed_args = arg_parser.parse_args()

        # then:

        assert (
            getattr(
                parsed_args,
                CommandArg.name_py_exec.value,
            )
            == PythonExecutable.py_exec_venv.name
        )

    def test_multiple_mutually_exclusive_options(self):

        # given:

        test_args = [
            os.path.basename(primer_kernel.__file__),
            ArgConst.arg_mode_prime,
            ArgConst.arg_mode_wizard,
        ]

        # when:

        with patch.object(sys, "argv", test_args):
            arg_parser = init_arg_parser()
            with patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
                with self.assertRaises(SystemExit) as exc_ctx:
                    arg_parser.parse_args(args=test_args)
                self.assertEqual(exc_ctx.exception.code, 2)
                self.assertIn("not allowed with argument", mock_stderr.getvalue())
