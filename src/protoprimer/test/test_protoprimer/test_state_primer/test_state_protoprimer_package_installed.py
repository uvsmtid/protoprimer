import os
from unittest.mock import patch

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_env_project_descriptors_eval_finalized,
    Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized,
    Bootstrapper_state_py_exec_selected,
    ConfField,
    EnvContext,
    EnvState,
    PythonExecutable,
)
from test_protoprimer.misc_tools.mock_verifier import assert_parent_states_mocked


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
        f"{primer_kernel.__name__}.{Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized.__name__}._eval_state_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_selected.__name__}._eval_state_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_env_project_descriptors_eval_finalized.__name__}._eval_state_once"
    )
    @patch(
        f"{primer_kernel.__name__}.install_editable_project",
    )
    def test_state_protoprimer_package_installed(
        self,
        mock_install_editable_project,
        mock_state_env_project_rel_path_to_extras_list_finalized_lconf,
        mock_state_py_exec_selected,
        mock_state_primer_ref_root_dir_abs_path_eval_finalized,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_protoprimer_package_installed,
        )

        mock_client_ref_root_dir = "/mock_client_ref_root_dir"
        self.fs.create_dir(mock_client_ref_root_dir)
        os.chdir(mock_client_ref_root_dir)

        mock_state_py_exec_selected.return_value = PythonExecutable.py_exec_venv

        mock_state_primer_ref_root_dir_abs_path_eval_finalized.return_value = (
            mock_client_ref_root_dir
        )

        project_descriptors: list[dict] = []
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
                mock_client_ref_root_dir,
                project_rel_path,
            )
            project_toml = os.path.join(
                project_abs_path,
                "pyproject.toml",
            )

            self.fs.create_file(project_toml)
            project_descriptors.append(
                {
                    ConfField.field_env_build_root_dir_rel_path.value: project_rel_path,
                    ConfField.field_env_install_extras.value: [],
                }
            )

        mock_state_env_project_rel_path_to_extras_list_finalized_lconf.return_value = (
            project_descriptors
        )

        # when:

        self.env_ctx.state_graph.eval_state(
            EnvState.state_protoprimer_package_installed.name
        )

        # then:

        mock_install_editable_project.assert_called_once_with(
            mock_client_ref_root_dir,
            project_descriptors,
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized.__name__}._eval_state_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_selected.__name__}._eval_state_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_env_project_descriptors_eval_finalized.__name__}._eval_state_once"
    )
    @patch(
        f"{primer_kernel.__name__}.install_editable_project",
    )
    def test_nothing_to_install(
        self,
        mock_install_editable_project,
        mock_state_env_project_rel_path_to_extras_list_finalized_lconf,
        mock_state_py_exec_selected,
        mock_state_primer_ref_root_dir_abs_path_eval_finalized,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_protoprimer_package_installed,
        )

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        mock_state_py_exec_selected.return_value = PythonExecutable.py_exec_venv

        mock_state_primer_ref_root_dir_abs_path_eval_finalized.return_value = (
            mock_client_dir
        )

        project_rel_path_to_extras_list = []

        mock_state_env_project_rel_path_to_extras_list_finalized_lconf.return_value = (
            project_rel_path_to_extras_list
        )

        # when:

        self.env_ctx.state_graph.eval_state(
            EnvState.state_protoprimer_package_installed.name
        )

        # then:

        mock_install_editable_project.assert_not_called()
