import os
from unittest.mock import patch

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_client_conf_env_dir_abs_path_eval_finalized,
    Bootstrapper_state_client_conf_env_dir_abs_path_eval_verified,
    Bootstrapper_state_client_conf_env_file_abs_path_eval_finalized,
    Bootstrapper_state_client_link_name_dir_rel_path_eval_finalized,
    Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized,
    ConfConstClient,
    EnvContext,
    EnvState,
)
from test_protoprimer.misc_tools.mock_verifier import assert_parent_states_mocked


# noinspection PyPep8Naming
class ThisTestClass(BasePyfakefsTestClass):

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = EnvContext()

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_str(
            EnvState.state_client_conf_env_file_abs_path_eval_finalized.name
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_link_name_dir_rel_path_eval_finalized.__name__}._eval_state_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_env_dir_abs_path_eval_verified.__name__}._eval_state_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized.__name__}._eval_state_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_env_dir_abs_path_eval_finalized.__name__}._eval_state_once"
    )
    def test_success_when_all_parent_states_are_set(
        self,
        mock_state_client_conf_env_dir_abs_path_eval_finalized,
        mock_state_primer_ref_root_dir_abs_path_eval_finalized,
        mock_state_client_conf_env_dir_abs_path_eval_verified,
        mock_state_client_link_name_dir_rel_path_eval_finalized,
    ):
        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_client_conf_env_file_abs_path_eval_finalized,
        )

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        mock_state_client_conf_env_dir_abs_path_eval_verified.return_value = True
        mock_state_primer_ref_root_dir_abs_path_eval_finalized.return_value = (
            mock_client_dir
        )
        mock_state_client_conf_env_dir_abs_path_eval_finalized.return_value = (
            os.path.join(
                mock_client_dir,
                ConfConstClient.default_dir_rel_path_leap_env_link_name,
            )
        )
        mock_state_client_link_name_dir_rel_path_eval_finalized.return_value = (
            ConfConstClient.default_dir_rel_path_leap_env_link_name
        )

        # when:

        state_client_conf_env_file_abs_path_eval_finalized = (
            self.env_ctx.state_graph.eval_state(
                EnvState.state_client_conf_env_file_abs_path_eval_finalized.name
            )
        )

        # then:

        expected_path = os.path.join(
            mock_client_dir,
            ConfConstClient.default_dir_rel_path_leap_env_link_name,
            ConfConstClient.default_file_basename_leap_env,
        )
        self.assertEqual(
            state_client_conf_env_file_abs_path_eval_finalized, expected_path
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_link_name_dir_rel_path_eval_finalized.__name__}._eval_state_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_env_dir_abs_path_eval_verified.__name__}._eval_state_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized.__name__}._eval_state_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_env_dir_abs_path_eval_finalized.__name__}._eval_state_once"
    )
    def test_failure_when_path_is_not_sub_path(
        self,
        mock_state_client_conf_env_dir_abs_path_eval_finalized,
        mock_state_primer_ref_root_dir_abs_path_eval_finalized,
        mock_state_client_conf_env_dir_abs_path_eval_verified,
        mock_state_client_link_name_dir_rel_path_eval_finalized,
    ):
        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_client_conf_env_file_abs_path_eval_finalized,
        )

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        mock_state_client_conf_env_dir_abs_path_eval_verified.return_value = True

        # This will cause the path to be outside:
        mock_state_primer_ref_root_dir_abs_path_eval_finalized.return_value = (
            "/another_dir"
        )
        mock_state_client_conf_env_dir_abs_path_eval_finalized.return_value = (
            os.path.join(
                mock_client_dir,
                ConfConstClient.default_dir_rel_path_leap_env_link_name,
            )
        )
        mock_state_client_link_name_dir_rel_path_eval_finalized.return_value = (
            ConfConstClient.default_dir_rel_path_leap_env_link_name
        )

        # when:

        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.state_graph.eval_state(
                EnvState.state_client_conf_env_file_abs_path_eval_finalized.name
            )

        # then:

        self.assertIn("path is not under", str(ctx.exception))
