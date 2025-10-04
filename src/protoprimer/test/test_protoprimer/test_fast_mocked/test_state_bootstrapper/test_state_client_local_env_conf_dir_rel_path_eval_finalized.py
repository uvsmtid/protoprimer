import argparse
import os
from unittest.mock import patch

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.mock_verifier import (
    assert_parent_states_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_args_parsed,
    Bootstrapper_state_client_conf_file_data,
    Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized,
    ConfField,
    EnvContext,
    EnvState,
)


# noinspection PyPep8Naming
class ThisTestClass(BasePyfakefsTestClass):

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = EnvContext()
        self.mock_ref_root = "/mock_ref_root"
        self.fs.create_dir(self.mock_ref_root)

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_str(
            EnvState.state_client_local_env_conf_dir_rel_path_eval_finalized.name
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data.__name__}.eval_own_state"
    )
    def test_success_when_arg_is_present_and_rel_to_cwd(
        self,
        mock_state_client_conf_file_data,
        mock_state_args_parsed,
        mock_state_primer_ref_root_dir_abs_path_eval_finalized,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_client_local_env_conf_dir_rel_path_eval_finalized.name,
        )
        mock_state_primer_ref_root_dir_abs_path_eval_finalized.return_value = (
            self.mock_ref_root
        )

        # This should be ignored:
        client_conf_file_data = {
            ConfField.field_client_default_env_dir_rel_path.value: "my_env_dir_from_conf",
        }
        self.fs.create_dir(os.path.join(self.mock_ref_root, "my_env_dir_from_conf"))
        mock_state_client_conf_file_data.return_value = client_conf_file_data

        # This should be used:
        arg_value = "my_env_dir_from_arg"
        # Create it inside ref_root, and CWD will be ref_root
        os.chdir(self.mock_ref_root)
        self.fs.create_dir(arg_value)
        mock_state_args_parsed.return_value = argparse.Namespace(
            **{primer_kernel.ParsedArg.name_local_env_conf_dir.value: arg_value}
        )

        # when:
        state_client_local_env_conf_dir_rel_path_eval_finalized = (
            self.env_ctx.state_graph.eval_state(
                EnvState.state_client_local_env_conf_dir_rel_path_eval_finalized.name
            )
        )

        # then:
        self.assertEqual(
            state_client_local_env_conf_dir_rel_path_eval_finalized, arg_value
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data.__name__}.eval_own_state"
    )
    def test_success_when_arg_is_present_and_rel_to_ref_root(
        self,
        mock_state_client_conf_file_data,
        mock_state_args_parsed,
        mock_state_primer_ref_root_dir_abs_path_eval_finalized,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_client_local_env_conf_dir_rel_path_eval_finalized.name,
        )
        mock_state_primer_ref_root_dir_abs_path_eval_finalized.return_value = (
            self.mock_ref_root
        )
        os.chdir("/")  # change cwd to something else

        # This should be ignored:
        client_conf_file_data = {
            ConfField.field_client_default_env_dir_rel_path.value: "my_env_dir_from_conf",
        }
        self.fs.create_dir(os.path.join(self.mock_ref_root, "my_env_dir_from_conf"))
        mock_state_client_conf_file_data.return_value = client_conf_file_data

        # This should be used:
        arg_value = "my_env_dir_from_arg"
        self.fs.create_dir(os.path.join(self.mock_ref_root, arg_value))
        mock_state_args_parsed.return_value = argparse.Namespace(
            **{primer_kernel.ParsedArg.name_local_env_conf_dir.value: arg_value}
        )

        # when:
        state_client_local_env_conf_dir_rel_path_eval_finalized = (
            self.env_ctx.state_graph.eval_state(
                EnvState.state_client_local_env_conf_dir_rel_path_eval_finalized.name
            )
        )

        # then:
        self.assertEqual(
            state_client_local_env_conf_dir_rel_path_eval_finalized, arg_value
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data.__name__}.eval_own_state"
    )
    def test_success_when_default_field_is_present(
        self,
        mock_state_client_conf_file_data,
        mock_state_args_parsed,
        mock_state_primer_ref_root_dir_abs_path_eval_finalized,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_client_local_env_conf_dir_rel_path_eval_finalized.name,
        )
        mock_state_primer_ref_root_dir_abs_path_eval_finalized.return_value = (
            self.mock_ref_root
        )
        os.chdir(self.mock_ref_root)

        mock_state_args_parsed.return_value = argparse.Namespace(
            **{primer_kernel.ParsedArg.name_local_env_conf_dir.value: None}
        )

        client_conf_file_data = {
            ConfField.field_client_default_env_dir_rel_path.value: "my_env_dir",
        }
        self.fs.create_dir("my_env_dir")
        mock_state_client_conf_file_data.return_value = client_conf_file_data

        # when:
        state_client_local_env_conf_dir_rel_path_eval_finalized = (
            self.env_ctx.state_graph.eval_state(
                EnvState.state_client_local_env_conf_dir_rel_path_eval_finalized.name
            )
        )

        # then:
        self.assertEqual(
            state_client_local_env_conf_dir_rel_path_eval_finalized, "my_env_dir"
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data.__name__}.eval_own_state"
    )
    def test_failure_when_default_field_is_missing(
        self,
        mock_state_client_conf_file_data,
        mock_state_args_parsed,
        mock_state_primer_ref_root_dir_abs_path_eval_finalized,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_client_local_env_conf_dir_rel_path_eval_finalized.name,
        )
        mock_state_primer_ref_root_dir_abs_path_eval_finalized.return_value = (
            self.mock_ref_root
        )
        os.chdir(self.mock_ref_root)

        mock_state_args_parsed.return_value = argparse.Namespace(
            **{primer_kernel.ParsedArg.name_local_env_conf_dir.value: None}
        )

        client_conf_file_data = {}
        mock_state_client_conf_file_data.return_value = client_conf_file_data

        # when:
        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.state_graph.eval_state(
                EnvState.state_client_local_env_conf_dir_rel_path_eval_finalized.name
            )

        # then:
        self.assertIn(
            f"Field `{ConfField.field_client_default_env_dir_rel_path.value}` is [None]",
            str(ctx.exception),
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data.__name__}.eval_own_state"
    )
    def test_failure_when_path_is_not_a_dir(
        self,
        mock_state_client_conf_file_data,
        mock_state_args_parsed,
        mock_state_primer_ref_root_dir_abs_path_eval_finalized,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_client_local_env_conf_dir_rel_path_eval_finalized.name,
        )
        mock_state_primer_ref_root_dir_abs_path_eval_finalized.return_value = (
            self.mock_ref_root
        )
        os.chdir(self.mock_ref_root)

        mock_state_args_parsed.return_value = argparse.Namespace(
            **{primer_kernel.ParsedArg.name_local_env_conf_dir.value: None}
        )

        client_conf_file_data = {
            ConfField.field_client_default_env_dir_rel_path.value: "not_a_dir",
        }
        self.fs.create_file("not_a_dir")
        mock_state_client_conf_file_data.return_value = client_conf_file_data

        # when:
        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.state_graph.eval_state(
                EnvState.state_client_local_env_conf_dir_rel_path_eval_finalized.name
            )

        # then:
        self.assertIn("is relative to neither", str(ctx.exception))

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data.__name__}.eval_own_state"
    )
    def test_failure_when_default_path_from_conf_is_absolute(
        self,
        mock_state_client_conf_file_data,
        mock_state_args_parsed,
        mock_state_primer_ref_root_dir_abs_path_eval_finalized,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_client_local_env_conf_dir_rel_path_eval_finalized.name,
        )
        mock_state_primer_ref_root_dir_abs_path_eval_finalized.return_value = (
            self.mock_ref_root
        )
        os.chdir(self.mock_ref_root)

        mock_state_args_parsed.return_value = argparse.Namespace(
            **{primer_kernel.ParsedArg.name_local_env_conf_dir.value: None}
        )

        client_conf_file_data = {
            ConfField.field_client_default_env_dir_rel_path.value: "/abs/path",
        }
        mock_state_client_conf_file_data.return_value = client_conf_file_data

        # when:
        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.state_graph.eval_state(
                EnvState.state_client_local_env_conf_dir_rel_path_eval_finalized.name
            )

        # then:
        self.assertIn("must be a relative path", str(ctx.exception))

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data.__name__}.eval_own_state"
    )
    def test_failure_when_path_from_conf_is_outside_ref_root(
        self,
        mock_state_client_conf_file_data,
        mock_state_args_parsed,
        mock_state_primer_ref_root_dir_abs_path_eval_finalized,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_client_local_env_conf_dir_rel_path_eval_finalized.name,
        )
        mock_state_primer_ref_root_dir_abs_path_eval_finalized.return_value = (
            self.mock_ref_root
        )
        os.chdir(self.mock_ref_root)

        mock_state_client_conf_file_data.return_value = {}  # Should be ignored

        arg_value = "/abs/path/outside/ref_root"
        self.fs.create_dir(arg_value)
        mock_state_args_parsed.return_value = argparse.Namespace(
            **{primer_kernel.ParsedArg.name_local_env_conf_dir.value: arg_value}
        )

        # when:
        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.state_graph.eval_state(
                EnvState.state_client_local_env_conf_dir_rel_path_eval_finalized.name
            )

        # then:
        self.assertIn("is not under", str(ctx.exception))

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data.__name__}.eval_own_state"
    )
    def test_success_when_path_from_conf_is_inside_ref_root(
        self,
        mock_state_client_conf_file_data,
        mock_state_args_parsed,
        mock_state_primer_ref_root_dir_abs_path_eval_finalized,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_client_local_env_conf_dir_rel_path_eval_finalized.name,
        )
        mock_state_primer_ref_root_dir_abs_path_eval_finalized.return_value = (
            self.mock_ref_root
        )
        os.chdir(self.mock_ref_root)

        mock_state_client_conf_file_data.return_value = {}  # Should be ignored

        arg_value_rel = "my_env"
        arg_value_abs = os.path.join(self.mock_ref_root, arg_value_rel)
        self.fs.create_dir(arg_value_abs)
        mock_state_args_parsed.return_value = argparse.Namespace(
            **{primer_kernel.ParsedArg.name_local_env_conf_dir.value: arg_value_abs}
        )

        # when:
        result = self.env_ctx.state_graph.eval_state(
            EnvState.state_client_local_env_conf_dir_rel_path_eval_finalized.name
        )

        # then:
        self.assertEqual(result, arg_value_rel)

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data.__name__}.eval_own_state"
    )
    def test_failure_when_path_does_not_exist(
        self,
        mock_state_client_conf_file_data,
        mock_state_args_parsed,
        mock_state_primer_ref_root_dir_abs_path_eval_finalized,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_client_local_env_conf_dir_rel_path_eval_finalized.name,
        )
        mock_state_primer_ref_root_dir_abs_path_eval_finalized.return_value = (
            self.mock_ref_root
        )
        os.chdir(self.mock_ref_root)

        mock_state_args_parsed.return_value = argparse.Namespace(
            **{primer_kernel.ParsedArg.name_local_env_conf_dir.value: None}
        )

        client_conf_file_data = {
            ConfField.field_client_default_env_dir_rel_path.value: "missing_dir",
        }
        mock_state_client_conf_file_data.return_value = client_conf_file_data

        # when:
        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.state_graph.eval_state(
                EnvState.state_client_local_env_conf_dir_rel_path_eval_finalized.name
            )

        # then:
        self.assertIn("is relative to neither", str(ctx.exception))

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data.__name__}.eval_own_state"
    )
    def test_success_when_path_leads_to_a_dir(
        self,
        mock_state_client_conf_file_data,
        mock_state_args_parsed,
        mock_state_primer_ref_root_dir_abs_path_eval_finalized,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_client_local_env_conf_dir_rel_path_eval_finalized.name,
        )
        mock_state_primer_ref_root_dir_abs_path_eval_finalized.return_value = (
            self.mock_ref_root
        )
        os.chdir(self.mock_ref_root)

        mock_state_args_parsed.return_value = argparse.Namespace(
            **{primer_kernel.ParsedArg.name_local_env_conf_dir.value: None}
        )

        self.fs.create_dir("valid_dir")
        self.fs.create_symlink("symlink_to_dir", "valid_dir")
        client_conf_file_data = {
            ConfField.field_client_default_env_dir_rel_path.value: "symlink_to_dir",
        }
        mock_state_client_conf_file_data.return_value = client_conf_file_data

        # when:
        result = self.env_ctx.state_graph.eval_state(
            EnvState.state_client_local_env_conf_dir_rel_path_eval_finalized.name
        )

        # then:
        self.assertEqual(result, "symlink_to_dir")

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data.__name__}.eval_own_state"
    )
    def test_failure_when_path_from_arg_is_not_a_dir(
        self,
        mock_state_client_conf_file_data,
        mock_state_args_parsed,
        mock_state_primer_ref_root_dir_abs_path_eval_finalized,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_client_local_env_conf_dir_rel_path_eval_finalized.name,
        )
        mock_state_primer_ref_root_dir_abs_path_eval_finalized.return_value = (
            self.mock_ref_root
        )
        os.chdir(self.mock_ref_root)

        mock_state_client_conf_file_data.return_value = {}  # Should be ignored

        arg_value = "/abs/path/not_a_dir"
        self.fs.create_file(arg_value)
        mock_state_args_parsed.return_value = argparse.Namespace(
            **{primer_kernel.ParsedArg.name_local_env_conf_dir.value: arg_value}
        )

        # when:
        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.state_graph.eval_state(
                EnvState.state_client_local_env_conf_dir_rel_path_eval_finalized.name
            )

        # then:
        self.assertIn(
            f"`{primer_kernel.PathName.path_local_env_conf.value}` [{arg_value}] must be a dir.",
            str(ctx.exception),
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data.__name__}.eval_own_state"
    )
    def test_success_when_arg_is_present_and_sub_dir_to_ref_root_but_rel_to_curr_dir(
        self,
        mock_state_client_conf_file_data,
        mock_state_args_parsed,
        mock_state_primer_ref_root_dir_abs_path_eval_finalized,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_client_local_env_conf_dir_rel_path_eval_finalized.name,
        )
        mock_state_primer_ref_root_dir_abs_path_eval_finalized.return_value = (
            self.mock_ref_root
        )

        # This should be ignored:
        client_conf_file_data = {
            ConfField.field_client_default_env_dir_rel_path.value: "my_env_dir_from_conf",
        }
        self.fs.create_dir(os.path.join(self.mock_ref_root, "my_env_dir_from_conf"))
        mock_state_client_conf_file_data.return_value = client_conf_file_data

        # This should be used:
        arg_value = "my_env_dir_from_arg"

        # Create a different CWD
        mock_cwd = os.path.join(self.mock_ref_root, "subdir")
        self.fs.create_dir(mock_cwd)
        os.chdir(mock_cwd)

        self.fs.create_dir(arg_value)
        mock_state_args_parsed.return_value = argparse.Namespace(
            **{primer_kernel.ParsedArg.name_local_env_conf_dir.value: arg_value}
        )

        # when:
        result = self.env_ctx.state_graph.eval_state(
            EnvState.state_client_local_env_conf_dir_rel_path_eval_finalized.name
        )

        # then:
        self.assertEqual(result, os.path.join("subdir", arg_value))
