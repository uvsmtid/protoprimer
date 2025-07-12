import argparse
import os
import sys
from unittest.mock import patch

import protoprimer
from local_test.name_assertion import assert_test_module_name_embeds_str
from local_test.base_test_class import BasePyfakefsTestClass
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    ArgConst,
    Bootstrapper_state_client_dir_path_configured,
    Bootstrapper_state_args_parsed,
    Bootstrapper_state_proto_kernel_dir_path,
    Bootstrapper_state_py_exec_selected,
    ConfConstGeneral,
    EnvContext,
    EnvState,
    get_path_to_curr_python,
    PythonExecutable,
)


# noinspection PyPep8Naming
class ThisTestClass(BasePyfakefsTestClass):

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = EnvContext()

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_str(EnvState.state_proto_kernel_updated.name)

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_dir_path_configured.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_selected.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.install_editable_package",
    )
    @patch(f"{primer_kernel.__name__}.os.execv")
    def test_state_proto_kernel_updated(
        self,
        mock_execv,
        mock_install_editable_package,
        mock_state_args_parsed,
        mock_state_py_exec_selected,
        mock_state_client_dir_path_configured,
    ):

        # given:

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        # proto_kernel copy:
        proto_kernel_abs_path = os.path.join(
            mock_client_dir,
            ConfConstGeneral.default_proto_kernel_basename,
        )
        self.fs.create_file(proto_kernel_abs_path)

        # proto_kernel orig (in fake filesystem):
        self.fs.create_file(
            protoprimer.primer_kernel.__file__,
            # Not real code, just 1000 empty lines:
            contents="\n" * 1000,
        )

        mock_state_args_parsed.return_value = argparse.Namespace(
            **{
                ArgConst.name_py_exec: PythonExecutable.py_exec_venv.name,
                ArgConst.name_proto_kernel_abs_path: proto_kernel_abs_path,
            },
        )

        mock_state_py_exec_selected.return_value = PythonExecutable.py_exec_venv

        mock_state_client_dir_path_configured.return_value = mock_client_dir

        for distrib_name in [
            "local_repo",
            "local_test",
            "protoprimer",
        ]:
            self.fs.create_file(
                os.path.join(
                    mock_client_dir,
                    "src",
                    distrib_name,
                    "setup.py",
                )
            )

        # when:

        self.env_ctx.bootstrap_state(EnvState.state_proto_kernel_updated.name)

        # then:

        for distrib_name in [
            "local_repo",
            "local_test",
            "protoprimer",
        ]:
            mock_install_editable_package.assert_any_call(
                os.path.join(
                    mock_client_dir,
                    "src",
                    distrib_name,
                ),
                [],
            )
        self.assertEqual(
            3,
            mock_install_editable_package.call_count,
        )
        proto_kernel_obj = self.fs.get_object(proto_kernel_abs_path)
        self.assertIn(
            ConfConstGeneral.func_get_proto_kernel_generated_boilerplate(
                protoprimer.primer_kernel
            ),
            proto_kernel_obj.contents,
        )
        mock_execv.assert_called_once_with(
            get_path_to_curr_python(),
            [
                get_path_to_curr_python(),
                *sys.argv,
                ArgConst.arg_py_exec,
                PythonExecutable.py_exec_updated_protoprimer_package.name,
                ArgConst.arg_proto_kernel_abs_path,
                proto_kernel_abs_path,
            ],
        )
