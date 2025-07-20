from unittest.mock import patch

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_proto_kernel_code_file_abs_path_finalized,
    Bootstrapper_state_proto_kernel_updated,
    Bootstrapper_state_py_exec_arg,
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
            EnvState.state_py_exec_updated_proto_kernel_code.name
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_arg.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_proto_kernel_updated.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_proto_kernel_code_file_abs_path_finalized.__name__}._bootstrap_once"
    )
    @patch(f"{primer_kernel.__name__}.switch_python")
    def test_not_yet_at_required_python(
        self,
        mock_switch_python,
        mock_state_proto_kernel_code_file_abs_path_finalized,
        mock_state_proto_kernel_updated,
        mock_state_py_exec_arg,
    ):

        # given:

        mock_state_proto_kernel_code_file_abs_path_finalized.return_value = (
            "path/to/whatever"
        )

        mock_state_proto_kernel_updated.return_value = True

        mock_state_py_exec_arg.return_value = PythonExecutable.py_exec_unknown

        # when:

        self.env_ctx.bootstrap_state(
            EnvState.state_py_exec_updated_proto_kernel_code.name
        )

        # then:

        mock_switch_python.assert_called_once_with(
            curr_py_exec=PythonExecutable.py_exec_unknown,
            curr_python_path=get_path_to_curr_python(),
            next_py_exec=PythonExecutable.py_exec_updated_proto_kernel_code,
            next_python_path=get_path_to_curr_python(),
            proto_kernel_abs_file_path=mock_state_proto_kernel_code_file_abs_path_finalized.return_value,
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_arg.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_proto_kernel_updated.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_proto_kernel_code_file_abs_path_finalized.__name__}._bootstrap_once"
    )
    @patch(f"{primer_kernel.__name__}.switch_python")
    def test_already_required_python(
        self,
        mock_switch_python,
        mock_state_proto_kernel_code_file_abs_path_finalized,
        mock_state_proto_kernel_updated,
        mock_state_py_exec_arg,
    ):
        """
        UC_90_98_17_93.run_under_venv.md
        """

        # given:

        mock_state_proto_kernel_code_file_abs_path_finalized.return_value = (
            "path/to/whatever"
        )

        mock_state_proto_kernel_updated.return_value = True

        mock_state_py_exec_arg.return_value = (
            PythonExecutable.py_exec_updated_proto_kernel_code
        )

        # when:

        self.env_ctx.bootstrap_state(
            EnvState.state_py_exec_updated_proto_kernel_code.name
        )

        # then:

        mock_switch_python.assert_not_called()
