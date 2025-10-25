import os
import subprocess
from unittest.mock import (
    patch,
)

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.mock_verifier import (
    assert_parent_states_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_client_conf_env_dir_abs_path_eval_finalized,
    Bootstrapper_state_protoprimer_package_installed,
    ConfConstEnv,
    EnvContext,
    EnvState,
)


# noinspection PyPep8Naming
class ThisTestClass(BasePyfakefsTestClass):

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = EnvContext()

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_str(
            EnvState.state_version_constraints_generated.name
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_protoprimer_package_installed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_env_dir_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    @patch(f"{primer_kernel.__name__}.get_path_to_curr_python")
    @patch(f"{subprocess.__name__}.check_call")
    def test_constraints_generated(
        self,
        mock_check_call,
        mock_get_path_to_curr_python,
        mock_state_client_conf_env_dir_abs_path_eval_finalized,
        mock_state_protoprimer_package_installed,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_version_constraints_generated.name,
        )
        self.fs.reset()
        self.env_ctx = EnvContext()
        mock_check_call.reset_mock()
        mock_state_protoprimer_package_installed.return_value = True
        mock_client_conf_env_dir = "/mock_client_conf_env_dir"
        self.fs.create_dir(mock_client_conf_env_dir)
        mock_state_client_conf_env_dir_abs_path_eval_finalized.return_value = (
            mock_client_conf_env_dir
        )
        mock_python_path = "/mock/python"
        mock_get_path_to_curr_python.return_value = mock_python_path
        # when:
        self.env_ctx.state_graph.eval_state(
            EnvState.state_version_constraints_generated.name
        )
        # then:
        constraints_txt_path = os.path.join(
            mock_client_conf_env_dir,
            ConfConstEnv.constraints_txt_basename,
        )
        self.assertTrue(os.path.exists(constraints_txt_path))
        mock_check_call.assert_called_once()
        args, kwargs = mock_check_call.call_args
        self.assertEqual(
            args[0],
            [
                mock_python_path,
                "-m",
                "pip",
                "freeze",
                "--exclude-editable",
            ],
        )
        self.assertIn("stdout", kwargs)

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_protoprimer_package_installed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_env_dir_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    @patch(f"{primer_kernel.__name__}.get_path_to_curr_python")
    @patch(f"{subprocess.__name__}.check_call")
    def test_generation_skipped(
        self,
        mock_check_call,
        mock_get_path_to_curr_python,
        mock_state_client_conf_env_dir_abs_path_eval_finalized,
        mock_state_protoprimer_package_installed,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_version_constraints_generated.name,
        )
        self.fs.reset()
        self.env_ctx = EnvContext()
        mock_check_call.reset_mock()
        mock_state_protoprimer_package_installed.return_value = False
        mock_client_conf_env_dir = "/mock_client_conf_env_dir"
        self.fs.create_dir(mock_client_conf_env_dir)
        mock_state_client_conf_env_dir_abs_path_eval_finalized.return_value = (
            mock_client_conf_env_dir
        )
        mock_python_path = "/mock/python"
        mock_get_path_to_curr_python.return_value = mock_python_path
        # when:
        self.env_ctx.state_graph.eval_state(
            EnvState.state_version_constraints_generated.name
        )
        # then:
        constraints_txt_path = os.path.join(
            mock_client_conf_env_dir,
            ConfConstEnv.constraints_txt_basename,
        )
        self.assertFalse(os.path.exists(constraints_txt_path))
        mock_check_call.assert_not_called()
