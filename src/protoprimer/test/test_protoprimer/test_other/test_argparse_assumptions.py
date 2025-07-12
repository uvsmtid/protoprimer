import os
import sys
from unittest.mock import patch

from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    ArgConst,
    init_arg_parser,
    PythonExecutable,
)
from local_test.base_test_class import BaseTestClass


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
