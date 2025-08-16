from unittest.mock import patch

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_input_proto_conf_primer_file_abs_path_eval_finalized,
    Bootstrapper_state_input_py_exec_arg_loaded,
    Bootstrapper_state_input_wizard_stage_arg_loaded,
    Bootstrapper_state_proto_conf_file_data,
    ConfLeap,
    EnvContext,
    EnvState,
    PythonExecutable,
    StateNode,
    wizard_conf_leap,
    Wizard_state_proto_conf_file_data,
    WizardStage,
    write_json_file,
)


# noinspection PyPep8Naming
class ThisTestClass(BasePyfakefsTestClass):

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = EnvContext()

        # Replace the original bootstrapper with the wizard one:
        self.wizard_bootstrapper = Wizard_state_proto_conf_file_data(self.env_ctx)
        self.env_ctx.state_graph.register_node(
            self.wizard_bootstrapper,
            replace_existing=True,
        )

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_str(
            f"wizard_{EnvState.state_proto_conf_file_data.name}"
        )

    @patch(f"{primer_kernel.__name__}.{StateNode.__name__}")
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_wizard_stage_arg_loaded.__name__}._eval_state_once"
    )
    @patch(f"{primer_kernel.__name__}.{write_json_file.__name__}")
    @patch(f"{primer_kernel.__name__}.{wizard_conf_leap.__name__}")
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_proto_conf_primer_file_abs_path_eval_finalized.__name__}._eval_state_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_proto_conf_file_data.__name__}._eval_state_once"
    )
    def test_wizard_triggered(
        self,
        mock_state_proto_conf_file_data,
        mock_state_input_proto_conf_primer_file_abs_path_eval_finalized,
        mock_wizard_conf_leap,
        mock_write_json_file,
        mock_state_input_wizard_stage_arg_loaded,
        mock_state_node,
    ):
        # given:

        mock_state_input_wizard_stage_arg_loaded.return_value = (
            WizardStage.wizard_started
        )

        mock_file_path = "/mock/path/to/file"
        mock_state_input_proto_conf_primer_file_abs_path_eval_finalized.return_value = (
            mock_file_path
        )

        initial_data = {"test": "data"}
        mock_state_proto_conf_file_data.return_value = initial_data

        # when:

        state_value = self.env_ctx.state_graph.eval_state(
            EnvState.state_proto_conf_file_data.name
        )

        # then:

        mock_wizard_conf_leap.assert_called_once_with(
            self.wizard_bootstrapper,
            ConfLeap.leap_primer,
            mock_file_path,
            initial_data,
        )
        self.assertEqual(state_value, initial_data)
        mock_write_json_file.assert_called_once_with(
            mock_file_path,
            initial_data,
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_wizard_stage_arg_loaded.__name__}._eval_state_once"
    )
    @patch(f"{primer_kernel.__name__}.{wizard_conf_leap.__name__}")
    @patch(f"{primer_kernel.__name__}.{StateNode.__name__}")
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_proto_conf_primer_file_abs_path_eval_finalized.__name__}._eval_state_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_proto_conf_file_data.__name__}._eval_state_once"
    )
    def test_wizard_not_triggered(
        self,
        mock_state_proto_conf_file_data,
        mock_state_input_proto_conf_primer_file_abs_path_eval_finalized,
        mock_wizard_conf_leap,
        mock_state_input_wizard_stage_arg_loaded,
        mock_state_node,
    ):

        # given:

        mock_state_input_wizard_stage_arg_loaded.return_value = (
            WizardStage.wizard_finished
        )

        mock_file_path = "/mock/path/to/file"
        mock_state_input_proto_conf_primer_file_abs_path_eval_finalized.return_value = (
            mock_file_path
        )

        initial_data = {"test": "data"}
        mock_state_proto_conf_file_data.return_value = initial_data

        # when:

        state_value = self.env_ctx.state_graph.eval_state(
            EnvState.state_proto_conf_file_data.name
        )

        # then:

        mock_wizard_conf_leap.assert_not_called()
        self.assertEqual(state_value, initial_data)
