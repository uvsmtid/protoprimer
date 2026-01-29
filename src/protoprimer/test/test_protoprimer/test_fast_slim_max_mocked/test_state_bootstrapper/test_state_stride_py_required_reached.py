import argparse
import os
from unittest.mock import patch

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.mock_verifier import (
    assert_parent_states_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_args_parsed,
    Bootstrapper_state_default_file_log_handler_configured,
    Bootstrapper_state_input_py_exec_var_loaded,
    Bootstrapper_state_input_start_id_var_loaded,
    Bootstrapper_state_local_conf_file_abs_path_inited,
    Bootstrapper_state_local_tmp_dir_abs_path_inited,
    Bootstrapper_state_local_venv_dir_abs_path_inited,
    Bootstrapper_state_proto_code_file_abs_path_inited,
    Bootstrapper_state_required_python_file_abs_path_inited,
    ConfConstEnv,
    ConfConstGeneral,
    EnvContext,
    EnvState,
    ParsedArg,
    StateStride,
)

mock_client_dir = "/mock_client_dir"
state_proto_code_file_abs_path_inited = os.path.join(
    mock_client_dir,
    ConfConstGeneral.default_proto_code_basename,
)
target_dst_dir_path = "target_dst_dir"

non_default_file_abs_path_python = "/oct/bin/python3"
non_default_dir_abs_path_venv = "/another/venv"


# noinspection PyPep8Naming
class ThisTestClass(BasePyfakefsTestClass):

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = EnvContext()

        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        self.fs.create_file(state_proto_code_file_abs_path_inited)

        self.fs.create_dir(target_dst_dir_path)

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_str(
            EnvState.state_stride_py_required_reached.name
        )

    def test_assumptions_used_in_other_tests(self):
        self.assertNotEqual(
            non_default_file_abs_path_python,
            ConfConstEnv.default_file_abs_path_python,
        )

    ####################################################################################################################
    @patch.dict(
        os.environ,
        {
            primer_kernel.EnvVar.var_PROTOPRIMER_PY_EXEC.value: StateStride.stride_py_arbitrary.name
        },
        clear=True,
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_tmp_dir_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_default_file_log_handler_configured.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_required_python_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.get_path_to_curr_python",
        return_value=ConfConstEnv.default_file_abs_path_python,
    )
    @patch(f"{primer_kernel.__name__}.os.execve")
    @patch(f"{primer_kernel.__name__}.venv.create")
    @patch(
        f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_run_mode_arg_loaded.__name__}.eval_own_state"
    )
    def test_success_on_arbitrary_py_exec_outside_venv(
        self,
        mock_input_run_mode_arg_loaded,
        mock_venv_create,
        mock_execve,
        mock_get_path_to_curr_python,
        mock_state_required_python_file_abs_path_inited,
        mock_state_local_venv_dir_abs_path_inited,
        mock_state_local_conf_file_abs_path_inited,
        mock_state_proto_code_file_abs_path_inited,
        mock_state_args_parsed,
        mock_state_default_file_log_handler_configured,
        mock_state_local_tmp_dir_abs_path_inited,
        mock_state_input_start_id_var_loaded,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_stride_py_required_reached.name,
        )

        mock_state_args_parsed.return_value = argparse.Namespace(
            **{
                ParsedArg.name_reinstall.value: False,
            }
        )
        mock_state_input_start_id_var_loaded.return_value = "mock_start_id"
        mock_state_proto_code_file_abs_path_inited.return_value = "any/path"

        # Make sure `path_to_curr_python` != `configured python`:
        mock_state_required_python_file_abs_path_inited.return_value = (
            "/a/different/python"
        )

        # Make sure `is_sub_path` is false:
        mock_state_local_venv_dir_abs_path_inited.return_value = (
            "/not/the/parent/of/current/python"
        )

        mock_state_local_conf_file_abs_path_inited.return_value = "any/path"

        # when:

        self.env_ctx.state_graph.eval_state(
            EnvState.state_stride_py_required_reached.name
        )

        # then:

        # With `stride_py_arbitrary`, we expect `execve` to be called to switch `python`.
        mock_execve.assert_called_once()
        mock_venv_create.assert_not_called()
        mock_get_path_to_curr_python.assert_called_once()

    @patch.dict(
        os.environ,
        {
            primer_kernel.EnvVar.var_PROTOPRIMER_PY_EXEC.value: StateStride.stride_py_required.name
        },
        clear=True,
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_tmp_dir_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_default_file_log_handler_configured.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_required_python_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.get_path_to_curr_python",
        return_value=ConfConstEnv.default_file_abs_path_python,
    )
    @patch(f"{primer_kernel.__name__}.os.execve")
    @patch(f"{primer_kernel.__name__}.venv.create")
    @patch(
        f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_run_mode_arg_loaded.__name__}.eval_own_state"
    )
    def test_skip_if_py_exec_is_already_required(
        self,
        mock_input_run_mode_arg_loaded,
        mock_venv_create,
        mock_execve,
        mock_get_path_to_curr_python,
        mock_state_required_python_file_abs_path_inited,
        mock_state_local_venv_dir_abs_path_inited,
        mock_state_local_conf_file_abs_path_inited,
        mock_state_proto_code_file_abs_path_inited,
        mock_state_args_parsed,
        mock_state_default_file_log_handler_configured,
        mock_state_local_tmp_dir_abs_path_inited,
        mock_state_input_start_id_var_loaded,
    ):
        # given:
        self.env_ctx.state_stride = StateStride.stride_py_required

        # when:
        actual_result = self.env_ctx.state_graph.eval_state(
            EnvState.state_stride_py_required_reached.name
        )

        # then:
        self.assertEqual(
            StateStride.stride_py_required,
            actual_result,
        )
        mock_execve.assert_not_called()
        mock_venv_create.assert_not_called()
        mock_get_path_to_curr_python.assert_not_called()

    @patch.dict(
        os.environ,
        {
            primer_kernel.EnvVar.var_PROTOPRIMER_PY_EXEC.value: StateStride.stride_py_arbitrary.name
        },
        clear=True,
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_tmp_dir_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_default_file_log_handler_configured.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_required_python_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.get_path_to_curr_python",
        return_value=non_default_file_abs_path_python,
    )
    @patch(f"{primer_kernel.__name__}.os.execve")
    @patch(f"{primer_kernel.__name__}.venv.create")
    @patch(
        f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_run_mode_arg_loaded.__name__}.eval_own_state"
    )
    def test_success_if_correct_python_is_already_used(
        self,
        mock_input_run_mode_arg_loaded,
        mock_venv_create,
        mock_execve,
        mock_get_path_to_curr_python,
        mock_state_required_python_file_abs_path_inited,
        mock_state_local_venv_dir_abs_path_inited,
        mock_state_local_conf_file_abs_path_inited,
        mock_state_proto_code_file_abs_path_inited,
        mock_state_args_parsed,
        mock_state_default_file_log_handler_configured,
        mock_state_local_tmp_dir_abs_path_inited,
        mock_state_input_start_id_var_loaded,
    ):
        # given:
        mock_state_required_python_file_abs_path_inited.return_value = (
            non_default_file_abs_path_python
        )
        mock_state_local_venv_dir_abs_path_inited.return_value = (
            non_default_dir_abs_path_venv
        )

        # when:
        actual_result = self.env_ctx.state_graph.eval_state(
            EnvState.state_stride_py_required_reached.name
        )

        # then:
        self.assertEqual(
            StateStride.stride_py_required,
            actual_result,
        )
        mock_execve.assert_not_called()
        mock_venv_create.assert_not_called()
        mock_get_path_to_curr_python.assert_called_once()
