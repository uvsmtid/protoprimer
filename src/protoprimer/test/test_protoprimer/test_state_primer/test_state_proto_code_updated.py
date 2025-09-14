import os
from unittest.mock import patch

import protoprimer
from local_test.base_test_class import BasePyfakefsTestClass
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_input_proto_code_file_abs_path_eval_finalized,
    Bootstrapper_state_py_exec_updated_protoprimer_package_reached,
    ConfConstGeneral,
    EnvContext,
    EnvState,
    PythonExecutable,
)
from test_protoprimer.misc_tools.mock_verifier import assert_parent_states_mocked


# noinspection PyPep8Naming
class ThisTestClass(BasePyfakefsTestClass):

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = EnvContext()

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_str(EnvState.state_proto_code_updated.name)

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_proto_code_file_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_updated_protoprimer_package_reached.__name__}.eval_own_state"
    )
    @patch(f"{primer_kernel.__name__}.os.execv")
    def test_state_proto_code_updated(
        self,
        mock_execv,
        mock_state_py_exec_updated_protoprimer_package_reached,
        mock_state_input_proto_code_file_abs_path_eval_finalized,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_proto_code_updated,
        )

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        # proto_kernel copy:
        proto_code_abs_file_path = os.path.join(
            mock_client_dir,
            ConfConstGeneral.default_proto_code_basename,
        )
        self.fs.create_file(proto_code_abs_file_path)

        # proto_kernel orig (in fake filesystem):
        self.fs.create_file(
            protoprimer.primer_kernel.__file__,
            # Not real code, just 1000 empty lines:
            contents="\n" * 1000,
        )

        mock_state_py_exec_updated_protoprimer_package_reached.return_value = (
            PythonExecutable.py_exec_updated_protoprimer_package
        )

        mock_state_input_proto_code_file_abs_path_eval_finalized.return_value = (
            proto_code_abs_file_path
        )

        # when:

        self.env_ctx.state_graph.eval_state(EnvState.state_proto_code_updated.name)

        # then:

        proto_kernel_obj = self.fs.get_object(proto_code_abs_file_path)
        self.assertIn(
            ConfConstGeneral.func_get_proto_code_generated_boilerplate_single_header(
                protoprimer.primer_kernel
            ),
            proto_kernel_obj.contents,
        )
        self.assertIn(
            ConfConstGeneral.func_get_proto_code_generated_boilerplate_multiple_body(
                protoprimer.primer_kernel
            ),
            proto_kernel_obj.contents,
        )
