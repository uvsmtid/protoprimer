import os
from unittest.mock import patch

from local_repo.cmd_venv_shell import customize_env_context
from local_test.base_test_class import BasePyfakefsTestClass
from local_test.name_assertion import assert_test_module_name_embeds_str
from neoprimer import venv_shell
from neoprimer.venv_shell import Bootstrapper_state_activated_venv_shell_started
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_env_local_venv_dir_abs_path_eval_finalized,
    Bootstrapper_state_py_exec_updated_proto_code,
    ConfConstGeneral,
    PythonExecutable,
)


# noinspection PyPep8Naming
class ThisTestClass(BasePyfakefsTestClass):

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = customize_env_context()

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_str(
            Bootstrapper_state_activated_venv_shell_started.state_activated_venv_shell_started
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_env_local_venv_dir_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_updated_proto_code.__name__}.eval_own_state"
    )
    @patch(f"{venv_shell.__name__}.create_temp_file")
    @patch(f"{primer_kernel.__name__}.os.execv")
    def test_state_primer_conf_client_file_abs_path_eval_finalized_exists(
        self,
        mock_execv,
        mock_create_temp_file,
        mock_state_py_exec_updated_proto_code,
        mock_state_env_local_venv_dir_abs_path_eval_finalized,
    ):

        # given:

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        temp_file_path = os.path.join(
            mock_client_dir,
            "temp_file",
        )
        temp_file_fake = self.fs.create_file(temp_file_path)
        mock_create_temp_file.return_value = open(temp_file_fake.path, "w")

        mock_state_py_exec_updated_proto_code.return_value = (
            PythonExecutable.py_exec_updated_protoprimer_package
        )

        mock_state_env_local_venv_dir_abs_path_eval_finalized.return_value = (
            mock_client_dir
        )
        expected_venv_activate_path = os.path.join(
            mock_state_env_local_venv_dir_abs_path_eval_finalized.return_value,
            ConfConstGeneral.file_rel_path_venv_activate,
        )

        # when:

        self.env_ctx.state_graph.eval_state(
            Bootstrapper_state_activated_venv_shell_started.state_activated_venv_shell_started
        )

        # then:

        mock_execv.assert_called_once_with(
            "/usr/bin/bash",
            [
                "bash",
                "--init-file",
                temp_file_path,
            ],
        )
        self.assertEqual(
            f"source ~/.bashrc && source {expected_venv_activate_path}",
            temp_file_fake.contents,
        )
