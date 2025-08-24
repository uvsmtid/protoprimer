import os
import sys
from unittest.mock import patch

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_client_conf_env_dir_abs_path_eval_finalized,
    Bootstrapper_state_client_local_env_dir_rel_path_eval_finalized,
    Bootstrapper_state_client_local_env_dir_rel_path_eval_verified,
    Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized,
    ConfConstClient,
    ConfConstInput,
    ConfConstPrimer,
    ConfField,
    EnvContext,
    EnvState,
    write_json_file,
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
            EnvState.state_client_conf_env_dir_abs_path_eval_verified.name
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_local_env_dir_rel_path_eval_verified.__name__}._eval_state_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_local_env_dir_rel_path_eval_finalized.__name__}._eval_state_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_env_dir_abs_path_eval_finalized.__name__}._eval_state_once"
    )
    def test_success_when_conf_symlink_exists_and_target_dst_dir_unspecified(
        self,
        mock_state_client_conf_env_dir_abs_path_eval_finalized,
        mock_state_client_local_env_dir_rel_path_eval_finalized,
        mock_state_client_local_env_dir_rel_path_eval_verified,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_client_conf_env_dir_abs_path_eval_verified,
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

        state_client_conf_env_dir_abs_path_eval_finalized = os.path.join(
            mock_client_dir,
            ConfConstClient.default_dir_rel_path_leap_env_link_name,
        )
        mock_state_client_conf_env_dir_abs_path_eval_finalized.return_value = (
            state_client_conf_env_dir_abs_path_eval_finalized
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

        mock_state_client_local_env_dir_rel_path_eval_finalized.return_value = (
            mock_target_dir
        )
        mock_state_client_local_env_dir_rel_path_eval_verified.return_value = True

        # when:

        with patch.object(sys, "argv", test_args):
            self.env_ctx.state_graph.eval_state(
                EnvState.state_client_conf_env_dir_abs_path_eval_verified.name
            )

        # then:

        # no exception happens

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_local_env_dir_rel_path_eval_verified.__name__}._eval_state_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_local_env_dir_rel_path_eval_finalized.__name__}._eval_state_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_env_dir_abs_path_eval_finalized.__name__}._eval_state_once"
    )
    def test_success_when_conf_symlink_exists_and_target_dst_dir_matches(
        self,
        mock_state_client_conf_env_dir_abs_path_eval_finalized,
        mock_state_client_local_env_dir_rel_path_eval_finalized,
        mock_state_client_local_env_dir_rel_path_eval_verified,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_client_conf_env_dir_abs_path_eval_verified,
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
        state_client_conf_env_dir_abs_path_eval_finalized = os.path.join(
            mock_client_dir,
            ConfConstClient.default_dir_rel_path_leap_env_link_name,
        )
        mock_state_client_conf_env_dir_abs_path_eval_finalized.return_value = (
            state_client_conf_env_dir_abs_path_eval_finalized
        )
        target_dst_dir_path = os.path.join(
            "target_dir",
        )
        self.fs.create_dir(target_dst_dir_path)
        self.fs.create_symlink(
            state_client_conf_env_dir_abs_path_eval_finalized,
            target_dst_dir_path,
        )
        mock_state_client_local_env_dir_rel_path_eval_finalized.return_value = (
            target_dst_dir_path
        )
        mock_state_client_local_env_dir_rel_path_eval_verified.return_value = True

        # when:

        self.env_ctx.state_graph.eval_state(
            EnvState.state_client_conf_env_dir_abs_path_eval_verified.name
        )

        # then:

        # no exception happens

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_local_env_dir_rel_path_eval_verified.__name__}._eval_state_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_local_env_dir_rel_path_eval_finalized.__name__}._eval_state_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_env_dir_abs_path_eval_finalized.__name__}._eval_state_once"
    )
    def test_failure_when_conf_symlink_exists_but_target_dst_dir_mismatches(
        self,
        mock_state_client_conf_env_dir_abs_path_eval_finalized,
        mock_state_client_local_env_dir_rel_path_eval_finalized,
        mock_state_client_local_env_dir_rel_path_eval_verified,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_client_conf_env_dir_abs_path_eval_verified,
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
            ConfConstClient.default_dir_rel_path_leap_env_link_name,
        )
        mock_state_client_conf_env_dir_abs_path_eval_finalized.return_value = (
            state_client_conf_env_dir_abs_path_eval_finalized
        )
        self.fs.create_dir(actual_target_dir)
        self.fs.create_dir(expected_target_dir)
        self.fs.create_symlink(
            state_client_conf_env_dir_abs_path_eval_finalized,
            actual_target_dir,
        )

        mock_state_client_local_env_dir_rel_path_eval_finalized.return_value = (
            expected_target_dir
        )
        mock_state_client_local_env_dir_rel_path_eval_verified.return_value = True

        # when:

        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.state_graph.eval_state(
                EnvState.state_client_conf_env_dir_abs_path_eval_verified.name
            )

        # then:

        self.assertIn("not the same as the provided target", str(ctx.exception))

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_local_env_dir_rel_path_eval_verified.__name__}._eval_state_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_local_env_dir_rel_path_eval_finalized.__name__}._eval_state_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_env_dir_abs_path_eval_finalized.__name__}._eval_state_once"
    )
    def test_failure_when_conf_symlink_is_not_directory(
        self,
        mock_state_client_conf_env_dir_abs_path_eval_finalized,
        mock_state_client_local_env_dir_rel_path_eval_finalized,
        mock_state_client_local_env_dir_rel_path_eval_verified,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_client_conf_env_dir_abs_path_eval_verified,
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
        state_client_conf_env_dir_abs_path_eval_finalized = os.path.join(
            mock_client_dir,
            ConfConstClient.default_dir_rel_path_leap_env_link_name,
        )
        mock_state_client_conf_env_dir_abs_path_eval_finalized.return_value = (
            state_client_conf_env_dir_abs_path_eval_finalized
        )
        self.fs.create_file(mock_not_a_dir)
        self.fs.create_symlink(
            state_client_conf_env_dir_abs_path_eval_finalized,
            mock_not_a_dir,
        )
        mock_state_client_local_env_dir_rel_path_eval_finalized.return_value = (
            mock_not_a_dir
        )
        mock_state_client_local_env_dir_rel_path_eval_verified.return_value = True

        # when:

        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.state_graph.eval_state(
                EnvState.state_client_conf_env_dir_abs_path_eval_verified.name
            )

        # then:

        self.assertIn("target is not a directory", str(ctx.exception))

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_local_env_dir_rel_path_eval_verified.__name__}._eval_state_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_local_env_dir_rel_path_eval_finalized.__name__}._eval_state_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_env_dir_abs_path_eval_finalized.__name__}._eval_state_once"
    )
    def test_failure_when_conf_is_not_symlink(
        self,
        mock_state_client_conf_env_dir_abs_path_eval_finalized,
        mock_state_client_local_env_dir_rel_path_eval_finalized,
        mock_state_client_local_env_dir_rel_path_eval_verified,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_client_conf_env_dir_abs_path_eval_verified,
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

        state_client_conf_env_dir_abs_path_eval_finalized = os.path.join(
            mock_client_dir,
            ConfConstClient.default_dir_rel_path_leap_env_link_name,
        )
        mock_state_client_conf_env_dir_abs_path_eval_finalized.return_value = (
            state_client_conf_env_dir_abs_path_eval_finalized
        )
        self.fs.create_dir(state_client_conf_env_dir_abs_path_eval_finalized)
        client_script_basename = "client_script.py"
        test_args = [
            client_script_basename,
        ]

        mock_state_client_local_env_dir_rel_path_eval_finalized.return_value = (
            "some_dir"
        )
        mock_state_client_local_env_dir_rel_path_eval_verified.return_value = True

        # when:

        with patch.object(sys, "argv", test_args):
            with self.assertRaises(AssertionError) as ctx:
                self.env_ctx.state_graph.eval_state(
                    EnvState.state_client_conf_env_dir_abs_path_eval_verified.name
                )

        # then:

        self.assertIn("is not a symlink", str(ctx.exception))

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_local_env_dir_rel_path_eval_verified.__name__}._eval_state_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_local_env_dir_rel_path_eval_finalized.__name__}._eval_state_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_env_dir_abs_path_eval_finalized.__name__}._eval_state_once"
    )
    def test_success_when_conf_symlink_is_created_if_it_is_missing_and_target_dir_is_given(
        self,
        mock_state_client_conf_env_dir_abs_path_eval_finalized,
        mock_state_client_local_env_dir_rel_path_eval_finalized,
        mock_state_client_local_env_dir_rel_path_eval_verified,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_client_conf_env_dir_abs_path_eval_verified,
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
        state_client_conf_env_dir_abs_path_eval_finalized = os.path.join(
            mock_client_dir,
            ConfConstClient.default_dir_rel_path_leap_env_link_name,
        )
        mock_state_client_conf_env_dir_abs_path_eval_finalized.return_value = (
            state_client_conf_env_dir_abs_path_eval_finalized
        )
        self.fs.create_dir(target_dst_dir_path)

        mock_state_client_local_env_dir_rel_path_eval_finalized.return_value = (
            target_dst_dir_path
        )
        mock_state_client_local_env_dir_rel_path_eval_verified.return_value = True

        # when:

        self.env_ctx.state_graph.eval_state(
            EnvState.state_client_conf_env_dir_abs_path_eval_verified.name
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
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_local_env_dir_rel_path_eval_verified.__name__}._eval_state_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_local_env_dir_rel_path_eval_finalized.__name__}._eval_state_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_env_dir_abs_path_eval_finalized.__name__}._eval_state_once"
    )
    def test_success_when_conf_symlink_is_created_with_normalized_target(
        self,
        mock_state_client_conf_env_dir_abs_path_eval_finalized,
        mock_state_client_local_env_dir_rel_path_eval_finalized,
        mock_state_client_local_env_dir_rel_path_eval_verified,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_client_conf_env_dir_abs_path_eval_verified,
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
        state_client_conf_env_dir_abs_path_eval_finalized = os.path.join(
            mock_client_dir,
            ConfConstClient.default_dir_rel_path_leap_env_link_name,
        )
        mock_state_client_conf_env_dir_abs_path_eval_finalized.return_value = (
            state_client_conf_env_dir_abs_path_eval_finalized
        )
        self.fs.create_dir(target_dst_dir_path_normalized)

        mock_state_client_local_env_dir_rel_path_eval_finalized.return_value = (
            target_dst_dir_path_non_normalized
        )
        mock_state_client_local_env_dir_rel_path_eval_verified.return_value = True

        # when:

        self.env_ctx.state_graph.eval_state(
            EnvState.state_client_conf_env_dir_abs_path_eval_verified.name
        )

        # then:

        self.assertTrue(
            os.path.islink(state_client_conf_env_dir_abs_path_eval_finalized)
        )
        self.assertEqual(
            os.readlink(state_client_conf_env_dir_abs_path_eval_finalized),
            target_dst_dir_path_normalized,
        )
