import argparse
import os
from unittest.mock import patch

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.mock_verifier import (
    assert_parent_factories_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_args_parsed,
    Bootstrapper_state_input_do_install_var_loaded,
    Bootstrapper_state_local_conf_symlink_abs_path_inited,
    Bootstrapper_state_project_descriptors_inited,
    Bootstrapper_state_install_specs_inited,
    Bootstrapper_state_ref_root_dir_abs_path_inited,
    Bootstrapper_state_stride_py_venv_reached,
    Bootstrapper_state_venv_driver_prepared,
    CommandAction,
    ConfConstClient,
    ConfField,
    EnvContext,
    EnvState,
    EnvVar,
    ParsedArg,
    ExecMode,
    StateStride,
)


# noinspection PyPep8Naming
class ThisTestClass(BasePyfakefsTestClass):

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = EnvContext()

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_str(EnvState.state_protoprimer_package_installed.name)

    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_symlink_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_ref_root_dir_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_stride_py_venv_reached.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_project_descriptors_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_install_specs_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_do_install_var_loaded.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.create_state_node")
    @patch.dict(
        os.environ,
        {EnvVar.var_PROTOPRIMER_PY_EXEC.value: StateStride.stride_py_venv.name},
    )
    @patch(f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_exec_mode_arg_loaded.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_venv_driver_prepared.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{EnvContext.__name__}.{EnvContext.get_stride.__name__}")
    def test_default_install(
        self,
        mock_get_stride,
        mock_state_venv_driver_prepared,
        mock_state_input_exec_mode_arg_loaded,
        mock_state_args_parsed,
        mock_state_input_do_install_var_loaded,
        mock_state_install_specs_inited,
        mock_state_project_descriptors_inited,
        mock_state_stride_py_venv_reached,
        mock_state_ref_root_dir_abs_path_inited,
        mock_state_local_conf_symlink_abs_path_inited,
    ):
        # given:
        assert_parent_factories_mocked(
            self.env_ctx,
            EnvState.state_protoprimer_package_installed.name,
        )
        mock_get_stride.return_value = StateStride.stride_py_venv
        mock_client_ref_root_dir = "/mock_client_ref_root_dir"
        self.fs.create_dir(mock_client_ref_root_dir)
        os.chdir(mock_client_ref_root_dir)
        mock_state_stride_py_venv_reached.return_value.eval_own_state.return_value = StateStride.stride_py_venv
        mock_state_ref_root_dir_abs_path_inited.return_value.eval_own_state.return_value = mock_client_ref_root_dir
        mock_client_conf_env_dir = "/mock_client_conf_env_dir"
        self.fs.create_dir(mock_client_conf_env_dir)
        mock_state_local_conf_symlink_abs_path_inited.return_value.eval_own_state.return_value = mock_client_conf_env_dir
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
                    ConfField.field_build_root_dir_rel_path.value: str(project_rel_path),
                    ConfField.field_install_extras.value: [],
                }
            )
        mock_state_project_descriptors_inited.return_value.eval_own_state.return_value = project_descriptors
        mock_state_install_specs_inited.return_value.eval_own_state.return_value = []
        mock_state_input_do_install_var_loaded.return_value.eval_own_state.return_value = True
        parsed_args = argparse.Namespace(
            **{ParsedArg.name_exec_mode.value: ExecMode.mode_boot.value},
        )
        mock_state_args_parsed.return_value.eval_own_state.return_value = parsed_args
        mock_state_input_exec_mode_arg_loaded.return_value.eval_own_state.return_value = ExecMode.mode_boot
        # when:
        self.env_ctx.state_graph.eval_state(EnvState.state_protoprimer_package_installed.name)
        # then:
        mock_state_venv_driver_prepared.return_value.eval_own_state.return_value.install_dependencies.assert_called()
        mock_state_venv_driver_prepared.return_value.eval_own_state.return_value.install_dependencies.assert_any_call(
            mock_state_ref_root_dir_abs_path_inited.return_value.eval_own_state.return_value,
            primer_kernel.get_path_to_curr_python(),
            os.path.join(
                mock_state_local_conf_symlink_abs_path_inited.return_value.eval_own_state.return_value,
                primer_kernel.ConfConstEnv.constraints_txt_basename,
            ),
            project_descriptors,
            [],
        )

    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_symlink_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_ref_root_dir_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_stride_py_venv_reached.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_project_descriptors_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_install_specs_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_do_install_var_loaded.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.create_state_node")
    @patch.dict(
        os.environ,
        {EnvVar.var_PROTOPRIMER_PY_EXEC.value: StateStride.stride_py_venv.name},
    )
    @patch(f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_exec_mode_arg_loaded.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_venv_driver_prepared.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{EnvContext.__name__}.{EnvContext.get_stride.__name__}")
    def test_reboot(
        self,
        mock_get_stride,
        mock_state_venv_driver_prepared,
        mock_state_input_exec_mode_arg_loaded,
        mock_state_args_parsed,
        mock_state_input_do_install_var_loaded,
        mock_state_install_specs_inited,
        mock_state_project_descriptors_inited,
        mock_state_stride_py_venv_reached,
        mock_state_ref_root_dir_abs_path_inited,
        mock_state_local_conf_symlink_abs_path_inited,
    ):
        # given:
        assert_parent_factories_mocked(
            self.env_ctx,
            EnvState.state_protoprimer_package_installed.name,
        )
        mock_get_stride.return_value = StateStride.stride_py_venv
        mock_client_ref_root_dir = "/mock_client_ref_root_dir"
        self.fs.create_dir(mock_client_ref_root_dir)
        os.chdir(mock_client_ref_root_dir)
        mock_state_stride_py_venv_reached.return_value.eval_own_state.return_value = StateStride.stride_py_venv
        mock_state_ref_root_dir_abs_path_inited.return_value.eval_own_state.return_value = mock_client_ref_root_dir
        mock_client_conf_env_dir = "/mock_client_conf_env_dir"
        self.fs.create_dir(mock_client_conf_env_dir)
        mock_state_local_conf_symlink_abs_path_inited.return_value.eval_own_state.return_value = mock_client_conf_env_dir
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
                    ConfField.field_build_root_dir_rel_path.value: str(project_rel_path),
                    ConfField.field_install_extras.value: [],
                }
            )
        mock_state_project_descriptors_inited.return_value.eval_own_state.return_value = project_descriptors
        mock_state_install_specs_inited.return_value.eval_own_state.return_value = []
        mock_state_input_do_install_var_loaded.return_value.eval_own_state.return_value = True
        parsed_args = argparse.Namespace(
            **{ParsedArg.name_exec_mode.value: ExecMode.mode_reboot.value},
        )
        mock_state_args_parsed.return_value.eval_own_state.return_value = parsed_args
        mock_state_input_exec_mode_arg_loaded.return_value.eval_own_state.return_value = ExecMode.mode_reboot
        # when:
        self.env_ctx.state_graph.eval_state(EnvState.state_protoprimer_package_installed.name)
        # then:
        mock_state_venv_driver_prepared.return_value.eval_own_state.return_value.install_dependencies.assert_called()
        mock_state_venv_driver_prepared.return_value.eval_own_state.return_value.install_dependencies.assert_any_call(
            mock_state_ref_root_dir_abs_path_inited.return_value.eval_own_state.return_value,
            primer_kernel.get_path_to_curr_python(),
            os.path.join(
                mock_state_local_conf_symlink_abs_path_inited.return_value.eval_own_state.return_value,
                primer_kernel.ConfConstEnv.constraints_txt_basename,
            ),
            project_descriptors,
            [],
        )

    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_symlink_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_ref_root_dir_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_stride_py_venv_reached.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_project_descriptors_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_install_specs_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_do_install_var_loaded.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.create_state_node")
    @patch.dict(
        os.environ,
        {EnvVar.var_PROTOPRIMER_PY_EXEC.value: StateStride.stride_py_venv.name},
    )
    @patch(f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_exec_mode_arg_loaded.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_venv_driver_prepared.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{EnvContext.__name__}.{EnvContext.get_stride.__name__}")
    def test_no_install_triggered(
        self,
        mock_get_stride,
        mock_state_venv_driver_prepared,
        mock_state_input_exec_mode_arg_loaded,
        mock_state_args_parsed,
        mock_state_input_do_install_var_loaded,
        mock_state_install_specs_inited,
        mock_state_project_descriptors_inited,
        mock_state_stride_py_venv_reached,
        mock_state_ref_root_dir_abs_path_inited,
        mock_state_local_conf_symlink_abs_path_inited,
    ):
        # given:
        assert_parent_factories_mocked(
            self.env_ctx,
            EnvState.state_protoprimer_package_installed.name,
        )
        mock_get_stride.return_value = StateStride.stride_py_venv
        mock_client_ref_root_dir = "/mock_client_ref_root_dir"
        self.fs.create_dir(mock_client_ref_root_dir)
        os.chdir(mock_client_ref_root_dir)
        mock_state_stride_py_venv_reached.return_value.eval_own_state.return_value = StateStride.stride_py_venv
        mock_state_ref_root_dir_abs_path_inited.return_value.eval_own_state.return_value = mock_client_ref_root_dir
        mock_client_conf_env_dir = "/mock_client_conf_env_dir"
        self.fs.create_dir(mock_client_conf_env_dir)
        mock_state_local_conf_symlink_abs_path_inited.return_value.eval_own_state.return_value = mock_client_conf_env_dir
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
                    ConfField.field_build_root_dir_rel_path.value: str(project_rel_path),
                    ConfField.field_install_extras.value: [],
                }
            )
        mock_state_project_descriptors_inited.return_value.eval_own_state.return_value = project_descriptors
        mock_state_install_specs_inited.return_value.eval_own_state.return_value = []
        mock_state_input_do_install_var_loaded.return_value.eval_own_state.return_value = False
        parsed_args = argparse.Namespace(
            **{ParsedArg.name_exec_mode.value: ExecMode.mode_boot.value},
        )
        mock_state_args_parsed.return_value.eval_own_state.return_value = parsed_args
        mock_state_input_exec_mode_arg_loaded.return_value.eval_own_state.return_value = ExecMode.mode_boot
        # when:
        self.env_ctx.state_graph.eval_state(EnvState.state_protoprimer_package_installed.name)
        # then:
        mock_state_venv_driver_prepared.return_value.eval_own_state.return_value.install_dependencies.assert_not_called()

    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_symlink_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_ref_root_dir_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_stride_py_venv_reached.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_project_descriptors_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_install_specs_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_do_install_var_loaded.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.create_state_node")
    @patch.dict(
        os.environ,
        {EnvVar.var_PROTOPRIMER_PY_EXEC.value: StateStride.stride_py_venv.name},
    )
    @patch(f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_exec_mode_arg_loaded.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_venv_driver_prepared.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{EnvContext.__name__}.{EnvContext.get_stride.__name__}")
    def test_grouped_install(
        self,
        mock_get_stride,
        mock_state_venv_driver_prepared,
        mock_state_input_exec_mode_arg_loaded,
        mock_state_args_parsed,
        mock_state_input_do_install_var_loaded,
        mock_state_install_specs_inited,
        mock_state_project_descriptors_inited,
        mock_state_stride_py_venv_reached,
        mock_state_ref_root_dir_abs_path_inited,
        mock_state_local_conf_symlink_abs_path_inited,
    ):
        # given:
        assert_parent_factories_mocked(
            self.env_ctx,
            EnvState.state_protoprimer_package_installed.name,
        )
        mock_get_stride.return_value = StateStride.stride_py_venv
        mock_client_ref_root_dir = "/mock_client_ref_root_dir"
        self.fs.create_dir(mock_client_ref_root_dir)
        os.chdir(mock_client_ref_root_dir)
        mock_state_stride_py_venv_reached.return_value.eval_own_state.return_value = StateStride.stride_py_venv
        mock_state_ref_root_dir_abs_path_inited.return_value.eval_own_state.return_value = mock_client_ref_root_dir
        mock_client_conf_env_dir = "/mock_client_conf_env_dir"
        self.fs.create_dir(mock_client_conf_env_dir)
        mock_state_local_conf_symlink_abs_path_inited.return_value.eval_own_state.return_value = mock_client_conf_env_dir

        project_descriptors = [
            {
                ConfField.field_build_root_dir_rel_path.value: "proj1",
                ConfField.field_install_group.value: "group2",
            },
            {
                ConfField.field_build_root_dir_rel_path.value: "proj2",
                ConfField.field_install_group.value: "group1",
            },
            {
                ConfField.field_build_root_dir_rel_path.value: "proj3",
                # missing group -> None
            },
        ]
        mock_state_project_descriptors_inited.return_value.eval_own_state.return_value = project_descriptors
        mock_state_install_specs_inited.return_value.eval_own_state.return_value = [
            {"group1": {ConfField.field_extra_command_args.value: ["--group_1-arg"]}},
            {"group2": {}},
        ]
        mock_state_input_do_install_var_loaded.return_value.eval_own_state.return_value = True
        mock_state_args_parsed.return_value.eval_own_state.return_value = argparse.Namespace(exec_mode=ExecMode.mode_boot.value)
        mock_state_input_exec_mode_arg_loaded.return_value.eval_own_state.return_value = ExecMode.mode_boot

        # when:
        self.env_ctx.state_graph.eval_state(EnvState.state_protoprimer_package_installed.name)

        # then:
        from unittest.mock import call

        constraints_txt_path = os.path.join(
            mock_client_conf_env_dir,
            primer_kernel.ConfConstEnv.constraints_txt_basename,
        )
        mock_state_venv_driver_prepared.return_value.eval_own_state.return_value.install_dependencies.assert_has_calls(
            [
                call(
                    mock_client_ref_root_dir,
                    primer_kernel.get_path_to_curr_python(),
                    constraints_txt_path,
                    [project_descriptors[1]],
                    ["--group_1-arg"],
                ),
                call(
                    mock_client_ref_root_dir,
                    primer_kernel.get_path_to_curr_python(),
                    constraints_txt_path,
                    [project_descriptors[0]],
                    [],
                ),
                call(
                    mock_client_ref_root_dir,
                    primer_kernel.get_path_to_curr_python(),
                    constraints_txt_path,
                    [project_descriptors[2]],
                    [],
                ),
            ],
            any_order=False,
        )

    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_symlink_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_ref_root_dir_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_stride_py_venv_reached.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_project_descriptors_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_install_specs_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_do_install_var_loaded.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.create_state_node")
    @patch.dict(
        os.environ,
        {EnvVar.var_PROTOPRIMER_PY_EXEC.value: StateStride.stride_py_venv.name},
    )
    @patch(f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_exec_mode_arg_loaded.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_venv_driver_prepared.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{EnvContext.__name__}.{EnvContext.get_stride.__name__}")
    def test_nothing_to_install(
        self,
        mock_get_stride,
        mock_state_venv_driver_prepared,
        mock_state_input_exec_mode_arg_loaded,
        mock_state_args_parsed,
        mock_state_input_do_install_var_loaded,
        mock_state_install_specs_inited,
        mock_state_project_descriptors_inited,
        mock_state_stride_py_venv_reached,
        mock_state_ref_root_dir_abs_path_inited,
        mock_state_local_conf_symlink_abs_path_inited,
    ):

        # given:

        assert_parent_factories_mocked(
            self.env_ctx,
            EnvState.state_protoprimer_package_installed.name,
        )
        mock_get_stride.return_value = StateStride.stride_py_venv
        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        mock_state_stride_py_venv_reached.return_value.eval_own_state.return_value = StateStride.stride_py_venv

        mock_state_ref_root_dir_abs_path_inited.return_value.eval_own_state.return_value = mock_client_dir

        mock_client_conf_env_dir = "/mock_client_conf_env_dir"
        self.fs.create_dir(mock_client_conf_env_dir)
        mock_state_local_conf_symlink_abs_path_inited.return_value.eval_own_state.return_value = mock_client_conf_env_dir

        project_descriptors: list[dict] = []

        mock_state_project_descriptors_inited.return_value.eval_own_state.return_value = project_descriptors
        mock_state_install_specs_inited.return_value.eval_own_state.return_value = []

        mock_state_input_do_install_var_loaded.return_value.eval_own_state.return_value = True

        parsed_args = argparse.Namespace(
            **{ParsedArg.name_exec_mode.value: ExecMode.mode_boot.value},
        )
        mock_state_args_parsed.return_value.eval_own_state.return_value = parsed_args
        mock_state_input_exec_mode_arg_loaded.return_value.eval_own_state.return_value = ExecMode.mode_boot

        # when:

        self.env_ctx.state_graph.eval_state(EnvState.state_protoprimer_package_installed.name)

        # then:

        mock_state_venv_driver_prepared.return_value.eval_own_state.return_value.install_dependencies.assert_not_called()
