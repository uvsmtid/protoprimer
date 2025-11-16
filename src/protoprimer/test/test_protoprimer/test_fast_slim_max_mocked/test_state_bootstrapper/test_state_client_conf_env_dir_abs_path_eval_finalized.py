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
    Bootstrapper_state_client_conf_file_data,
    Bootstrapper_state_client_local_env_conf_dir_rel_path_eval_finalized,
    Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized,
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
            EnvState.state_client_conf_env_dir_abs_path_eval_finalized.name
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_local_env_conf_dir_rel_path_eval_finalized.__name__}.eval_own_state"
    )
    def test_success_when_conf_symlink_exists_and_target_dst_dir_unspecified(
        self,
        mock_state_client_local_env_conf_dir_rel_path_eval_finalized,
        mock_state_primer_ref_root_dir_abs_path_eval_finalized,
        mock_state_client_conf_file_data,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_client_conf_env_dir_abs_path_eval_finalized.name,
        )

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        primer_conf_data = {
            ConfField.field_primer_ref_root_dir_rel_path.value: ".",
            ConfField.field_primer_conf_client_file_rel_path.value: ConfConstPrimer.default_client_conf_file_rel_path,
        }
        write_json_file(
            os.path.join(
                mock_client_dir, ConfConstInput.default_file_basename_conf_primer
            ),
            primer_conf_data,
        )

        mock_state_primer_ref_root_dir_abs_path_eval_finalized.return_value = (
            mock_client_dir
        )
        mock_state_client_conf_file_data.return_value = {
            ConfField.field_client_link_name_dir_rel_path.value: ConfConstClient.default_dir_rel_path_leap_env_link_name
        }

        state_client_conf_env_dir_abs_path_eval_finalized = os.path.join(
            mock_client_dir,
            ConfConstClient.default_dir_rel_path_leap_env_link_name,
        )
        mock_target_dir = os.path.join(
            "target_dir",
        )
        self.fs.create_dir(mock_target_dir)
        self.fs.create_symlink(
            state_client_conf_env_dir_abs_path_eval_finalized,
            mock_target_dir,
        )
        client_script_basename = "client_script.py"
        test_args = [
            client_script_basename,
        ]

        mock_state_client_local_env_conf_dir_rel_path_eval_finalized.return_value = (
            mock_target_dir
        )

        # when:

        with patch.object(sys, "argv", test_args):
            self.env_ctx.state_graph.eval_state(
                EnvState.state_client_conf_env_dir_abs_path_eval_finalized.name
            )

        # then:

        # no exception happens

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_local_env_conf_dir_rel_path_eval_finalized.__name__}.eval_own_state"
    )
    def test_success_when_conf_symlink_exists_and_target_dst_dir_matches(
        self,
        mock_state_client_local_env_conf_dir_rel_path_eval_finalized,
        mock_state_primer_ref_root_dir_abs_path_eval_finalized,
        mock_state_client_conf_file_data,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_client_conf_env_dir_abs_path_eval_finalized.name,
        )

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        primer_conf_data = {
            ConfField.field_primer_ref_root_dir_rel_path.value: ".",
            ConfField.field_primer_conf_client_file_rel_path.value: ConfConstPrimer.default_client_conf_file_rel_path,
        }
        write_json_file(
            os.path.join(
                mock_client_dir, ConfConstInput.default_file_basename_conf_primer
            ),
            primer_conf_data,
        )
        mock_state_primer_ref_root_dir_abs_path_eval_finalized.return_value = (
            mock_client_dir
        )
        mock_state_client_conf_file_data.return_value = {
            ConfField.field_client_link_name_dir_rel_path.value: ConfConstClient.default_dir_rel_path_leap_env_link_name
        }

        state_client_conf_env_dir_abs_path_eval_finalized = os.path.join(
            mock_client_dir,
            ConfConstClient.default_dir_rel_path_leap_env_link_name,
        )
        target_dst_dir_path = os.path.join(
            "target_dir",
        )
        self.fs.create_dir(target_dst_dir_path)
        self.fs.create_symlink(
            state_client_conf_env_dir_abs_path_eval_finalized,
            target_dst_dir_path,
        )
        mock_state_client_local_env_conf_dir_rel_path_eval_finalized.return_value = (
            target_dst_dir_path
        )

        # when:

        self.env_ctx.state_graph.eval_state(
            EnvState.state_client_conf_env_dir_abs_path_eval_finalized.name
        )

        # then:

        # no exception happens

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_local_env_conf_dir_rel_path_eval_finalized.__name__}.eval_own_state"
    )
    def test_failure_when_conf_symlink_exists_but_target_dst_dir_mismatches(
        self,
        mock_state_client_local_env_conf_dir_rel_path_eval_finalized,
        mock_state_primer_ref_root_dir_abs_path_eval_finalized,
        mock_state_client_conf_file_data,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_client_conf_env_dir_abs_path_eval_finalized.name,
        )

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        primer_conf_data = {
            ConfField.field_primer_ref_root_dir_rel_path.value: ".",
            ConfField.field_primer_conf_client_file_rel_path.value: ConfConstPrimer.default_client_conf_file_rel_path,
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
        state_client_conf_env_dir_abs_path_eval_finalized = os.path.join(
            mock_client_dir, "lconf"
        )
        mock_state_primer_ref_root_dir_abs_path_eval_finalized.return_value = (
            mock_client_dir
        )
        mock_state_client_conf_file_data.return_value = {
            ConfField.field_client_link_name_dir_rel_path.value: os.path.basename(
                state_client_conf_env_dir_abs_path_eval_finalized
            )
        }
        self.fs.create_dir(actual_target_dir)
        self.fs.create_dir(expected_target_dir)
        self.fs.create_symlink(
            state_client_conf_env_dir_abs_path_eval_finalized,
            actual_target_dir,
        )

        mock_state_client_local_env_conf_dir_rel_path_eval_finalized.return_value = (
            expected_target_dir
        )

        # when:

        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.state_graph.eval_state(
                EnvState.state_client_conf_env_dir_abs_path_eval_finalized.name
            )

        # then:

        self.assertIn("not the same as the provided target", str(ctx.exception))

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_local_env_conf_dir_rel_path_eval_finalized.__name__}.eval_own_state"
    )
    def test_failure_when_conf_symlink_is_not_directory(
        self,
        mock_state_client_local_env_conf_dir_rel_path_eval_finalized,
        mock_state_primer_ref_root_dir_abs_path_eval_finalized,
        mock_state_client_conf_file_data,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_client_conf_env_dir_abs_path_eval_finalized.name,
        )

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        primer_conf_data = {
            ConfField.field_primer_ref_root_dir_rel_path.value: ".",
            ConfField.field_primer_conf_client_file_rel_path.value: ConfConstPrimer.default_client_conf_file_rel_path,
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
        mock_state_primer_ref_root_dir_abs_path_eval_finalized.return_value = (
            mock_client_dir
        )
        mock_state_client_conf_file_data.return_value = {
            ConfField.field_client_link_name_dir_rel_path.value: ConfConstClient.default_dir_rel_path_leap_env_link_name
        }

        state_client_conf_env_dir_abs_path_eval_finalized = os.path.join(
            mock_client_dir,
            ConfConstClient.default_dir_rel_path_leap_env_link_name,
        )
        self.fs.create_file(mock_not_a_dir)
        self.fs.create_symlink(
            state_client_conf_env_dir_abs_path_eval_finalized,
            mock_not_a_dir,
        )
        mock_state_client_local_env_conf_dir_rel_path_eval_finalized.return_value = (
            mock_not_a_dir
        )

        # when:

        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.state_graph.eval_state(
                EnvState.state_client_conf_env_dir_abs_path_eval_finalized.name
            )

        # then:

        self.assertIn("target is not a directory", str(ctx.exception))

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_local_env_conf_dir_rel_path_eval_finalized.__name__}.eval_own_state"
    )
    def test_failure_when_conf_is_not_symlink(
        self,
        mock_state_client_local_env_conf_dir_rel_path_eval_finalized,
        mock_state_primer_ref_root_dir_abs_path_eval_finalized,
        mock_state_client_conf_file_data,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_client_conf_env_dir_abs_path_eval_finalized.name,
        )

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        primer_conf_data = {
            ConfField.field_primer_ref_root_dir_rel_path.value: ".",
            ConfField.field_primer_conf_client_file_rel_path.value: ConfConstPrimer.default_client_conf_file_rel_path,
        }
        write_json_file(
            os.path.join(
                mock_client_dir, ConfConstInput.default_file_basename_conf_primer
            ),
            primer_conf_data,
        )

        mock_state_primer_ref_root_dir_abs_path_eval_finalized.return_value = (
            mock_client_dir
        )
        mock_state_client_conf_file_data.return_value = {
            ConfField.field_client_link_name_dir_rel_path.value: ConfConstClient.default_dir_rel_path_leap_env_link_name
        }

        state_client_conf_env_dir_abs_path_eval_finalized = os.path.join(
            mock_client_dir,
            ConfConstClient.default_dir_rel_path_leap_env_link_name,
        )
        self.fs.create_dir(state_client_conf_env_dir_abs_path_eval_finalized)
        client_script_basename = "client_script.py"
        test_args = [
            client_script_basename,
        ]

        mock_state_client_local_env_conf_dir_rel_path_eval_finalized.return_value = (
            "some_dir"
        )

        # when:

        with patch.object(sys, "argv", test_args):
            with self.assertRaises(AssertionError) as ctx:
                self.env_ctx.state_graph.eval_state(
                    EnvState.state_client_conf_env_dir_abs_path_eval_finalized.name
                )

        # then:

        self.assertIn("is not a symlink", str(ctx.exception))

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_local_env_conf_dir_rel_path_eval_finalized.__name__}.eval_own_state"
    )
    def test_success_when_conf_symlink_is_created_if_it_is_missing_and_target_dir_is_given(
        self,
        mock_state_client_local_env_conf_dir_rel_path_eval_finalized,
        mock_state_primer_ref_root_dir_abs_path_eval_finalized,
        mock_state_client_conf_file_data,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_client_conf_env_dir_abs_path_eval_finalized.name,
        )

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        primer_conf_data = {
            ConfField.field_primer_ref_root_dir_rel_path.value: ".",
            ConfField.field_primer_conf_client_file_rel_path.value: ConfConstPrimer.default_client_conf_file_rel_path,
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
        mock_state_primer_ref_root_dir_abs_path_eval_finalized.return_value = (
            mock_client_dir
        )
        mock_state_client_conf_file_data.return_value = {
            ConfField.field_client_link_name_dir_rel_path.value: ConfConstClient.default_dir_rel_path_leap_env_link_name
        }

        state_client_conf_env_dir_abs_path_eval_finalized = os.path.join(
            mock_client_dir,
            ConfConstClient.default_dir_rel_path_leap_env_link_name,
        )
        self.fs.create_dir(target_dst_dir_path)

        mock_state_client_local_env_conf_dir_rel_path_eval_finalized.return_value = (
            target_dst_dir_path
        )

        # when:

        self.env_ctx.state_graph.eval_state(
            EnvState.state_client_conf_env_dir_abs_path_eval_finalized.name
        )

        # then:

        self.assertTrue(
            os.path.islink(state_client_conf_env_dir_abs_path_eval_finalized)
        )
        self.assertEqual(
            os.readlink(state_client_conf_env_dir_abs_path_eval_finalized),
            target_dst_dir_path,
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_local_env_conf_dir_rel_path_eval_finalized.__name__}.eval_own_state"
    )
    def test_success_when_conf_symlink_is_created_with_normalized_target(
        self,
        mock_state_client_local_env_conf_dir_rel_path_eval_finalized,
        mock_state_primer_ref_root_dir_abs_path_eval_finalized,
        mock_state_client_conf_file_data,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_client_conf_env_dir_abs_path_eval_finalized.name,
        )

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        primer_conf_data = {
            ConfField.field_primer_ref_root_dir_rel_path.value: ".",
            ConfField.field_primer_conf_client_file_rel_path.value: ConfConstPrimer.default_client_conf_file_rel_path,
        }
        write_json_file(
            os.path.join(
                mock_client_dir, ConfConstInput.default_file_basename_conf_primer
            ),
            primer_conf_data,
        )

        target_dst_dir_path_non_normalized = "target_dir/"
        target_dst_dir_path_normalized = "target_dir"
        mock_state_primer_ref_root_dir_abs_path_eval_finalized.return_value = (
            mock_client_dir
        )
        mock_state_client_conf_file_data.return_value = {
            ConfField.field_client_link_name_dir_rel_path.value: ConfConstClient.default_dir_rel_path_leap_env_link_name
        }

        state_client_conf_env_dir_abs_path_eval_finalized = os.path.join(
            mock_client_dir,
            ConfConstClient.default_dir_rel_path_leap_env_link_name,
        )
        self.fs.create_dir(target_dst_dir_path_normalized)

        mock_state_client_local_env_conf_dir_rel_path_eval_finalized.return_value = (
            target_dst_dir_path_non_normalized
        )

        # when:

        self.env_ctx.state_graph.eval_state(
            EnvState.state_client_conf_env_dir_abs_path_eval_finalized.name
        )

        # then:

        self.assertTrue(
            os.path.islink(state_client_conf_env_dir_abs_path_eval_finalized)
        )
        self.assertEqual(
            os.readlink(state_client_conf_env_dir_abs_path_eval_finalized),
            target_dst_dir_path_normalized,
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_local_env_conf_dir_rel_path_eval_finalized.__name__}.eval_own_state"
    )
    def test_success_when_local_env_conf_dir_is_none(
        self,
        mock_state_client_local_env_conf_dir_rel_path_eval_finalized,
        mock_state_primer_ref_root_dir_abs_path_eval_finalized,
        mock_state_client_conf_file_data,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_client_conf_env_dir_abs_path_eval_finalized.name,
        )

        mock_ref_root = "/mock_ref_root"
        mock_state_primer_ref_root_dir_abs_path_eval_finalized.return_value = (
            mock_ref_root
        )
        mock_state_client_local_env_conf_dir_rel_path_eval_finalized.return_value = None
        mock_state_client_conf_file_data.return_value = {}  # Not used in this branch

        # when:
        result = self.env_ctx.state_graph.eval_state(
            EnvState.state_client_conf_env_dir_abs_path_eval_finalized.name
        )

        # then:
        self.assertEqual(result, mock_ref_root)
