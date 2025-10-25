import os
import sys
from unittest.mock import patch

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.mock_verifier import (
    assert_parent_states_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from neoprimer import pre_commit
from neoprimer.cmd_install_pre_commit import customize_env_context
from neoprimer.pre_commit import (
    Bootstrapper_state_pre_commit_configured,
)
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_command_executed,
    Bootstrapper_state_primer_conf_client_file_abs_path_eval_finalized,
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
            Bootstrapper_state_pre_commit_configured.state_pre_commit_configured
        )

    @patch(f"{pre_commit.__name__}.subprocess.check_call")
    @patch(f"{primer_kernel.__name__}.os.execve")
    @patch("sys.argv", [""])
    @patch(f"{primer_kernel.__name__}.is_venv", return_value=False)
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_command_executed.__name__}.eval_own_state",
        return_value=True,
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_primer_conf_client_file_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    def test_state_evaluation(
        self,
        mock_state_primer_conf_client_file_abs_path_eval_finalized,
        mock_command_executed_eval_own_state,
        mock_is_venv,
        mock_execve,
        mock_check_call,
    ):
        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            Bootstrapper_state_pre_commit_configured.state_pre_commit_configured,
        )

        mock_client_conf_path = "/gconf/proto_kernel.conf_client.json"
        self.fs.create_dir("/gconf")
        write_json_file(mock_client_conf_path, {})
        mock_state_primer_conf_client_file_abs_path_eval_finalized.return_value = (
            mock_client_conf_path
        )

        client_conf_dir_path = "/gconf"
        pre_commit_conf_file_path = os.path.join(
            client_conf_dir_path,
            "pre_commit.yaml",
        )

        # when:
        state_value = self.env_ctx.state_graph.eval_state(
            Bootstrapper_state_pre_commit_configured.state_pre_commit_configured
        )

        # then:
        assert state_value == 0

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
