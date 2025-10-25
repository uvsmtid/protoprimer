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
    Bootstrapper_state_input_proto_code_file_abs_path_eval_finalized,
    Bootstrapper_state_input_py_exec_var_loaded,
    Bootstrapper_state_input_start_id_var_loaded,
    Bootstrapper_state_input_wizard_stage_arg_loaded,
    Bootstrapper_state_proto_code_updated,
    EnvContext,
    EnvState,
    get_path_to_curr_python,
    ParsedArg,
    PythonExecutable,
    WizardStage,
)


# noinspection PyPep8Naming
class ThisTestClass(BasePyfakefsTestClass):

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = EnvContext()

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_str(
            EnvState.state_py_exec_updated_proto_code.name
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_wizard_stage_arg_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_py_exec_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_updated.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_proto_code_file_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    @patch(f"{primer_kernel.__name__}.switch_python")
    def test_not_yet_at_required_python(
        self,
        mock_switch_python,
        mock_state_input_proto_code_file_abs_path_eval_finalized,
        mock_state_proto_code_updated,
        mock_state_input_py_exec_var_loaded,
        mock_state_input_wizard_stage_arg_loaded,
        mock_state_args_parsed,
        mock_state_input_start_id_var_loaded,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_py_exec_updated_proto_code.name,
        )

        mock_state_args_parsed.return_value = argparse.Namespace(
            **{
                ParsedArg.name_reinstall.value: False,
            }
        )
        mock_state_input_start_id_var_loaded.return_value = "mock_start_id"
        mock_state_input_wizard_stage_arg_loaded.return_value = (
            WizardStage.wizard_started
        )

        mock_state_input_proto_code_file_abs_path_eval_finalized.return_value = (
            "path/to/whatever"
        )

        mock_state_proto_code_updated.return_value = True

        mock_state_input_py_exec_var_loaded.return_value = (
            PythonExecutable.py_exec_unknown
        )

        # when:

        self.env_ctx.state_graph.eval_state(
            EnvState.state_py_exec_updated_proto_code.name
        )

        # then:

        mock_switch_python.assert_called_once_with(
            curr_py_exec=PythonExecutable.py_exec_unknown,
            curr_python_path=get_path_to_curr_python(),
            next_py_exec=PythonExecutable.py_exec_updated_proto_code,
            next_python_path=get_path_to_curr_python(),
            start_id="mock_start_id",
            proto_code_abs_file_path=mock_state_input_proto_code_file_abs_path_eval_finalized.return_value,
            wizard_stage=WizardStage.wizard_started,
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_wizard_stage_arg_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_py_exec_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_updated.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_proto_code_file_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    @patch(f"{primer_kernel.__name__}.switch_python")
    def test_already_required_python(
        self,
        mock_switch_python,
        mock_state_input_proto_code_file_abs_path_eval_finalized,
        mock_state_proto_code_updated,
        mock_state_input_py_exec_var_loaded,
        mock_state_input_wizard_stage_arg_loaded,
        mock_state_args_parsed,
        mock_state_input_start_id_var_loaded,
    ):
        """
        UC_90_98_17_93.run_under_venv.md
        """

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_py_exec_updated_proto_code.name,
        )

        mock_state_args_parsed.return_value = argparse.Namespace(
            **{
                ParsedArg.name_reinstall.value: False,
            }
        )
        mock_state_input_start_id_var_loaded.return_value = "mock_start_id"
        mock_state_input_wizard_stage_arg_loaded.return_value = (
            WizardStage.wizard_started
        )

        mock_state_input_proto_code_file_abs_path_eval_finalized.return_value = (
            "path/to/whatever"
        )

        mock_state_proto_code_updated.return_value = True

        mock_state_input_py_exec_var_loaded.return_value = (
            PythonExecutable.py_exec_updated_proto_code
        )

        # when:

        self.env_ctx.state_graph.eval_state(
            EnvState.state_py_exec_updated_proto_code.name
        )

        # then:

        mock_switch_python.assert_not_called()
