import argparse
import os
import sys
from unittest.mock import patch

from pyfakefs.fake_filesystem_unittest import TestCase as PyfakefsTestCase

import protoprimer
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    ArgConst,
    Bootstrapper_state_client_dir_path_configured,
    Bootstrapper_state_parsed_args,
    Bootstrapper_state_py_exec_selected,
    Bootstrapper_state_py_exec_updated_protoprimer_package_reached,
    Bootstrapper_state_proto_kernel_dir_path,
    ConfConstEnv,
    ConfConstGeneral,
    EnvContext,
    EnvState,
    get_path_to_curr_python,
    PythonExecutable,
    read_text_file,
)
from test_support import assert_test_module_name_embeds_str


# noinspection PyPep8Naming
class ThisTestClass(PyfakefsTestCase):

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = EnvContext()

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_str(EnvState.state_proto_kernel_updated.name)

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_proto_kernel_dir_path.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_dir_path_configured.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_selected.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_parsed_args.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.install_editable_package",
    )
    @patch(f"{primer_kernel.__name__}.os.execv")
    def test_state_proto_kernel_updated(
        self,
        mock_execv,
        mock_install_editable_package,
        mock_state_parsed_args,
        mock_state_py_exec_selected,
        mock_state_client_dir_path_configured,
        mock_state_script_dir_path,
    ):

        # given:
        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        script_dir = os.path.join(
            mock_client_dir,
            "cmd",
        )
        script_path = os.path.join(
            script_dir,
            # TODO: be able to configure it:
            ConfConstGeneral.default_proto_kernel_basename,
        )
        # script copy:
        self.fs.create_file(
            script_path,
        )
        # script orig (in fake filesystem):
        self.fs.create_file(
            protoprimer.primer_kernel.__file__,
            # Not real code, just 1000 empty lines:
            contents="\n" * 1000,
        )
        mock_state_script_dir_path.return_value = script_dir

        mock_state_parsed_args.return_value = argparse.Namespace(
            py_exec=PythonExecutable.py_exec_venv.name,
        )

        mock_state_py_exec_selected.return_value = PythonExecutable.py_exec_venv

        mock_state_client_dir_path_configured.return_value = mock_client_dir

        self.fs.create_file(os.path.join(mock_client_dir, "src", "setup.py"))

        # when:
        self.env_ctx.bootstrap_state(EnvState.state_proto_kernel_updated.name)

        # then:
        mock_install_editable_package.assert_called_once_with(
            os.path.join(
                mock_client_dir,
                "src",
            ),
            [
                "test",
            ],
        )
        script_obj = self.fs.get_object(script_path)
        self.assertIn(
            ConfConstGeneral.func_get_proto_kernel_generated_boilerplate(
                protoprimer.primer_kernel
            ),
            script_obj.contents,
        )
        mock_execv.assert_called_once_with(
            get_path_to_curr_python(),
            [
                get_path_to_curr_python(),
                *sys.argv,
                ArgConst.arg_py_exec,
                PythonExecutable.py_exec_updated_protoprimer_package.name,
            ],
        )
