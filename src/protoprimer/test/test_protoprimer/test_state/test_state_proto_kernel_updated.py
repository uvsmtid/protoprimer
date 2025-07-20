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
    Bootstrapper_state_client_ref_dir_abs_path_global,
    Bootstrapper_state_args_parsed,
    Bootstrapper_state_proto_kernel_code_file_abs_path_finalized,
    Bootstrapper_state_proto_kernel_code_dir_abs_path_finalized,
    Bootstrapper_state_py_exec_selected,
    Bootstrapper_state_py_exec_updated_protoprimer_package_reached,
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
        f"{primer_kernel.__name__}.{Bootstrapper_state_proto_kernel_code_file_abs_path_finalized.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_updated_protoprimer_package_reached.__name__}._bootstrap_once"
    )
    @patch(f"{primer_kernel.__name__}.os.execv")
    def test_state_proto_kernel_updated(
        self,
        mock_execv,
        mock_state_py_exec_updated_protoprimer_package_reached,
        mock_state_proto_kernel_code_file_abs_path_finalized,
    ):

        # given:

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        # proto_kernel copy:
        proto_kernel_abs_file_path = os.path.join(
            mock_client_dir,
            ConfConstGeneral.default_proto_kernel_basename,
        )
        self.fs.create_file(proto_kernel_abs_file_path)

        # proto_kernel orig (in fake filesystem):
        self.fs.create_file(
            protoprimer.primer_kernel.__file__,
            # Not real code, just 1000 empty lines:
            contents="\n" * 1000,
        )

        mock_state_py_exec_updated_protoprimer_package_reached.return_value = (
            PythonExecutable.py_exec_updated_protoprimer_package
        )

        mock_state_proto_kernel_code_file_abs_path_finalized.return_value = (
            proto_kernel_abs_file_path
        )

        # when:

        self.env_ctx.bootstrap_state(EnvState.state_proto_kernel_updated.name)

        # then:

        proto_kernel_obj = self.fs.get_object(proto_kernel_abs_file_path)
        self.assertIn(
            ConfConstGeneral.func_get_proto_kernel_generated_boilerplate(
                protoprimer.primer_kernel
            ),
            proto_kernel_obj.contents,
        )
