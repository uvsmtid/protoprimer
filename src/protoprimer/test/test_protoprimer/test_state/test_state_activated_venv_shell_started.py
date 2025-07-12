import os
from unittest.mock import patch

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_env_path_to_venv,
    Bootstrapper_state_py_exec_updated_proto_kernel_code,
    ConfConstGeneral,
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
            EnvState.state_activated_venv_shell_started.name
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_env_path_to_venv.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_updated_proto_kernel_code.__name__}._bootstrap_once"
    )
    @patch(f"{primer_kernel.__name__}.create_temp_file")
    @patch(f"{primer_kernel.__name__}.os.execv")
    def test_state_client_conf_file_path_exists(
        self,
        mock_execv,
        mock_create_temp_file,
        mock_state_py_exec_updated_proto_kernel_code,
        mock_state_env_path_to_venv,
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

        mock_state_py_exec_updated_proto_kernel_code.return_value = (
            PythonExecutable.py_exec_updated_protoprimer_package
        )

        mock_state_env_path_to_venv.return_value = mock_client_dir
        expected_venv_activate_path = os.path.join(
            mock_state_env_path_to_venv.return_value,
            ConfConstGeneral.file_rel_path_venv_activate,
        )

        # when:

        self.env_ctx.bootstrap_state(EnvState.state_activated_venv_shell_started.name)

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
