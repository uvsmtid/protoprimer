import argparse
from unittest.mock import patch

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_args_parsed,
    CommandArg,
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
            EnvState.state_client_local_env_dir_rel_path_eval_verified.name
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}._eval_state_once"
    )
    def test_success_on_valid_relative_dir(
        self,
        mock_state_args_parsed,
    ):

        # given:

        self.fs.create_dir("valid_dir")
        mock_state_args_parsed.return_value = argparse.Namespace(
            **{CommandArg.name_local_env.value: "valid_dir"},
        )

        # when:

        self.env_ctx.state_graph.eval_state(
            EnvState.state_client_local_env_dir_rel_path_eval_verified.name
        )

        # then:

        # no exception happens

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}._eval_state_once"
    )
    def test_failure_on_absolute_path(
        self,
        mock_state_args_parsed,
    ):

        # given:

        mock_state_args_parsed.return_value = argparse.Namespace(
            **{CommandArg.name_local_env.value: "/abs/path"},
        )

        # when:

        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.state_graph.eval_state(
                EnvState.state_client_local_env_dir_rel_path_eval_verified.name
            )

        # then:

        self.assertIn("must not be absolute", str(ctx.exception))

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}._eval_state_once"
    )
    def test_failure_on_path_with_dot_dot(
        self,
        mock_state_args_parsed,
    ):

        # given:

        mock_state_args_parsed.return_value = argparse.Namespace(
            **{CommandArg.name_local_env.value: "conf/../bad"},
        )

        # when:

        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.state_graph.eval_state(
                EnvState.state_client_local_env_dir_rel_path_eval_verified.name
            )

        # then:

        self.assertIn("must not contain `..`", str(ctx.exception))

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}._eval_state_once"
    )
    def test_failure_on_non_directory_path(
        self,
        mock_state_args_parsed,
    ):

        # given:

        self.fs.create_file("not_a_dir")
        mock_state_args_parsed.return_value = argparse.Namespace(
            **{CommandArg.name_local_env.value: "not_a_dir"},
        )

        # when:

        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.state_graph.eval_state(
                EnvState.state_client_local_env_dir_rel_path_eval_verified.name
            )

        # then:

        self.assertIn("must lead to a directory", str(ctx.exception))

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}._eval_state_once"
    )
    def test_failure_on_non_existent_path(
        self,
        mock_state_args_parsed,
    ):

        # given:

        mock_state_args_parsed.return_value = argparse.Namespace(
            **{CommandArg.name_local_env.value: "missing_dir"},
        )

        # when:

        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.state_graph.eval_state(
                EnvState.state_client_local_env_dir_rel_path_eval_verified.name
            )

        # then:

        self.assertIn("must lead to a directory", str(ctx.exception))

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}._eval_state_once"
    )
    def test_success_on_symlink_leading_to_a_dir(
        self,
        mock_state_args_parsed,
    ):

        # given:

        self.fs.create_dir("valid_dir")
        self.fs.create_symlink("symlink_to_dir", "valid_dir")
        mock_state_args_parsed.return_value = argparse.Namespace(
            **{CommandArg.name_local_env.value: "symlink_to_dir"},
        )

        # when:

        self.env_ctx.state_graph.eval_state(
            EnvState.state_client_local_env_dir_rel_path_eval_verified.name
        )

        # then:

        # no exception happens
