import os
import sys
from unittest.mock import patch

from local_repo.cmd_bootstrap_env import customize_env_context
from local_test.base_test_class import BasePyfakefsTestClass
from local_test.mock_verifier import (
    assert_parent_states_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_client_conf_file_data_loaded,
    Bootstrapper_state_selected_env_dir_rel_path_inited,
    Bootstrapper_state_ref_root_dir_abs_path_inited,
    ConfConstClient,
    ConfConstInput,
    ConfConstPrimer,
    ConfField,
    EnvState,
    write_json_file,
)


# noinspection PyPep8Naming
class ThisTestClass(BasePyfakefsTestClass):

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = customize_env_context()

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_str(
            EnvState.state_local_conf_symlink_abs_path_inited.name
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_ref_root_dir_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_selected_env_dir_rel_path_inited.__name__}.eval_own_state"
    )
    def test_success_when_conf_symlink_exists_and_target_dst_dir_unspecified(
        self,
        mock_state_selected_env_dir_rel_path_inited,
        mock_state_ref_root_dir_abs_path_inited,
        mock_state_client_conf_file_data_loaded,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_local_conf_symlink_abs_path_inited.name,
        )

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        primer_conf_data = {
            ConfField.field_ref_root_dir_rel_path.value: ".",
            ConfField.field_global_conf_dir_rel_path.value: ConfConstPrimer.default_client_conf_dir_rel_path,
        }
        write_json_file(
            os.path.join(
                mock_client_dir, ConfConstInput.default_file_basename_conf_primer
            ),
            primer_conf_data,
        )

        mock_state_ref_root_dir_abs_path_inited.return_value = mock_client_dir
        mock_state_client_conf_file_data_loaded.return_value = {
            ConfField.field_local_conf_symlink_rel_path.value: ConfConstClient.default_dir_rel_path_leap_env_link_name
        }

        state_local_conf_symlink_abs_path_inited = os.path.join(
            mock_client_dir,
            ConfConstClient.default_dir_rel_path_leap_env_link_name,
        )
        mock_target_dir = os.path.join(
            "target_dir",
        )
        self.fs.create_dir(mock_target_dir)
        self.fs.create_symlink(
            state_local_conf_symlink_abs_path_inited,
            mock_target_dir,
        )
        client_script_basename = "client_script.py"
        test_args = [
            client_script_basename,
        ]

        mock_state_selected_env_dir_rel_path_inited.return_value = mock_target_dir

        # when:

        with patch.object(sys, "argv", test_args):
            self.env_ctx.state_graph.eval_state(
                EnvState.state_local_conf_symlink_abs_path_inited.name
            )

        # then:

        # no exception happens

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_ref_root_dir_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_selected_env_dir_rel_path_inited.__name__}.eval_own_state"
    )
    def test_success_when_conf_symlink_exists_and_target_dst_dir_matches(
        self,
        mock_state_selected_env_dir_rel_path_inited,
        mock_state_ref_root_dir_abs_path_inited,
        mock_state_client_conf_file_data_loaded,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_local_conf_symlink_abs_path_inited.name,
        )

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        primer_conf_data = {
            ConfField.field_ref_root_dir_rel_path.value: ".",
            ConfField.field_global_conf_dir_rel_path.value: ConfConstPrimer.default_client_conf_dir_rel_path,
        }
        write_json_file(
            os.path.join(
                mock_client_dir, ConfConstInput.default_file_basename_conf_primer
            ),
            primer_conf_data,
        )
        mock_state_ref_root_dir_abs_path_inited.return_value = mock_client_dir
        mock_state_client_conf_file_data_loaded.return_value = {
            ConfField.field_local_conf_symlink_rel_path.value: ConfConstClient.default_dir_rel_path_leap_env_link_name
        }

        state_local_conf_symlink_abs_path_inited = os.path.join(
            mock_client_dir,
            ConfConstClient.default_dir_rel_path_leap_env_link_name,
        )
        target_dst_dir_path = os.path.join(
            "target_dir",
        )
        self.fs.create_dir(target_dst_dir_path)
        self.fs.create_symlink(
            state_local_conf_symlink_abs_path_inited,
            target_dst_dir_path,
        )
        mock_state_selected_env_dir_rel_path_inited.return_value = target_dst_dir_path

        # when:

        self.env_ctx.state_graph.eval_state(
            EnvState.state_local_conf_symlink_abs_path_inited.name
        )

        # then:

        # no exception happens

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_ref_root_dir_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_selected_env_dir_rel_path_inited.__name__}.eval_own_state"
    )
    def test_failure_when_conf_symlink_exists_but_target_dst_dir_mismatches(
        self,
        mock_state_selected_env_dir_rel_path_inited,
        mock_state_ref_root_dir_abs_path_inited,
        mock_state_client_conf_file_data_loaded,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_local_conf_symlink_abs_path_inited.name,
        )

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        primer_conf_data = {
            ConfField.field_ref_root_dir_rel_path.value: ".",
            ConfField.field_global_conf_dir_rel_path.value: ConfConstPrimer.default_client_conf_dir_rel_path,
        }
        write_json_file(
            os.path.join(
                mock_client_dir, ConfConstInput.default_file_basename_conf_primer
            ),
            primer_conf_data,
        )
        actual_target_dir = os.path.join(
            "actual_target_dir",
        )
        expected_target_dir = os.path.join(
            "expected_target_dir",
        )
        state_local_conf_symlink_abs_path_inited = os.path.join(
            mock_client_dir, "lconf"
        )
        mock_state_ref_root_dir_abs_path_inited.return_value = mock_client_dir
        mock_state_client_conf_file_data_loaded.return_value = {
            ConfField.field_local_conf_symlink_rel_path.value: os.path.basename(
                state_local_conf_symlink_abs_path_inited
            )
        }
        self.fs.create_dir(actual_target_dir)
        self.fs.create_dir(expected_target_dir)
        self.fs.create_symlink(
            state_local_conf_symlink_abs_path_inited,
            actual_target_dir,
        )

        mock_state_selected_env_dir_rel_path_inited.return_value = expected_target_dir

        # when:

        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.state_graph.eval_state(
                EnvState.state_local_conf_symlink_abs_path_inited.name
            )

        # then:

        self.assertIn("not the same as the provided target", str(ctx.exception))

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_ref_root_dir_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_selected_env_dir_rel_path_inited.__name__}.eval_own_state"
    )
    def test_failure_when_conf_symlink_is_not_directory(
        self,
        mock_state_selected_env_dir_rel_path_inited,
        mock_state_ref_root_dir_abs_path_inited,
        mock_state_client_conf_file_data_loaded,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_local_conf_symlink_abs_path_inited.name,
        )

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        primer_conf_data = {
            ConfField.field_ref_root_dir_rel_path.value: ".",
            ConfField.field_global_conf_dir_rel_path.value: ConfConstPrimer.default_client_conf_dir_rel_path,
        }
        write_json_file(
            os.path.join(
                mock_client_dir, ConfConstInput.default_file_basename_conf_primer
            ),
            primer_conf_data,
        )
        mock_not_a_dir = os.path.join(
            "file",
        )
        mock_state_ref_root_dir_abs_path_inited.return_value = mock_client_dir
        mock_state_client_conf_file_data_loaded.return_value = {
            ConfField.field_local_conf_symlink_rel_path.value: ConfConstClient.default_dir_rel_path_leap_env_link_name
        }

        state_local_conf_symlink_abs_path_inited = os.path.join(
            mock_client_dir,
            ConfConstClient.default_dir_rel_path_leap_env_link_name,
        )
        self.fs.create_file(mock_not_a_dir)
        self.fs.create_symlink(
            state_local_conf_symlink_abs_path_inited,
            mock_not_a_dir,
        )
        mock_state_selected_env_dir_rel_path_inited.return_value = mock_not_a_dir

        # when:

        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.state_graph.eval_state(
                EnvState.state_local_conf_symlink_abs_path_inited.name
            )

        # then:

        self.assertIn("is not a directory", str(ctx.exception))

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_ref_root_dir_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_selected_env_dir_rel_path_inited.__name__}.eval_own_state"
    )
    def test_failure_when_conf_is_not_symlink(
        self,
        mock_state_selected_env_dir_rel_path_inited,
        mock_state_ref_root_dir_abs_path_inited,
        mock_state_client_conf_file_data_loaded,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_local_conf_symlink_abs_path_inited.name,
        )

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        primer_conf_data = {
            ConfField.field_ref_root_dir_rel_path.value: ".",
            ConfField.field_global_conf_dir_rel_path.value: ConfConstPrimer.default_client_conf_dir_rel_path,
        }
        write_json_file(
            os.path.join(
                mock_client_dir, ConfConstInput.default_file_basename_conf_primer
            ),
            primer_conf_data,
        )

        mock_state_ref_root_dir_abs_path_inited.return_value = mock_client_dir
        mock_state_client_conf_file_data_loaded.return_value = {
            ConfField.field_local_conf_symlink_rel_path.value: ConfConstClient.default_dir_rel_path_leap_env_link_name
        }

        state_local_conf_symlink_abs_path_inited = os.path.join(
            mock_client_dir,
            ConfConstClient.default_dir_rel_path_leap_env_link_name,
        )
        self.fs.create_dir(state_local_conf_symlink_abs_path_inited)
        client_script_basename = "client_script.py"
        test_args = [
            client_script_basename,
        ]

        mock_state_selected_env_dir_rel_path_inited.return_value = "some_dir"

        # when:

        with patch.object(sys, "argv", test_args):
            with self.assertRaises(AssertionError) as ctx:
                self.env_ctx.state_graph.eval_state(
                    EnvState.state_local_conf_symlink_abs_path_inited.name
                )

        # then:

        self.assertIn("is not a symlink", str(ctx.exception))

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_ref_root_dir_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_selected_env_dir_rel_path_inited.__name__}.eval_own_state"
    )
    def test_success_when_conf_symlink_is_created_if_it_is_missing_and_target_dir_is_given(
        self,
        mock_state_selected_env_dir_rel_path_inited,
        mock_state_ref_root_dir_abs_path_inited,
        mock_state_client_conf_file_data_loaded,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_local_conf_symlink_abs_path_inited.name,
        )

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        primer_conf_data = {
            ConfField.field_ref_root_dir_rel_path.value: ".",
            ConfField.field_global_conf_dir_rel_path.value: ConfConstPrimer.default_client_conf_dir_rel_path,
        }
        write_json_file(
            os.path.join(
                mock_client_dir, ConfConstInput.default_file_basename_conf_primer
            ),
            primer_conf_data,
        )
        target_dst_dir_path = os.path.join(
            "target_dir",
        )
        mock_state_ref_root_dir_abs_path_inited.return_value = mock_client_dir
        mock_state_client_conf_file_data_loaded.return_value = {
            ConfField.field_local_conf_symlink_rel_path.value: ConfConstClient.default_dir_rel_path_leap_env_link_name
        }

        state_local_conf_symlink_abs_path_inited = os.path.join(
            mock_client_dir,
            ConfConstClient.default_dir_rel_path_leap_env_link_name,
        )
        self.fs.create_dir(target_dst_dir_path)

        mock_state_selected_env_dir_rel_path_inited.return_value = target_dst_dir_path

        # when:

        self.env_ctx.state_graph.eval_state(
            EnvState.state_local_conf_symlink_abs_path_inited.name
        )

        # then:

        self.assertTrue(os.path.islink(state_local_conf_symlink_abs_path_inited))
        self.assertEqual(
            os.readlink(state_local_conf_symlink_abs_path_inited),
            target_dst_dir_path,
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_ref_root_dir_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_selected_env_dir_rel_path_inited.__name__}.eval_own_state"
    )
    def test_success_when_conf_symlink_is_created_with_normalized_target(
        self,
        mock_state_selected_env_dir_rel_path_inited,
        mock_state_ref_root_dir_abs_path_inited,
        mock_state_client_conf_file_data_loaded,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_local_conf_symlink_abs_path_inited.name,
        )

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        primer_conf_data = {
            ConfField.field_ref_root_dir_rel_path.value: ".",
            ConfField.field_global_conf_dir_rel_path.value: ConfConstPrimer.default_client_conf_dir_rel_path,
        }
        write_json_file(
            os.path.join(
                mock_client_dir, ConfConstInput.default_file_basename_conf_primer
            ),
            primer_conf_data,
        )

        target_dst_dir_path_non_normalized = "target_dir/"
        target_dst_dir_path_normalized = "target_dir"
        mock_state_ref_root_dir_abs_path_inited.return_value = mock_client_dir
        mock_state_client_conf_file_data_loaded.return_value = {
            ConfField.field_local_conf_symlink_rel_path.value: ConfConstClient.default_dir_rel_path_leap_env_link_name
        }

        state_local_conf_symlink_abs_path_inited = os.path.join(
            mock_client_dir,
            ConfConstClient.default_dir_rel_path_leap_env_link_name,
        )
        self.fs.create_dir(target_dst_dir_path_normalized)

        mock_state_selected_env_dir_rel_path_inited.return_value = (
            target_dst_dir_path_non_normalized
        )

        # when:

        self.env_ctx.state_graph.eval_state(
            EnvState.state_local_conf_symlink_abs_path_inited.name
        )

        # then:

        self.assertTrue(os.path.islink(state_local_conf_symlink_abs_path_inited))
        self.assertEqual(
            os.readlink(state_local_conf_symlink_abs_path_inited),
            target_dst_dir_path_normalized,
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_ref_root_dir_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_selected_env_dir_rel_path_inited.__name__}.eval_own_state"
    )
    def test_success_when_local_env_conf_dir_is_none(
        self,
        mock_state_selected_env_dir_rel_path_inited,
        mock_state_ref_root_dir_abs_path_inited,
        mock_state_client_conf_file_data_loaded,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_local_conf_symlink_abs_path_inited.name,
        )

        mock_ref_root = "/mock_ref_root"
        mock_state_ref_root_dir_abs_path_inited.return_value = mock_ref_root
        mock_state_selected_env_dir_rel_path_inited.return_value = None
        mock_state_client_conf_file_data_loaded.return_value = (
            {}
        )  # Not used in this branch

        # when:
        result = self.env_ctx.state_graph.eval_state(
            EnvState.state_local_conf_symlink_abs_path_inited.name
        )

        # then:
        self.assertEqual(result, mock_ref_root)
