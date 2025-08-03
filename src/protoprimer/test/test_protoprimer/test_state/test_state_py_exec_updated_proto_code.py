from unittest.mock import patch

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_input_proto_code_file_abs_path_eval_finalized,
    Bootstrapper_state_input_py_exec_arg_loaded,
    Bootstrapper_state_proto_code_updated,
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
        assert_test_module_name_embeds_str(
            EnvState.state_py_exec_updated_proto_code.name
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_py_exec_arg_loaded.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_updated.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_proto_code_file_abs_path_eval_finalized.__name__}._bootstrap_once"
    )
    @patch(f"{primer_kernel.__name__}.switch_python")
    def test_not_yet_at_required_python(
        self,
        mock_switch_python,
        mock_state_input_proto_code_file_abs_path_eval_finalized,
        mock_state_proto_code_updated,
        mock_state_input_py_exec_arg_loaded,
    ):

        # given:

        mock_state_input_proto_code_file_abs_path_eval_finalized.return_value = (
            "path/to/whatever"
        )

        mock_state_proto_code_updated.return_value = True

        mock_state_input_py_exec_arg_loaded.return_value = (
            PythonExecutable.py_exec_unknown
        )

        # when:

        self.env_ctx.bootstrap_state(EnvState.state_py_exec_updated_proto_code.name)

        # then:

        mock_switch_python.assert_called_once_with(
            curr_py_exec=PythonExecutable.py_exec_unknown,
            curr_python_path=get_path_to_curr_python(),
            next_py_exec=PythonExecutable.py_exec_updated_proto_code,
            next_python_path=get_path_to_curr_python(),
            proto_code_abs_file_path=mock_state_input_proto_code_file_abs_path_eval_finalized.return_value,
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_py_exec_arg_loaded.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_updated.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_proto_code_file_abs_path_eval_finalized.__name__}._bootstrap_once"
    )
    @patch(f"{primer_kernel.__name__}.switch_python")
    def test_already_required_python(
        self,
        mock_switch_python,
        mock_state_input_proto_code_file_abs_path_eval_finalized,
        mock_state_proto_code_updated,
        mock_state_input_py_exec_arg_loaded,
    ):
        """
        UC_90_98_17_93.run_under_venv.md
        """

        # given:

        mock_state_input_proto_code_file_abs_path_eval_finalized.return_value = (
            "path/to/whatever"
        )

        mock_state_proto_code_updated.return_value = True

        mock_state_input_py_exec_arg_loaded.return_value = (
            PythonExecutable.py_exec_updated_proto_code
        )

        # when:

        self.env_ctx.bootstrap_state(EnvState.state_py_exec_updated_proto_code.name)

        # then:

        mock_switch_python.assert_not_called()
