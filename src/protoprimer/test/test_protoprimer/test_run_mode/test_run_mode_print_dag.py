import os
import sys
from io import StringIO
from unittest.mock import patch

from local_test.base_test_class import BaseTestClass
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    ArgConst,
    EnvState,
    main,
    RunMode,
    SinkPrinterVisitor,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        ArgConst.name_run_mode,
    )
    assert_test_module_name_embeds_str(
        RunMode.print_dag.name,
    )


# noinspection PyMethodMayBeStatic
class ThisTestClass(BaseTestClass):

    def test_print_dag_no_parents(self):

        # given:

        given_state_name: str = EnvState.state_stderr_log_level_var.name

        test_args = [
            os.path.basename(primer_kernel.__file__),
            ArgConst.arg_run_mode,
            RunMode.print_dag.name,
            ArgConst.arg_state_name,
            given_state_name,
        ]

        # when:

        with patch("sys.stdout", new=StringIO()) as fake_stdout:
            with patch.object(sys, "argv", test_args):
                main()

        # then:

        stdout_text = fake_stdout.getvalue()
        self.assertEqual(
            stdout_text,
            f"{given_state_name}: {SinkPrinterVisitor.rendered_no_parents}" + "\n",
        )

    def test_print_dag_default(self):

        # given:

        test_args = [
            os.path.basename(primer_kernel.__file__),
            ArgConst.arg_run_mode,
            RunMode.print_dag.name,
        ]

        # when:

        with patch("sys.stdout", new=StringIO()) as fake_stdout:
            with patch.object(sys, "argv", test_args):
                main()

        # then:

        # do not assert huge output, if it does not fail, that is enough
