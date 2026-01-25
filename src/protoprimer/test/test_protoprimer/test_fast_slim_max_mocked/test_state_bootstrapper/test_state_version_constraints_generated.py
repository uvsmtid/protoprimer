import os
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
    Bootstrapper_state_local_conf_symlink_abs_path_inited,
    Bootstrapper_state_package_driver_prepared,
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
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_symlink_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_run_mode_arg_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_package_driver_prepared.__name__}.eval_own_state"
    )
    def test_constraints_generated(
        self,
        mock_state_package_driver_prepared,
        mock_state_input_run_mode_arg_loaded,
        mock_state_local_conf_symlink_abs_path_inited,
        mock_state_protoprimer_package_installed,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_version_constraints_generated.name,
        )
        self.fs.reset()
        self.env_ctx = EnvContext()
        mock_state_protoprimer_package_installed.return_value = True
        mock_client_conf_env_dir = "/mock_client_conf_env_dir"
        self.fs.create_dir(mock_client_conf_env_dir)
        mock_state_local_conf_symlink_abs_path_inited.return_value = (
            mock_client_conf_env_dir
        )

        def pin_versions_impl(
            required_python_file_abs_path,
            constraints_file_abs_path,
        ):
            self.fs.create_file(constraints_file_abs_path)

        mock_state_package_driver_prepared.return_value.pin_versions.side_effect = (
            pin_versions_impl
        )
        mock_state_input_run_mode_arg_loaded.return_value = "prime"

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
        mock_state_package_driver_prepared.return_value.pin_versions.assert_called_once()

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_protoprimer_package_installed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_symlink_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_run_mode_arg_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_package_driver_prepared.__name__}.eval_own_state"
    )
    def test_generation_skipped(
        self,
        mock_state_package_driver_prepared,
        mock_state_input_run_mode_arg_loaded,
        mock_state_local_conf_symlink_abs_path_inited,
        mock_state_protoprimer_package_installed,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_version_constraints_generated.name,
        )
        self.fs.reset()
        self.env_ctx = EnvContext()
        mock_state_protoprimer_package_installed.return_value = False
        mock_client_conf_env_dir = "/mock_client_conf_env_dir"
        self.fs.create_dir(mock_client_conf_env_dir)
        mock_state_local_conf_symlink_abs_path_inited.return_value = (
            mock_client_conf_env_dir
        )
        mock_state_input_run_mode_arg_loaded.return_value = "prime"
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
        mock_state_package_driver_prepared.return_value.pin_versions.assert_not_called()
