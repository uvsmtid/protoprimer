import argparse
import os
from unittest.mock import patch

from local_test.name_assertion import assert_test_module_name_embeds_str
from local_test.base_test_class import BasePyfakefsTestClass
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    ArgConst,
    Bootstrapper_state_args_parsed,
    Bootstrapper_state_client_ref_dir_abs_path_global,
    Bootstrapper_state_project_path_list_finalized,
    Bootstrapper_state_py_exec_selected,
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
            EnvState.state_protoprimer_package_installed.name
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_ref_dir_abs_path_global.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_selected.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_project_path_list_finalized.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.install_editable_project",
    )
    def test_state_protoprimer_package_installed(
        self,
        mock_install_editable_project,
        mock_state_project_path_list_finalized,
        mock_state_py_exec_selected,
        mock_state_client_ref_dir_abs_path_global,
    ):

        # given:

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        mock_state_py_exec_selected.return_value = PythonExecutable.py_exec_venv

        mock_state_client_ref_dir_abs_path_global.return_value = mock_client_dir

        project_rel_path_list = []
        project_abs_path_list = []
        for project_name in [
            "local_repo",
            "local_test",
            "neoprimer",
            "protoprimer",
        ]:
            project_rel_path = os.path.join(
                "src",
                project_name,
            )
            project_abs_path = os.path.join(
                mock_client_dir,
                project_rel_path,
            )
            project_toml = os.path.join(
                project_abs_path,
                "pyproject.toml",
            )

            self.fs.create_file(project_toml)
            project_rel_path_list.append(project_rel_path)
            project_abs_path_list.append(project_abs_path)

        mock_state_project_path_list_finalized.return_value = project_rel_path_list

        # when:

        self.env_ctx.bootstrap_state(EnvState.state_protoprimer_package_installed.name)

        # then:

        mock_install_editable_project.assert_called_once_with(project_abs_path_list)

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_ref_dir_abs_path_global.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_selected.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_project_path_list_finalized.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.install_editable_project",
    )
    def test_nothing_to_install(
        self,
        mock_install_editable_project,
        mock_state_project_path_list_finalized,
        mock_state_py_exec_selected,
        mock_state_client_ref_dir_abs_path_global,
    ):

        # given:

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        mock_state_py_exec_selected.return_value = PythonExecutable.py_exec_venv

        mock_state_client_ref_dir_abs_path_global.return_value = mock_client_dir

        project_path_list = []

        mock_state_project_path_list_finalized.return_value = project_path_list

        # when:

        self.env_ctx.bootstrap_state(EnvState.state_protoprimer_package_installed.name)

        # then:

        mock_install_editable_project.assert_not_called()
