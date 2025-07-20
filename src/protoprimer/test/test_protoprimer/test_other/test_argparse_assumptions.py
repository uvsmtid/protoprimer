import argparse
import os
import sys
from unittest.mock import patch

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    ArgConst,
    init_arg_parser,
    PythonExecutable,
)
from local_test.base_test_class import BaseTestClass


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

        assert parsed_args.py_exec == PythonExecutable.py_exec_venv.name
