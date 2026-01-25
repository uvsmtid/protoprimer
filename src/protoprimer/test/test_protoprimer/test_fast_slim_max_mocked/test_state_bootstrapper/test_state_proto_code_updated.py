import os
from unittest.mock import patch

import protoprimer
from local_test.base_test_class import BasePyfakefsTestClass
from local_test.mock_verifier import (
    assert_parent_states_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_proto_code_file_abs_path_inited,
    Bootstrapper_state_py_exec_deps_updated_reached,
    ConfConstGeneral,
    EnvContext,
    EnvState,
    PythonExecutable,
    RunMode,
)


# noinspection PyPep8Naming
class ThisTestClass(BasePyfakefsTestClass):

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = EnvContext()

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_str(EnvState.state_proto_code_updated.name)

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_deps_updated_reached.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_run_mode_arg_loaded.__name__}.eval_own_state"
    )
    @patch(f"{primer_kernel.__name__}.EnvContext.get_curr_py_exec")
    def test_state_proto_code_updated(
        self,
        mock_get_curr_py_exec,
        mock_state_input_run_mode_arg_loaded,
        mock_state_py_exec_deps_updated_reached,
        mock_state_proto_code_file_abs_path_inited,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_proto_code_updated.name,
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
        mock_get_curr_py_exec.return_value = PythonExecutable.py_exec_deps_updated

        mock_state_py_exec_deps_updated_reached.return_value = (
            PythonExecutable.py_exec_deps_updated
        )

        mock_state_proto_code_file_abs_path_inited.return_value = (
            proto_code_abs_file_path
        )
        mock_state_input_run_mode_arg_loaded.return_value = RunMode.mode_prime

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

    @patch(
        f"{primer_kernel.__name__}.is_venv",
        return_value=True,
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_deps_updated_reached.__name__}.eval_own_state"
    )
    @patch(f"{primer_kernel.__name__}.EnvContext.get_curr_py_exec")
    @patch(
        f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_run_mode_arg_loaded.__name__}.eval_own_state"
    )
    def test_import_error_when_protoprimer_is_missing(
        self,
        mock_state_input_run_mode_arg_loaded,
        mock_get_curr_py_exec,
        mock_state_py_exec_deps_updated_reached,
        mock_state_proto_code_file_abs_path_inited,
        mock_is_venv,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_proto_code_updated.name,
        )
        mock_get_curr_py_exec.return_value = PythonExecutable.py_exec_deps_updated

        fake_path = "/fake/path"
        self.fs.create_file(fake_path)
        mock_state_proto_code_file_abs_path_inited.return_value = fake_path
        mock_state_input_run_mode_arg_loaded.return_value = RunMode.mode_prime

        # when:
        with patch.dict("sys.modules", {"protoprimer": None}):
            with self.assertLogs(primer_kernel.logger, level="WARNING") as cm:
                result = self.env_ctx.state_graph.eval_state(
                    EnvState.state_proto_code_updated.name
                )

        # then:
        self.assertFalse(result)
        self.assertIn("Module `protoprimer` is missing in `venv`", cm.output[0])
