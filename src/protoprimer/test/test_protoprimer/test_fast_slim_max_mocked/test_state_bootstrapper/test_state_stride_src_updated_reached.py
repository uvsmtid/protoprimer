import argparse
from unittest.mock import patch

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.mock_verifier import (
    assert_parent_states_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_args_parsed,
    Bootstrapper_state_input_py_exec_var_loaded,
    Bootstrapper_state_input_start_id_var_loaded,
    Bootstrapper_state_proto_code_file_abs_path_inited,
    Bootstrapper_state_proto_code_updated,
    EnvContext,
    EnvState,
    ParsedArg,
    RunMode,
    StateStride,
)


# noinspection PyPep8Naming
class ThisTestClass(BasePyfakefsTestClass):

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = EnvContext()

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_str(
            EnvState.state_stride_src_updated_reached.name
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_updated.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_run_mode_arg_loaded.__name__}.eval_own_state"
    )
    @patch(f"{primer_kernel.__name__}.switch_python")
    def test_not_yet_at_required_python(
        self,
        mock_switch_python,
        mock_state_input_run_mode_arg_loaded,
        mock_state_local_venv_dir_abs_path_inited,
        mock_state_proto_code_file_abs_path_inited,
        mock_state_proto_code_updated,
        mock_state_args_parsed,
        mock_state_input_start_id_var_loaded,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_stride_src_updated_reached.name,
        )

        mock_state_args_parsed.return_value = argparse.Namespace(
            **{
                ParsedArg.name_reinstall.value: False,
            }
        )
        mock_state_input_start_id_var_loaded.return_value = "mock_start_id"

        mock_state_proto_code_file_abs_path_inited.return_value = "path/to/whatever"

        mock_state_proto_code_updated.return_value = True

        self.env_ctx.state_stride = StateStride.stride_py_unknown

        mock_state_input_run_mode_arg_loaded.return_value = RunMode.mode_prime
        mock_state_local_venv_dir_abs_path_inited.return_value = "/path/to/venv"
        self.fs.create_file("/path/to/venv/bin/python")

        # when:

        self.env_ctx.state_graph.eval_state(
            EnvState.state_stride_src_updated_reached.name
        )

        # then:

        mock_switch_python.assert_called_once_with(
            curr_python_path="/path/to/venv/bin/python",
            next_py_exec=StateStride.stride_src_updated,
            next_python_path="/path/to/venv/bin/python",
            start_id="mock_start_id",
            proto_code_abs_file_path=mock_state_proto_code_file_abs_path_inited.return_value,
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_updated.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_run_mode_arg_loaded.__name__}.eval_own_state"
    )
    @patch(f"{primer_kernel.__name__}.switch_python")
    def test_already_required_python(
        self,
        mock_switch_python,
        mock_state_input_run_mode_arg_loaded,
        mock_state_local_venv_dir_abs_path_inited,
        mock_state_proto_code_file_abs_path_inited,
        mock_state_proto_code_updated,
        mock_state_args_parsed,
        mock_state_input_start_id_var_loaded,
    ):
        """
        UC_90_98_17_93.run_under_venv.md
        """

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_stride_src_updated_reached.name,
        )

        mock_state_args_parsed.return_value = argparse.Namespace(
            **{
                ParsedArg.name_reinstall.value: False,
            }
        )
        mock_state_input_start_id_var_loaded.return_value = "mock_start_id"

        mock_state_proto_code_file_abs_path_inited.return_value = "path/to/whatever"

        mock_state_proto_code_updated.return_value = False

        self.env_ctx.state_stride = StateStride.stride_src_updated

        mock_state_input_run_mode_arg_loaded.return_value = RunMode.mode_prime
        mock_state_local_venv_dir_abs_path_inited.return_value = "/path/to/venv"

        # when:

        self.env_ctx.state_graph.eval_state(
            EnvState.state_stride_src_updated_reached.name
        )

        # then:

        mock_switch_python.assert_not_called()
