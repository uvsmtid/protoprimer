from unittest.mock import patch

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.mock_verifier import (
    assert_parent_states_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from neoprimer import pre_commit
from neoprimer.cmd_install_pre_commit import customize_env_context
from neoprimer.pre_commit import (
    Bootstrapper_state_pre_commit_installed,
)
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_command_executed,
)


# noinspection PyPep8Naming
class ThisTestClass(BasePyfakefsTestClass):

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = customize_env_context()

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_str(
            Bootstrapper_state_pre_commit_installed.state_pre_commit_installed
        )

    @patch(f"{pre_commit.__name__}.install_package")
    @patch(f"{primer_kernel.__name__}.os.execve")
    @patch("sys.argv", [""])
    @patch(f"{primer_kernel.__name__}.is_venv", return_value=False)
    @patch(f"{primer_kernel.__name__}.warn_if_non_venv_package_installed")
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_command_executed.__name__}.eval_own_state",
        return_value=True,
    )
    def test_state_evaluation(
        self,
        mock_parent_state,
        mock_warn_if_non_venv_package_installed,
        mock_is_venv,
        mock_execve,
        mock_install_package,
    ):
        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            Bootstrapper_state_pre_commit_installed.state_pre_commit_installed,
        )

        # when:
        state_value = self.env_ctx.state_graph.eval_state(
            Bootstrapper_state_pre_commit_installed.state_pre_commit_installed
        )

        # then:
        self.assertTrue(state_value)
        mock_install_package.assert_called_once_with("pre-commit")
