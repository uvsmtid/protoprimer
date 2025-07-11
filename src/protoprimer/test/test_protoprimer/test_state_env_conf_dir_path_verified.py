import argparse
import os
import sys
from unittest.mock import patch

from local_test import (
    assert_test_module_name_embeds_str,
    BasePyfakefsTestClass,
)
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    ArgConst,
    Bootstrapper_state_env_conf_dir_path,
    Bootstrapper_state_parsed_args,
    ConfConstClient,
    EnvContext,
    EnvState,
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
            EnvState.state_env_conf_dir_path_verified.name
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_env_conf_dir_path.__name__}.bootstrap_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_parsed_args.__name__}._bootstrap_once"
    )
    def test_success_when_conf_symlink_exists_and_target_dst_dir_unspecified(
        self,
        mock_state_parsed_args,
        mock_state_env_conf_dir_path,
    ):
        # given:
        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)
        state_env_conf_dir_path = os.path.join(
            mock_client_dir,
            ConfConstClient.default_dir_rel_path_conf_env_link_name,
        )
        mock_state_env_conf_dir_path.return_value = state_env_conf_dir_path
        mock_target_dir = os.path.join(
            "target_dir",
        )
        self.fs.create_dir(mock_target_dir)
        self.fs.create_symlink(
            state_env_conf_dir_path,
            mock_target_dir,
        )
        client_script_basename = "client_script.py"
        test_args = [
            client_script_basename,
        ]
        mock_state_parsed_args.return_value = argparse.Namespace(
            **{
                ArgConst.name_conf_env_path: None,
                ArgConst.name_py_exec: PythonExecutable.py_exec_unknown.name,
                ArgConst.name_client_dir_path: mock_client_dir,
            },
        )

        # when:
        with patch.object(sys, "argv", test_args):
            self.env_ctx.bootstrap_state(EnvState.state_env_conf_dir_path_verified.name)

        # then:
        # no exception happens

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_env_conf_dir_path.__name__}.bootstrap_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_parsed_args.__name__}._bootstrap_once"
    )
    def test_success_when_conf_symlink_exists_and_target_dst_dir_matches(
        self,
        mock_state_parsed_args,
        mock_state_env_conf_dir_path,
    ):
        # given:
        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)
        state_env_conf_dir_path = os.path.join(
            mock_client_dir,
            ConfConstClient.default_dir_rel_path_conf_env_link_name,
        )
        mock_state_env_conf_dir_path.return_value = state_env_conf_dir_path
        target_dst_dir_path = os.path.join(
            "target_dir",
        )
        mock_state_parsed_args.return_value = argparse.Namespace(
            **{ArgConst.name_conf_env_path: target_dst_dir_path},
        )
        self.fs.create_dir(target_dst_dir_path)
        self.fs.create_symlink(
            state_env_conf_dir_path,
            target_dst_dir_path,
        )

        # when:
        self.env_ctx.bootstrap_state(EnvState.state_env_conf_dir_path_verified.name)

        # then:
        # no exception happens

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_env_conf_dir_path.__name__}.bootstrap_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_parsed_args.__name__}._bootstrap_once"
    )
    def test_failure_when_conf_symlink_exists_but_target_dst_dir_mismatches(
        self,
        mock_state_parsed_args,
        mock_state_env_conf_dir_path,
    ):
        # given:
        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)
        actual_target_dir = os.path.join(
            "actual_target_dir",
        )
        expected_target_dir = os.path.join(
            "expected_target_dir",
        )
        state_env_conf_dir_path = os.path.join(
            ConfConstClient.default_dir_rel_path_conf_env_link_name,
        )
        mock_state_env_conf_dir_path.return_value = state_env_conf_dir_path
        self.fs.create_dir(actual_target_dir)
        self.fs.create_dir(expected_target_dir)
        self.fs.create_symlink(
            state_env_conf_dir_path,
            actual_target_dir,
        )
        mock_state_parsed_args.return_value = argparse.Namespace(
            **{ArgConst.name_conf_env_path: expected_target_dir},
        )

        # when:
        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.bootstrap_state(EnvState.state_env_conf_dir_path_verified.name)

        # then:
        self.assertIn("not the same as the provided target", str(ctx.exception))

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_env_conf_dir_path.__name__}.bootstrap_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_parsed_args.__name__}._bootstrap_once"
    )
    def test_failure_when_conf_symlink_is_not_directory(
        self,
        mock_state_parsed_args,
        mock_state_env_conf_dir_path,
    ):
        # given:
        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)
        mock_not_a_dir = os.path.join(
            "file",
        )
        state_env_conf_dir_path = os.path.join(
            mock_client_dir,
            ConfConstClient.default_dir_rel_path_conf_env_link_name,
        )
        mock_state_env_conf_dir_path.return_value = state_env_conf_dir_path
        self.fs.create_file(mock_not_a_dir)
        self.fs.create_symlink(
            state_env_conf_dir_path,
            mock_not_a_dir,
        )
        mock_state_parsed_args.return_value = argparse.Namespace(
            **{ArgConst.name_conf_env_path: mock_not_a_dir},
        )

        # when:
        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.bootstrap_state(EnvState.state_env_conf_dir_path_verified.name)

        # then:
        self.assertIn("target is not a directory", str(ctx.exception))

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_env_conf_dir_path.__name__}.bootstrap_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_parsed_args.__name__}._bootstrap_once"
    )
    def test_failure_when_conf_is_not_symlink(
        self,
        mock_state_parsed_args,
        mock_state_env_conf_dir_path,
    ):
        # given:
        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)
        state_env_conf_dir_path = os.path.join(
            mock_client_dir,
            ConfConstClient.default_dir_rel_path_conf_env_link_name,
        )
        mock_state_env_conf_dir_path.return_value = state_env_conf_dir_path
        self.fs.create_dir(state_env_conf_dir_path)
        client_script_basename = "client_script.py"
        test_args = [
            client_script_basename,
        ]
        mock_state_parsed_args.return_value = argparse.Namespace(
            **{
                ArgConst.name_conf_env_path: None,
                ArgConst.name_py_exec: PythonExecutable.py_exec_unknown.name,
                ArgConst.name_client_dir_path: mock_client_dir,
            },
        )

        # when:

        with patch.object(sys, "argv", test_args):
            with self.assertRaises(AssertionError) as ctx:
                self.env_ctx.bootstrap_state(
                    EnvState.state_env_conf_dir_path_verified.name
                )

        # then:
        self.assertIn("is not a symlink", str(ctx.exception))

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_env_conf_dir_path.__name__}.bootstrap_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_parsed_args.__name__}._bootstrap_once"
    )
    def test_success_when_conf_symlink_is_created_if_it_is_missing_and_target_dir_is_given(
        self,
        mock_state_parsed_args,
        mock_state_env_conf_dir_path,
    ):
        # given:
        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)
        target_dst_dir_path = os.path.join(
            "target_dir",
        )
        mock_state_parsed_args.return_value = argparse.Namespace(
            **{ArgConst.name_conf_env_path: target_dst_dir_path},
        )
        state_env_conf_dir_path = os.path.join(
            mock_client_dir,
            ConfConstClient.default_dir_rel_path_conf_env_link_name,
        )
        mock_state_env_conf_dir_path.return_value = state_env_conf_dir_path
        self.fs.create_dir(target_dst_dir_path)

        # when:
        self.env_ctx.bootstrap_state(EnvState.state_env_conf_dir_path_verified.name)

        # then:
        self.assertTrue(os.path.islink(state_env_conf_dir_path))
        self.assertEqual(
            os.readlink(state_env_conf_dir_path),
            target_dst_dir_path,
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_env_conf_dir_path.__name__}.bootstrap_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_parsed_args.__name__}._bootstrap_once"
    )
    def test_success_when_conf_symlink_is_created_with_normalized_target(
        self,
        mock_state_parsed_args,
        mock_state_env_conf_dir_path,
    ):
        # given:
        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)
        target_dst_dir_path_non_normalized = "target_dir/"
        target_dst_dir_path_normalized = "target_dir"
        mock_state_parsed_args.return_value = argparse.Namespace(
            **{ArgConst.name_conf_env_path: target_dst_dir_path_non_normalized},
        )
        state_env_conf_dir_path = os.path.join(
            mock_client_dir,
            ConfConstClient.default_dir_rel_path_conf_env_link_name,
        )
        mock_state_env_conf_dir_path.return_value = state_env_conf_dir_path
        self.fs.create_dir(target_dst_dir_path_normalized)

        # when:
        self.env_ctx.bootstrap_state(EnvState.state_env_conf_dir_path_verified.name)

        # then:
        self.assertTrue(os.path.islink(state_env_conf_dir_path))
        self.assertEqual(
            os.readlink(state_env_conf_dir_path),
            target_dst_dir_path_normalized,
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_env_conf_dir_path.__name__}.bootstrap_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_parsed_args.__name__}._bootstrap_once"
    )
    def test_failure_when_conf_symlink_is_missing_and_no_target_dir_is_given(
        self,
        mock_state_parsed_args,
        mock_state_env_conf_dir_path,
    ):
        # given:
        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)
        mock_state_parsed_args.return_value = argparse.Namespace(
            **{ArgConst.name_conf_env_path: None},
        )
        state_env_conf_dir_path = os.path.join(
            mock_client_dir,
            ConfConstClient.default_dir_rel_path_conf_env_link_name,
        )
        mock_state_env_conf_dir_path.return_value = state_env_conf_dir_path
        client_script_basename = "client_script.py"
        test_args = [
            client_script_basename,
        ]
        mock_state_parsed_args.return_value = argparse.Namespace(
            **{
                ArgConst.name_conf_env_path: None,
                ArgConst.name_py_exec: PythonExecutable.py_exec_unknown.name,
                ArgConst.name_client_dir_path: mock_client_dir,
            },
        )

        # when:
        with patch.object(sys, "argv", test_args):
            with self.assertRaises(AssertionError) as ctx:
                self.env_ctx.bootstrap_state(
                    EnvState.state_env_conf_dir_path_verified.name
                )

        # then:
        self.assertIn("not provided", str(ctx.exception))
