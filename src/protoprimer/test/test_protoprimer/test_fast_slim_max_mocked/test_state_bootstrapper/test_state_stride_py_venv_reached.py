import argparse
import os
import sys
from unittest.mock import patch

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.integrated_helper import (
    test_python_abs_path,
    test_python_version,
)
from local_test.mock_verifier import (
    assert_parent_factories_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_args_parsed,
    Bootstrapper_state_input_start_id_var_loaded,
    Bootstrapper_state_local_conf_file_abs_path_inited,
    Bootstrapper_state_local_venv_dir_abs_path_inited,
    Bootstrapper_state_proto_code_file_abs_path_inited,
    Bootstrapper_state_reboot_triggered,
    Bootstrapper_state_selected_python_file_abs_path_inited,
    Bootstrapper_state_venv_driver_prepared,
    ConfConstEnv,
    ConfConstGeneral,
    EnvContext,
    EnvState,
    EnvVar,
    StateStride,
)

mock_client_dir = "/mock_client_dir"
state_proto_code_file_abs_path_inited = os.path.join(
    mock_client_dir,
    ConfConstGeneral.default_proto_code_basename,
)
target_dst_dir_path = "target_dst_dir"

non_default_file_abs_path_python = "/oct/bin/python3"
non_default_dir_abs_path_venv = "/another/venv"


