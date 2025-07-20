import argparse
from unittest.mock import patch

from local_test.name_assertion import assert_test_module_name_embeds_str
from local_test.base_test_class import BasePyfakefsTestClass
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    ArgConst,
    Bootstrapper_state_args_parsed,
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
            EnvState.state_target_env_dir_rel_path_verified.name
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}._bootstrap_once"
    )
    def test_success_on_valid_relative_dir(
        self,
        mock_state_args_parsed,
    ):

        # given:

        self.fs.create_dir("valid_dir")
        mock_state_args_parsed.return_value = argparse.Namespace(
            **{ArgConst.name_target_env_dir_rel_path: "valid_dir"},
        )

        # when:

        self.env_ctx.bootstrap_state(
            EnvState.state_target_env_dir_rel_path_verified.name
        )

        # then:

        # no exception happens

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}._bootstrap_once"
    )
    def test_failure_on_absolute_path(
        self,
        mock_state_args_parsed,
    ):

        # given:

        mock_state_args_parsed.return_value = argparse.Namespace(
            **{ArgConst.name_target_env_dir_rel_path: "/abs/path"},
        )

        # when:

        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.bootstrap_state(
                EnvState.state_target_env_dir_rel_path_verified.name
            )

        # then:

        self.assertIn("must not be absolute", str(ctx.exception))

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}._bootstrap_once"
    )
    def test_failure_on_path_with_dot_dot(
        self,
        mock_state_args_parsed,
    ):

        # given:

        mock_state_args_parsed.return_value = argparse.Namespace(
            **{ArgConst.name_target_env_dir_rel_path: "conf/../bad"},
        )

        # when:

        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.bootstrap_state(
                EnvState.state_target_env_dir_rel_path_verified.name
            )

        # then:

        self.assertIn("must not contain `..`", str(ctx.exception))

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}._bootstrap_once"
    )
    def test_failure_on_non_directory_path(
        self,
        mock_state_args_parsed,
    ):

        # given:

        self.fs.create_file("not_a_dir")
        mock_state_args_parsed.return_value = argparse.Namespace(
            **{ArgConst.name_target_env_dir_rel_path: "not_a_dir"},
        )

        # when:

        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.bootstrap_state(
                EnvState.state_target_env_dir_rel_path_verified.name
            )

        # then:

        self.assertIn("must lead to a directory", str(ctx.exception))

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}._bootstrap_once"
    )
    def test_failure_on_non_existent_path(
        self,
        mock_state_args_parsed,
    ):

        # given:

        mock_state_args_parsed.return_value = argparse.Namespace(
            **{ArgConst.name_target_env_dir_rel_path: "missing_dir"},
        )

        # when:

        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.bootstrap_state(
                EnvState.state_target_env_dir_rel_path_verified.name
            )

        # then:

        self.assertIn("must lead to a directory", str(ctx.exception))

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}._bootstrap_once"
    )
    def test_success_on_symlink_leading_to_a_dir(
        self,
        mock_state_args_parsed,
    ):

        # given:

        self.fs.create_dir("valid_dir")
        self.fs.create_symlink("symlink_to_dir", "valid_dir")
        mock_state_args_parsed.return_value = argparse.Namespace(
            **{ArgConst.name_target_env_dir_rel_path: "symlink_to_dir"},
        )

        # when:

        self.env_ctx.bootstrap_state(
            EnvState.state_target_env_dir_rel_path_verified.name
        )

        # then:

        # no exception happens
