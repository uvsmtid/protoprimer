import os
import sys
from unittest.mock import patch

from local_repo.cmd_prime_env import customize_env_context
from local_test.base_test_class import BasePyfakefsTestClass
from local_test.mock_verifier import (
    assert_parent_factories_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from neoprimer import pre_commit
from neoprimer.pre_commit import (
    Bootstrapper_state_pre_commit_configured,
)
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_command_executed,
    Bootstrapper_state_global_conf_file_abs_path_inited,
    Bootstrapper_state_ref_root_dir_abs_path_inited,
    write_json_file,
)


# noinspection PyPep8Naming
class ThisTestClass(BasePyfakefsTestClass):

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = customize_env_context()

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_str(Bootstrapper_state_pre_commit_configured._state_name())

    @patch(f"{pre_commit.__name__}.subprocess.check_call")
    @patch(f"{pre_commit.__name__}.subprocess.check_output")
    @patch(f"{primer_kernel.__name__}.os.execve")
    @patch("sys.argv", [""])
    @patch(f"{primer_kernel.__name__}.is_venv", return_value=False)
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_command_executed.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_global_conf_file_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_ref_root_dir_abs_path_inited.__name__}.create_state_node")
    def test_state_evaluation(
        self,
        mock_create_state_ref_root_dir_abs_path_inited,
        mock_create_state_global_conf_file_abs_path_inited,
        mock_create_state_command_executed,
        mock_is_venv,
        mock_execve,
        mock_subprocess_check_output,
        mock_check_call,
    ):
        # given:

        mock_create_state_command_executed.return_value.eval_own_state.return_value = True

        assert_parent_factories_mocked(
            self.env_ctx,
            Bootstrapper_state_pre_commit_configured._state_name(),
        )

        mock_client_conf_path = "/gconf/proto_kernel.json"
        self.fs.create_dir("/gconf")
        write_json_file(mock_client_conf_path, {})
        mock_create_state_global_conf_file_abs_path_inited.return_value.eval_own_state.return_value = mock_client_conf_path
        mock_ref_root_dir = "/test/project"
        mock_create_state_ref_root_dir_abs_path_inited.return_value.eval_own_state.return_value = mock_ref_root_dir

        client_conf_dir_path = "/gconf"
        pre_commit_conf_file_path = os.path.join(
            client_conf_dir_path,
            "pre_commit.yaml",
        )

        # when:
        state_value = self.env_ctx.state_graph.eval_state(
            Bootstrapper_state_pre_commit_configured._state_name(),
            self.env_ctx,
        )

        # then:
        assert state_value == 0

        mock_subprocess_check_output.assert_called_once_with(
            [
                "git",
                "rev-parse",
                "--is-inside-work-tree",
            ],
            cwd=mock_ref_root_dir,
        )

        path_to_pre_commit = os.path.join(
            os.path.dirname(sys.executable),
            "pre-commit",
        )
        mock_check_call.assert_called_once_with(
            [
                path_to_pre_commit,
                "install",
                #
                "--hook-type",
                "pre-commit",
                #
                "--config",
                pre_commit_conf_file_path,
            ]
        )