# noinspection PyPep8Naming
class ThisTestClass(BasePyfakefsTestClass):

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = EnvContext()

        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        self.fs.create_file(state_proto_code_file_abs_path_inited)
        self.fs.create_file(test_python_abs_path)
        self.fs.create_file(non_default_file_abs_path_python)

        self.fs.create_dir(target_dst_dir_path)

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_str(EnvState.state_stride_py_venv_reached.name)

    def test_assumptions_used_in_other_tests(self):
        self.assertNotEqual(
            non_default_file_abs_path_python,
            test_python_abs_path,
        )

    ####################################################################################################################
    @patch.dict(f"{os.__name__}.environ", {}, clear=True)
    @patch.object(sys, "argv", ["/path/to/script.py", "--some-arg"])
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_reboot_triggered.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_file_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_file_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_selected_python_file_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_venv_driver_prepared.__name__}.create_state_node")
    @patch(
        f"{primer_kernel.__name__}.get_path_to_curr_python",
        return_value=test_python_abs_path,
    )
    @patch(f"{primer_kernel.__name__}.os.execve")
    @patch(f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_exec_mode_arg_loaded.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.is_same_file", return_value=True)
    def test_success_on_path_to_curr_python_is_outside_of_path_to_venv_when_venv_is_created(
        self,
        mock_state_input_exec_mode_arg_loaded,
        mock_is_same_file,
        mock_execve,
        mock_get_path_to_curr_python,
        mock_state_venv_driver_prepared,
        mock_state_selected_python_file_abs_path_inited,
        mock_state_local_venv_dir_abs_path_inited,
        mock_state_local_conf_file_abs_path_inited,
        mock_state_proto_code_file_abs_path_inited,
        mock_state_args_parsed,
        mock_state_reboot_triggered,
        mock_state_input_start_id_var_loaded,
    ):

        # given:

        assert_parent_factories_mocked(
            self.env_ctx,
            EnvState.state_stride_py_venv_reached.name,
        )

        mock_state_args_parsed.return_value.eval_own_state.return_value = argparse.Namespace()
        mock_state_input_start_id_var_loaded.return_value.eval_own_state.return_value = "mock_start_id"
        mock_state_reboot_triggered.return_value.eval_own_state.return_value = False
        mock_state_proto_code_file_abs_path_inited.return_value.eval_own_state.return_value = state_proto_code_file_abs_path_inited
        mock_state_selected_python_file_abs_path_inited.return_value.eval_own_state.return_value = test_python_abs_path
        mock_state_local_venv_dir_abs_path_inited.return_value.eval_own_state.return_value = os.path.join(mock_client_dir, ConfConstEnv.default_dir_rel_path_venv)
        mock_state_local_conf_file_abs_path_inited.return_value.eval_own_state.return_value = "fake: " + EnvState.state_local_conf_file_abs_path_inited.name

        # when:

        self.env_ctx.state_graph.eval_state(EnvState.state_stride_py_venv_reached.name, self.env_ctx)

        # then:

        mock_state_venv_driver_prepared.return_value.eval_own_state.return_value.create_venv.assert_called_once_with(
            os.path.join(
                mock_client_dir,
                ConfConstEnv.default_dir_rel_path_venv,
            )
        )
        path_to_required_python = os.path.join(
            mock_client_dir,
            ConfConstEnv.default_dir_rel_path_venv,
            ConfConstGeneral.file_rel_path_venv_python,
        )
        expected_argv = [
            path_to_required_python,
            "-I",
            "/path/to/script.py",
            "--some-arg",
        ]
        mock_execve.assert_called_once_with(
            path=path_to_required_python,
            argv=expected_argv,
            env={
                EnvVar.var_PROTOPRIMER_PY_EXEC.value: StateStride.stride_py_venv.name,
                EnvVar.var_PROTOPRIMER_START_ID.value: "mock_start_id",
                EnvVar.var_PROTOPRIMER_PROTO_CODE.value: state_proto_code_file_abs_path_inited,
            },
        )
        mock_get_path_to_curr_python.assert_called_once()

    ####################################################################################################################
    @patch.dict(f"{os.__name__}.environ", {}, clear=True)
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_reboot_triggered.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_file_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_file_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_selected_python_file_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_venv_driver_prepared.__name__}.create_state_node")
    @patch(
        f"{primer_kernel.__name__}.get_path_to_curr_python",
        return_value="/mock_client_dir/venv/wrong/path/to/python",
    )
    @patch(f"{primer_kernel.__name__}.os.execve")
    @patch(f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_exec_mode_arg_loaded.__name__}.create_state_node")
    def test_failure_when_path_to_curr_python_is_inside_venv(
        self,
        mock_state_input_exec_mode_arg_loaded,
        mock_execve,
        mock_get_path_to_curr_python,
        mock_state_venv_driver_prepared,
        mock_state_selected_python_file_abs_path_inited,
        mock_state_local_venv_dir_abs_path_inited,
        mock_state_local_conf_file_abs_path_inited,
        mock_state_proto_code_file_abs_path_inited,
        mock_state_args_parsed,
        mock_state_reboot_triggered,
        mock_state_input_start_id_var_loaded,
    ):

        # given:

        assert_parent_factories_mocked(
            self.env_ctx,
            EnvState.state_stride_py_venv_reached.name,
        )

        mock_state_args_parsed.return_value.eval_own_state.return_value = argparse.Namespace()
        mock_state_input_start_id_var_loaded.return_value.eval_own_state.return_value = "mock_start_id"
        mock_state_reboot_triggered.return_value.eval_own_state.return_value = False
        mock_state_proto_code_file_abs_path_inited.return_value.eval_own_state.return_value = state_proto_code_file_abs_path_inited

        mock_state_selected_python_file_abs_path_inited.return_value.eval_own_state.return_value = test_python_abs_path
        mock_state_local_venv_dir_abs_path_inited.return_value.eval_own_state.return_value = os.path.join(mock_client_dir, ConfConstEnv.default_dir_rel_path_venv)
        mock_state_local_conf_file_abs_path_inited.return_value.eval_own_state.return_value = "fake: " + EnvState.state_local_conf_file_abs_path_inited.name

        # when:
        with self.assertRaises(AssertionError) as cm:
            self.env_ctx.state_graph.eval_state(EnvState.state_stride_py_venv_reached.name, self.env_ctx)

        # then:
        self.assertIn(
            "must be outside of the `venv`",
            str(cm.exception),
        )
        mock_state_venv_driver_prepared.return_value.eval_own_state.return_value.create_venv.assert_not_called()
        mock_execve.assert_not_called()
        mock_get_path_to_curr_python.assert_called_once()

    ####################################################################################################################
    @patch.dict(f"{os.__name__}.environ", {}, clear=True)
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_reboot_triggered.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_file_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_file_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_selected_python_file_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_venv_driver_prepared.__name__}.create_state_node")
    @patch(
        f"{primer_kernel.__name__}.get_path_to_curr_python",
        # expected path to `python`:
        return_value="/mock_client_dir/venv/bin/python",
    )
    @patch(f"{primer_kernel.__name__}.os.execve")
    @patch(f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_exec_mode_arg_loaded.__name__}.create_state_node")
    def test_failure_when_path_to_curr_python_is_inside_venv_initially_and_expected(
        self,
        mock_state_input_exec_mode_arg_loaded,
        mock_execve,
        mock_get_path_to_curr_python,
        mock_state_venv_driver_prepared,
        mock_state_selected_python_file_abs_path_inited,
        mock_state_local_venv_dir_abs_path_inited,
        mock_state_local_conf_file_abs_path_inited,
        mock_state_proto_code_file_abs_path_inited,
        mock_state_args_parsed,
        mock_state_reboot_triggered,
        mock_state_input_start_id_var_loaded,
    ):

        # given:

        assert_parent_factories_mocked(
            self.env_ctx,
            EnvState.state_stride_py_venv_reached.name,
        )

        mock_state_args_parsed.return_value.eval_own_state.return_value = argparse.Namespace()
        mock_state_input_start_id_var_loaded.return_value.eval_own_state.return_value = "mock_start_id"
        mock_state_reboot_triggered.return_value.eval_own_state.return_value = False
        mock_state_proto_code_file_abs_path_inited.return_value.eval_own_state.return_value = state_proto_code_file_abs_path_inited

        mock_state_selected_python_file_abs_path_inited.return_value.eval_own_state.return_value = test_python_abs_path
        mock_state_local_venv_dir_abs_path_inited.return_value.eval_own_state.return_value = os.path.join(mock_client_dir, ConfConstEnv.default_dir_rel_path_venv)
        mock_state_local_conf_file_abs_path_inited.return_value.eval_own_state.return_value = "fake: " + EnvState.state_local_conf_file_abs_path_inited.name

        # when:
        with self.assertRaises(AssertionError) as cm:
            self.env_ctx.state_graph.eval_state(EnvState.state_stride_py_venv_reached.name, self.env_ctx)

        # then:
        self.assertIn(
            "must be outside of the `venv`",
            str(cm.exception),
        )
        mock_state_venv_driver_prepared.return_value.eval_own_state.return_value.create_venv.assert_not_called()
        mock_execve.assert_not_called()
        mock_get_path_to_curr_python.assert_called_once()

    ####################################################################################################################
    @patch.dict(f"{os.__name__}.environ", {}, clear=True)
    @patch.object(sys, "argv", ["/path/to/script.py", "--some-arg"])
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_reboot_triggered.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_file_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_file_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_selected_python_file_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_venv_driver_prepared.__name__}.create_state_node")
    @patch(
        f"{primer_kernel.__name__}.get_path_to_curr_python",
        return_value=test_python_abs_path,
    )
    @patch(f"{primer_kernel.__name__}.os.execve")
    @patch(f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_exec_mode_arg_loaded.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.is_same_file", return_value=False)
    def test_failure_when_path_to_python_differs_from_path_to_curr_python(
        self,
        mock_state_input_exec_mode_arg_loaded,
        mock_is_same_file,
        mock_execve,
        mock_get_path_to_curr_python,
        mock_state_venv_driver_prepared,
        mock_state_selected_python_file_abs_path_inited,
        mock_state_local_venv_dir_abs_path_inited,
        mock_state_local_conf_file_abs_path_inited,
        mock_state_proto_code_file_abs_path_inited,
        mock_state_args_parsed,
        mock_state_reboot_triggered,
        mock_state_input_start_id_var_loaded,
    ):

        # given:

        assert_parent_factories_mocked(
            self.env_ctx,
            EnvState.state_stride_py_venv_reached.name,
        )

        mock_state_args_parsed.return_value.eval_own_state.return_value = argparse.Namespace()
        mock_state_input_start_id_var_loaded.return_value.eval_own_state.return_value = "mock_start_id"
        mock_state_reboot_triggered.return_value.eval_own_state.return_value = False
        mock_state_proto_code_file_abs_path_inited.return_value.eval_own_state.return_value = state_proto_code_file_abs_path_inited

        mock_state_selected_python_file_abs_path_inited.return_value.eval_own_state.return_value = non_default_file_abs_path_python
        mock_state_local_venv_dir_abs_path_inited.return_value.eval_own_state.return_value = ConfConstEnv.default_dir_rel_path_venv
        mock_state_local_conf_file_abs_path_inited.return_value.eval_own_state.return_value = "fake: " + EnvState.state_local_conf_file_abs_path_inited.name

        # when:
        with self.assertRaises(AssertionError) as cm:
            self.env_ctx.state_graph.eval_state(EnvState.state_stride_py_venv_reached.name, self.env_ctx)

        # then:
        self.assertIn(
            "must point to the same file as the selected one",
            str(cm.exception),
        )
        mock_state_venv_driver_prepared.return_value.eval_own_state.return_value.create_venv.assert_not_called()
        mock_execve.assert_not_called()
        mock_get_path_to_curr_python.assert_called_once()

    ####################################################################################################################
    @patch.dict(f"{os.__name__}.environ", {}, clear=True)
    @patch.object(sys, "argv", ["/path/to/script.py", "--some-arg"])
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_reboot_triggered.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_file_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_file_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_selected_python_file_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_venv_driver_prepared.__name__}.create_state_node")
    @patch(
        f"{primer_kernel.__name__}.get_path_to_curr_python",
        return_value=test_python_abs_path,
    )
    @patch(f"{primer_kernel.__name__}.os.execve")
    @patch(f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_exec_mode_arg_loaded.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.is_same_file", return_value=True)
    def test_success_when_path_to_python_matches_path_to_curr_python_and_execv_is_called_for_venv_python(
        self,
        mock_state_input_exec_mode_arg_loaded,
        mock_is_same_file,
        mock_execve,
        mock_get_path_to_curr_python,
        mock_state_venv_driver_prepared,
        mock_state_selected_python_file_abs_path_inited,
        mock_state_local_venv_dir_abs_path_inited,
        mock_state_local_conf_file_abs_path_inited,
        mock_state_proto_code_file_abs_path_inited,
        mock_state_args_parsed,
        mock_state_reboot_triggered,
        mock_state_input_start_id_var_loaded,
    ):

        # given:

        assert_parent_factories_mocked(
            self.env_ctx,
            EnvState.state_stride_py_venv_reached.name,
        )

        mock_state_args_parsed.return_value.eval_own_state.return_value = argparse.Namespace()
        mock_state_input_start_id_var_loaded.return_value.eval_own_state.return_value = "mock_start_id"
        mock_state_reboot_triggered.return_value.eval_own_state.return_value = False
        mock_state_proto_code_file_abs_path_inited.return_value.eval_own_state.return_value = state_proto_code_file_abs_path_inited

        mock_state_selected_python_file_abs_path_inited.return_value.eval_own_state.return_value = test_python_abs_path
        mock_state_local_venv_dir_abs_path_inited.return_value.eval_own_state.return_value = os.path.join(mock_client_dir, ConfConstEnv.default_dir_rel_path_venv)
        mock_state_local_conf_file_abs_path_inited.return_value.eval_own_state.return_value = "fake: " + EnvState.state_local_conf_file_abs_path_inited.name

        # when:

        self.env_ctx.state_graph.eval_state(EnvState.state_stride_py_venv_reached.name, self.env_ctx)

        # then:

        path_to_venv = os.path.join(
            mock_client_dir,
            ConfConstEnv.default_dir_rel_path_venv,
        )
        mock_state_venv_driver_prepared.return_value.eval_own_state.return_value.create_venv.assert_called_once_with(
            path_to_venv,
        )
        path_to_venv_python = os.path.join(
            path_to_venv,
            ConfConstGeneral.file_rel_path_venv_python,
        )
        expected_argv = [
            path_to_venv_python,
            "-I",
            "/path/to/script.py",
            "--some-arg",
        ]
        mock_execve.assert_called_once_with(
            path=path_to_venv_python,
            argv=expected_argv,
            env={
                EnvVar.var_PROTOPRIMER_PY_EXEC.value: StateStride.stride_py_venv.name,
                EnvVar.var_PROTOPRIMER_START_ID.value: "mock_start_id",
                EnvVar.var_PROTOPRIMER_PROTO_CODE.value: state_proto_code_file_abs_path_inited,
            },
        )
        mock_get_path_to_curr_python.assert_called_once()

    ####################################################################################################################
    @patch.dict(f"{os.__name__}.environ", {}, clear=True)
    @patch.object(sys, "argv", ["/path/to/script.py", "--some-arg"])
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_reboot_triggered.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_file_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_file_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_selected_python_file_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_venv_driver_prepared.__name__}.create_state_node")
    @patch(
        f"{primer_kernel.__name__}.get_path_to_curr_python",
        return_value=non_default_file_abs_path_python,
    )
    @patch(f"{primer_kernel.__name__}.os.execve")
    @patch(f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_exec_mode_arg_loaded.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.is_same_file", return_value=True)
    def test_success_when_path_to_python_is_not_inside_existing_venv(
        self,
        mock_state_input_exec_mode_arg_loaded,
        mock_is_same_file,
        mock_execve,
        mock_get_path_to_curr_python,
        mock_state_venv_driver_prepared,
        mock_state_selected_python_file_abs_path_inited,
        mock_state_local_venv_dir_abs_path_inited,
        mock_state_local_conf_file_abs_path_inited,
        mock_state_proto_code_file_abs_path_inited,
        mock_state_args_parsed,
        mock_state_reboot_triggered,
        mock_state_input_start_id_var_loaded,
    ):

        # given:

        assert_parent_factories_mocked(
            self.env_ctx,
            EnvState.state_stride_py_venv_reached.name,
        )

        mock_state_args_parsed.return_value.eval_own_state.return_value = argparse.Namespace()
        mock_state_input_start_id_var_loaded.return_value.eval_own_state.return_value = "mock_start_id"
        mock_state_reboot_triggered.return_value.eval_own_state.return_value = False
        mock_state_proto_code_file_abs_path_inited.return_value.eval_own_state.return_value = state_proto_code_file_abs_path_inited

        mock_state_selected_python_file_abs_path_inited.return_value.eval_own_state.return_value = non_default_file_abs_path_python
        mock_state_local_venv_dir_abs_path_inited.return_value.eval_own_state.return_value = non_default_dir_abs_path_venv
        mock_state_local_conf_file_abs_path_inited.return_value.eval_own_state.return_value = "fake: " + EnvState.state_local_conf_file_abs_path_inited.name

        # when:

        self.env_ctx.state_graph.eval_state(EnvState.state_stride_py_venv_reached.name, self.env_ctx)

        # then:

        mock_state_venv_driver_prepared.return_value.eval_own_state.return_value.create_venv.assert_called_once_with(
            non_default_dir_abs_path_venv,
        )

        path_to_venv_python = os.path.join(
            non_default_dir_abs_path_venv,
            ConfConstGeneral.file_rel_path_venv_python,
        )
        expected_argv = [
            path_to_venv_python,
            "-I",
            "/path/to/script.py",
            "--some-arg",
        ]
        mock_execve.assert_called_once_with(
            path=path_to_venv_python,
            argv=expected_argv,
            env={
                EnvVar.var_PROTOPRIMER_PY_EXEC.value: StateStride.stride_py_venv.name,
                EnvVar.var_PROTOPRIMER_START_ID.value: "mock_start_id",
                EnvVar.var_PROTOPRIMER_PROTO_CODE.value: state_proto_code_file_abs_path_inited,
            },
        )

        mock_get_path_to_curr_python.assert_called_once()

    ####################################################################################################################
    @patch.dict(f"{os.__name__}.environ", {}, clear=True)
    @patch.object(sys, "argv", ["/path/to/script.py", "--some-arg"])
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_reboot_triggered.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_file_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_file_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_selected_python_file_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_venv_driver_prepared.__name__}.create_state_node")
    @patch(
        f"{primer_kernel.__name__}.get_path_to_curr_python",
        return_value="/a/different/python",
    )
    @patch(f"{primer_kernel.__name__}.os.execve")
    @patch(f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_exec_mode_arg_loaded.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.is_same_file", return_value=True)
    def test_success_on_arbitrary_py_exec_outside_venv(
        self,
        mock_state_input_exec_mode_arg_loaded,
        mock_is_same_file,
        mock_execve,
        mock_get_path_to_curr_python,
        mock_state_venv_driver_prepared,
        mock_state_selected_python_file_abs_path_inited,
        mock_state_local_venv_dir_abs_path_inited,
        mock_state_local_conf_file_abs_path_inited,
        mock_state_proto_code_file_abs_path_inited,
        mock_state_args_parsed,
        mock_state_reboot_triggered,
        mock_state_input_start_id_var_loaded,
    ):

        # given:

        assert_parent_factories_mocked(
            self.env_ctx,
            EnvState.state_stride_py_venv_reached.name,
        )

        mock_state_args_parsed.return_value.eval_own_state.return_value = argparse.Namespace()
        mock_state_input_start_id_var_loaded.return_value.eval_own_state.return_value = "mock_start_id"
        mock_state_reboot_triggered.return_value.eval_own_state.return_value = False
        mock_state_proto_code_file_abs_path_inited.return_value.eval_own_state.return_value = "any/path"

        # Important: it should be `StateStride.stride_py_arbitrary` for this test case:
        self.env_ctx.state_stride = StateStride.stride_py_arbitrary

        # Make sure `path_to_curr_python` != `configured python`:
        mock_state_selected_python_file_abs_path_inited.return_value.eval_own_state.return_value = "/a/different/python"

        # Make sure `is_sub_path` is false:
        mock_state_local_venv_dir_abs_path_inited.return_value.eval_own_state.return_value = "/not/the/parent/of/current/python"

        mock_state_local_conf_file_abs_path_inited.return_value.eval_own_state.return_value = "any/path"

        # when:
        self.env_ctx.state_graph.eval_state(EnvState.state_stride_py_venv_reached.name, self.env_ctx)

        # then:
        path_to_venv_python = os.path.join(
            "/not/the/parent/of/current/python",
            ConfConstGeneral.file_rel_path_venv_python,
        )
        expected_argv = [
            path_to_venv_python,
            "-I",
            "/path/to/script.py",
            "--some-arg",
        ]
        mock_execve.assert_called_once_with(
            path=path_to_venv_python,
            argv=expected_argv,
            env={
                EnvVar.var_PROTOPRIMER_PY_EXEC.value: StateStride.stride_py_venv.name,
                EnvVar.var_PROTOPRIMER_START_ID.value: "mock_start_id",
                EnvVar.var_PROTOPRIMER_PROTO_CODE.value: "any/path",
            },
        )
        mock_state_venv_driver_prepared.return_value.eval_own_state.return_value.create_venv.assert_called_once()
        mock_get_path_to_curr_python.assert_called_once()

    ####################################################################################################################
    @patch.dict(
        f"{os.__name__}.environ",
        {primer_kernel.EnvVar.var_PROTOPRIMER_PY_EXEC.value: StateStride.stride_py_venv.name},
        clear=True,
    )
    @patch.object(sys, "argv", ["/path/to/script.py", "--some-arg"])
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_reboot_triggered.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_file_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_file_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_selected_python_file_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_venv_driver_prepared.__name__}.create_state_node")
    @patch(
        f"{primer_kernel.__name__}.get_path_to_curr_python",
    )
    @patch(f"{primer_kernel.__name__}.os.execve")
    @patch(f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_exec_mode_arg_loaded.__name__}.create_state_node")
    def test_success_when_py_exec_is_already_venv(
        self,
        mock_state_input_exec_mode_arg_loaded,
        mock_execve,
        mock_get_path_to_curr_python,
        mock_state_venv_driver_prepared,
        mock_state_selected_python_file_abs_path_inited,
        mock_state_local_venv_dir_abs_path_inited,
        mock_state_local_conf_file_abs_path_inited,
        mock_state_proto_code_file_abs_path_inited,
        mock_state_args_parsed,
        mock_state_reboot_triggered,
        mock_state_input_start_id_var_loaded,
    ):

        # given:

        assert_parent_factories_mocked(
            self.env_ctx,
            EnvState.state_stride_py_venv_reached.name,
        )

        self.env_ctx.state_stride = StateStride.stride_py_venv

        # when:

        actual_result = self.env_ctx.state_graph.eval_state(EnvState.state_stride_py_venv_reached.name, self.env_ctx)

        # then:

        self.assertEqual(StateStride.stride_py_venv, actual_result)

        mock_state_venv_driver_prepared.return_value.eval_own_state.return_value.create_venv.assert_not_called()
        mock_execve.assert_not_called()

    ####################################################################################################################
    @patch.dict(f"{os.__name__}.environ", {}, clear=True)
    @patch.object(sys, "argv", ["/path/to/script.py", "--some-arg"])
    @patch(f"{primer_kernel.__name__}.logger.info")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_reboot_triggered.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_file_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_file_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_selected_python_file_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_venv_driver_prepared.__name__}.create_state_node")
    @patch(
        f"{primer_kernel.__name__}.get_path_to_curr_python",
        return_value=test_python_abs_path,
    )
    @patch(f"{primer_kernel.__name__}.os.execve")
    @patch(f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_exec_mode_arg_loaded.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.is_same_file", return_value=True)
    def test_success_when_reusing_existing_venv(
        self,
        mock_state_input_exec_mode_arg_loaded,
        mock_is_same_file,
        mock_execve,
        mock_get_path_to_curr_python,
        mock_state_venv_driver_prepared,
        mock_state_selected_python_file_abs_path_inited,
        mock_state_local_venv_dir_abs_path_inited,
        mock_state_local_conf_file_abs_path_inited,
        mock_state_proto_code_file_abs_path_inited,
        mock_state_args_parsed,
        mock_state_reboot_triggered,
        mock_state_input_start_id_var_loaded,
        mock_logger_info,
    ):

        # given:

        assert_parent_factories_mocked(
            self.env_ctx,
            EnvState.state_stride_py_venv_reached.name,
        )

        mock_state_args_parsed.return_value.eval_own_state.return_value = argparse.Namespace()
        mock_state_input_start_id_var_loaded.return_value.eval_own_state.return_value = "mock_start_id"
        mock_state_reboot_triggered.return_value.eval_own_state.return_value = False
        mock_state_proto_code_file_abs_path_inited.return_value.eval_own_state.return_value = state_proto_code_file_abs_path_inited

        mock_state_selected_python_file_abs_path_inited.return_value.eval_own_state.return_value = test_python_abs_path
        path_to_venv = os.path.join(mock_client_dir, ConfConstEnv.default_dir_rel_path_venv)
        mock_state_local_venv_dir_abs_path_inited.return_value.eval_own_state.return_value = path_to_venv
        mock_state_local_conf_file_abs_path_inited.return_value.eval_own_state.return_value = "fake: " + EnvState.state_local_conf_file_abs_path_inited.name

        self.fs.create_dir(path_to_venv)

        # when:

        self.env_ctx.state_graph.eval_state(EnvState.state_stride_py_venv_reached.name, self.env_ctx)

        # then:

        mock_state_venv_driver_prepared.return_value.eval_own_state.return_value.create_venv.assert_not_called()
        mock_logger_info.assert_any_call(f"reusing existing `venv` [{path_to_venv}]")

        path_to_venv_python = os.path.join(
            path_to_venv,
            ConfConstGeneral.file_rel_path_venv_python,
        )
        expected_argv = [
            path_to_venv_python,
            "-I",
            "/path/to/script.py",
            "--some-arg",
        ]
        mock_execve.assert_called_once_with(
            path=path_to_venv_python,
            argv=expected_argv,
            env={
                EnvVar.var_PROTOPRIMER_PY_EXEC.value: StateStride.stride_py_venv.name,
                EnvVar.var_PROTOPRIMER_START_ID.value: "mock_start_id",
                EnvVar.var_PROTOPRIMER_PROTO_CODE.value: state_proto_code_file_abs_path_inited,
            },
        )
        mock_get_path_to_curr_python.assert_called_once()

    ####################################################################################################################
    @patch.dict(f"{os.__name__}.environ", {}, clear=True)
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_reboot_triggered.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_file_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_file_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_selected_python_file_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{Bootstrapper_state_venv_driver_prepared.__name__}.create_state_node")
    @patch(
        f"{primer_kernel.__name__}.get_path_to_curr_python",
        return_value=test_python_abs_path,
    )
    @patch(f"{primer_kernel.__name__}.os.execve")
    @patch(f"{primer_kernel.__name__}.{primer_kernel.VenvDriverPip.__name__}.create_venv")
    @patch(f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_exec_mode_arg_loaded.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.is_same_file", return_value=True)
    def test_failure_when_reusing_existing_venv_of_wrong_type(
        self,
        mock_state_input_exec_mode_arg_loaded,
        mock_is_same_file,
        mock_venv_venv_pip_create_venv,
        mock_execve,
        mock_get_path_to_curr_python,
        mock_state_venv_driver_prepared,
        mock_state_selected_python_file_abs_path_inited,
        mock_state_local_venv_dir_abs_path_inited,
        mock_state_local_conf_file_abs_path_inited,
        mock_state_proto_code_file_abs_path_inited,
        mock_state_args_parsed,
        mock_state_reboot_triggered,
        mock_state_input_start_id_var_loaded,
    ):
        # given:
        assert_parent_factories_mocked(
            self.env_ctx,
            EnvState.state_stride_py_venv_reached.name,
        )

        mock_state_args_parsed.return_value.eval_own_state.return_value = argparse.Namespace()
        mock_state_input_start_id_var_loaded.return_value.eval_own_state.return_value = "mock_start_id"
        mock_state_reboot_triggered.return_value.eval_own_state.return_value = False
        mock_state_proto_code_file_abs_path_inited.return_value.eval_own_state.return_value = state_proto_code_file_abs_path_inited

        mock_state_selected_python_file_abs_path_inited.return_value.eval_own_state.return_value = test_python_abs_path
        path_to_venv = os.path.join(mock_client_dir, ConfConstEnv.default_dir_rel_path_venv)
        mock_state_local_venv_dir_abs_path_inited.return_value.eval_own_state.return_value = path_to_venv
        mock_state_local_conf_file_abs_path_inited.return_value.eval_own_state.return_value = "fake: " + EnvState.state_local_conf_file_abs_path_inited.name

        # Create an uv-style `venv`:
        self.fs.create_dir(path_to_venv)
        self.fs.create_file(os.path.join(path_to_venv, "pyvenv.cfg"), contents="uv = 1.2.3")

        # But the driver is pip
        from protoprimer.primer_kernel import VenvDriverPip

        mock_state_venv_driver_prepared.return_value.eval_own_state.return_value = VenvDriverPip(
            test_python_abs_path,
            test_python_version,
            path_to_venv,
        )

        # when:
        with self.assertRaises(AssertionError) as cm:
            self.env_ctx.state_graph.eval_state(EnvState.state_stride_py_venv_reached.name, self.env_ctx)

        # then:
        self.assertIn("was not created by this driver", str(cm.exception))
        mock_venv_venv_pip_create_venv.assert_not_called()
        mock_execve.assert_not_called()
