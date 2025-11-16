import argparse
import os
from unittest.mock import patch

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.mock_verifier import (
    assert_parent_states_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_args_parsed,
    Bootstrapper_state_client_conf_env_dir_abs_path_eval_finalized,
    Bootstrapper_state_merged_project_descriptors_eval_finalized,
    Bootstrapper_state_input_do_install_var_loaded,
    Bootstrapper_state_package_driver_inited,
    Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized,
    Bootstrapper_state_py_exec_venv_reached,
    ConfConstClient,
    ConfField,
    EnvContext,
    EnvState,
    ParsedArg,
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
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_env_dir_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_venv_reached.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_merged_project_descriptors_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_do_install_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_package_driver_inited.__name__}.eval_own_state"
    )
    def test_default_install(
        self,
        mock_state_package_driver_inited,
        mock_state_args_parsed,
        mock_state_input_do_install_var_loaded,
        mock_state_env_project_rel_path_to_extras_list_finalized_lconf,
        mock_state_py_exec_venv_reached,
        mock_state_primer_ref_root_dir_abs_path_eval_finalized,
        mock_state_client_conf_env_dir_abs_path_eval_finalized,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_protoprimer_package_installed.name,
        )
        self.fs.reset()
        self.env_ctx = EnvContext()
        mock_client_ref_root_dir = "/mock_client_ref_root_dir"
        self.fs.create_dir(mock_client_ref_root_dir)
        os.chdir(mock_client_ref_root_dir)
        mock_state_py_exec_venv_reached.return_value = PythonExecutable.py_exec_venv
        mock_state_primer_ref_root_dir_abs_path_eval_finalized.return_value = (
            mock_client_ref_root_dir
        )
        mock_client_conf_env_dir = "/mock_client_conf_env_dir"
        self.fs.create_dir(mock_client_conf_env_dir)
        mock_state_client_conf_env_dir_abs_path_eval_finalized.return_value = (
            mock_client_conf_env_dir
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
                ConfConstClient.default_pyproject_toml_basename,
            )
            self.fs.create_file(project_toml)
            project_descriptors.append(
                {
                    ConfField.field_env_build_root_dir_rel_path.value: str(
                        project_rel_path
                    ),
                    ConfField.field_env_install_extras.value: [],
                }
            )
        mock_state_env_project_rel_path_to_extras_list_finalized_lconf.return_value = (
            project_descriptors
        )
        mock_state_input_do_install_var_loaded.return_value = True
        parsed_args = argparse.Namespace(
            **{ParsedArg.name_reinstall.value: False},
        )
        mock_state_args_parsed.return_value = parsed_args
        # when:
        self.env_ctx.state_graph.eval_state(
            EnvState.state_protoprimer_package_installed.name
        )
        # then:
        mock_state_package_driver_inited.return_value.install_dependencies.assert_called_once()

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_env_dir_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_venv_reached.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_merged_project_descriptors_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_do_install_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_package_driver_inited.__name__}.eval_own_state"
    )
    def test_reinstall(
        self,
        mock_state_package_driver_inited,
        mock_state_args_parsed,
        mock_state_input_do_install_var_loaded,
        mock_state_env_project_rel_path_to_extras_list_finalized_lconf,
        mock_state_py_exec_venv_reached,
        mock_state_primer_ref_root_dir_abs_path_eval_finalized,
        mock_state_client_conf_env_dir_abs_path_eval_finalized,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_protoprimer_package_installed.name,
        )
        self.fs.reset()
        self.env_ctx = EnvContext()
        mock_client_ref_root_dir = "/mock_client_ref_root_dir"
        self.fs.create_dir(mock_client_ref_root_dir)
        os.chdir(mock_client_ref_root_dir)
        mock_state_py_exec_venv_reached.return_value = PythonExecutable.py_exec_venv
        mock_state_primer_ref_root_dir_abs_path_eval_finalized.return_value = (
            mock_client_ref_root_dir
        )
        mock_client_conf_env_dir = "/mock_client_conf_env_dir"
        self.fs.create_dir(mock_client_conf_env_dir)
        mock_state_client_conf_env_dir_abs_path_eval_finalized.return_value = (
            mock_client_conf_env_dir
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
                ConfConstClient.default_pyproject_toml_basename,
            )
            self.fs.create_file(project_toml)
            project_descriptors.append(
                {
                    ConfField.field_env_build_root_dir_rel_path.value: str(
                        project_rel_path
                    ),
                    ConfField.field_env_install_extras.value: [],
                }
            )
        mock_state_env_project_rel_path_to_extras_list_finalized_lconf.return_value = (
            project_descriptors
        )
        mock_state_input_do_install_var_loaded.return_value = True
        parsed_args = argparse.Namespace(
            **{ParsedArg.name_reinstall.value: True},
        )
        mock_state_args_parsed.return_value = parsed_args
        # when:
        self.env_ctx.state_graph.eval_state(
            EnvState.state_protoprimer_package_installed.name
        )
        # then:
        mock_state_package_driver_inited.return_value.install_dependencies.assert_called_once()

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_env_dir_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_venv_reached.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_merged_project_descriptors_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_do_install_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_package_driver_inited.__name__}.eval_own_state"
    )
    def test_no_install_triggered(
        self,
        mock_state_package_driver_inited,
        mock_state_args_parsed,
        mock_state_input_do_install_var_loaded,
        mock_state_env_project_rel_path_to_extras_list_finalized_lconf,
        mock_state_py_exec_venv_reached,
        mock_state_primer_ref_root_dir_abs_path_eval_finalized,
        mock_state_client_conf_env_dir_abs_path_eval_finalized,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_protoprimer_package_installed.name,
        )
        self.fs.reset()
        self.env_ctx = EnvContext()
        mock_client_ref_root_dir = "/mock_client_ref_root_dir"
        self.fs.create_dir(mock_client_ref_root_dir)
        os.chdir(mock_client_ref_root_dir)
        mock_state_py_exec_venv_reached.return_value = PythonExecutable.py_exec_venv
        mock_state_primer_ref_root_dir_abs_path_eval_finalized.return_value = (
            mock_client_ref_root_dir
        )
        mock_client_conf_env_dir = "/mock_client_conf_env_dir"
        self.fs.create_dir(mock_client_conf_env_dir)
        mock_state_client_conf_env_dir_abs_path_eval_finalized.return_value = (
            mock_client_conf_env_dir
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
                ConfConstClient.default_pyproject_toml_basename,
            )
            self.fs.create_file(project_toml)
            project_descriptors.append(
                {
                    ConfField.field_env_build_root_dir_rel_path.value: str(
                        project_rel_path
                    ),
                    ConfField.field_env_install_extras.value: [],
                }
            )
        mock_state_env_project_rel_path_to_extras_list_finalized_lconf.return_value = (
            project_descriptors
        )
        mock_state_input_do_install_var_loaded.return_value = False
        parsed_args = argparse.Namespace(
            **{ParsedArg.name_reinstall.value: False},
        )
        mock_state_args_parsed.return_value = parsed_args
        # when:
        self.env_ctx.state_graph.eval_state(
            EnvState.state_protoprimer_package_installed.name
        )
        # then:
        mock_state_package_driver_inited.return_value.install_dependencies.assert_not_called()

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_env_dir_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_venv_reached.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_merged_project_descriptors_eval_finalized.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_do_install_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_package_driver_inited.__name__}.eval_own_state"
    )
    def test_nothing_to_install(
        self,
        mock_state_package_driver_inited,
        mock_state_args_parsed,
        mock_state_input_do_install_var_loaded,
        mock_state_env_project_rel_path_to_extras_list_finalized_lconf,
        mock_state_py_exec_venv_reached,
        mock_state_primer_ref_root_dir_abs_path_eval_finalized,
        mock_state_client_conf_env_dir_abs_path_eval_finalized,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_protoprimer_package_installed.name,
        )

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        mock_state_py_exec_venv_reached.return_value = PythonExecutable.py_exec_venv

        mock_state_primer_ref_root_dir_abs_path_eval_finalized.return_value = (
            mock_client_dir
        )

        mock_client_conf_env_dir = "/mock_client_conf_env_dir"
        self.fs.create_dir(mock_client_conf_env_dir)
        mock_state_client_conf_env_dir_abs_path_eval_finalized.return_value = (
            mock_client_conf_env_dir
        )

        project_rel_path_to_extras_list = []

        mock_state_env_project_rel_path_to_extras_list_finalized_lconf.return_value = (
            project_rel_path_to_extras_list
        )

        mock_state_input_do_install_var_loaded.return_value = True

        parsed_args = argparse.Namespace(
            **{ParsedArg.name_reinstall.value: False},
        )
        mock_state_args_parsed.return_value = parsed_args

        # when:

        self.env_ctx.state_graph.eval_state(
            EnvState.state_protoprimer_package_installed.name
        )

        # then:

        mock_state_package_driver_inited.return_value.install_dependencies.assert_not_called()
