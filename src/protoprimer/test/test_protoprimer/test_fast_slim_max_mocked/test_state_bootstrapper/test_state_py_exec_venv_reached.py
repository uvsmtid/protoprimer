import argparse
import os
import sys
from unittest.mock import patch

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.mock_verifier import (
    assert_parent_states_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_args_parsed,
    Bootstrapper_state_input_py_exec_var_loaded,
    Bootstrapper_state_input_start_id_var_loaded,
    Bootstrapper_state_local_conf_file_abs_path_inited,
    Bootstrapper_state_local_venv_dir_abs_path_inited,
    Bootstrapper_state_package_driver_prepared,
    Bootstrapper_state_proto_code_file_abs_path_inited,
    Bootstrapper_state_reinstall_triggered,
    Bootstrapper_state_required_python_file_abs_path_inited,
    ConfConstEnv,
    ConfConstGeneral,
    EnvContext,
    EnvState,
    EnvVar,
    ParsedArg,
    PythonExecutable,
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

        self.fs.create_dir(target_dst_dir_path)

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_str(EnvState.state_py_exec_venv_reached.name)

    def test_assumptions_used_in_other_tests(self):
        self.assertNotEqual(
            non_default_file_abs_path_python,
            ConfConstEnv.default_file_abs_path_python,
        )

    ####################################################################################################################
    @patch.dict(f"{os.__name__}.environ", {}, clear=True)
    @patch.object(sys, "argv", ["/path/to/script.py", "--some-arg"])
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_reinstall_triggered.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_py_exec_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_required_python_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_package_driver_prepared.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.get_path_to_curr_python",
        return_value=ConfConstEnv.default_file_abs_path_python,
    )
    @patch(f"{primer_kernel.__name__}.os.execve")
    @patch(f"{primer_kernel.__name__}.venv.create")
    @patch(
        f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_run_mode_arg_loaded.__name__}.eval_own_state"
    )
    def test_success_on_path_to_curr_python_is_outside_of_path_to_venv_when_venv_is_created(
        self,
        mock_state_input_run_mode_arg_loaded,
        mock_venv_create,
        mock_execve,
        mock_get_path_to_curr_python,
        mock_state_package_driver_prepared,
        mock_state_required_python_file_abs_path_inited,
        mock_state_local_venv_dir_abs_path_inited,
        mock_state_local_conf_file_abs_path_inited,
        mock_state_input_py_exec_var_loaded,
        mock_state_proto_code_file_abs_path_inited,
        mock_state_args_parsed,
        mock_state_reinstall_triggered,
        mock_state_input_start_id_var_loaded,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_py_exec_venv_reached.name,
        )

        mock_state_args_parsed.return_value = argparse.Namespace(
            **{
                ParsedArg.name_reinstall.value: False,
            }
        )
        mock_state_input_start_id_var_loaded.return_value = "mock_start_id"
        mock_state_reinstall_triggered.return_value = False
        mock_state_proto_code_file_abs_path_inited.return_value = (
            state_proto_code_file_abs_path_inited
        )
        mock_state_input_py_exec_var_loaded.return_value = (
            PythonExecutable.py_exec_required
        )
        mock_state_required_python_file_abs_path_inited.return_value = (
            ConfConstEnv.default_file_abs_path_python
        )
        mock_state_local_venv_dir_abs_path_inited.return_value = os.path.join(
            mock_client_dir, ConfConstEnv.default_dir_rel_path_venv
        )
        mock_state_local_conf_file_abs_path_inited.return_value = (
            "fake: " + EnvState.state_local_conf_file_abs_path_inited.name
        )

        # when:

        self.env_ctx.state_graph.eval_state(EnvState.state_py_exec_venv_reached.name)

        # then:

        mock_state_package_driver_prepared.return_value.create_venv.assert_called_once_with(
            ConfConstEnv.default_file_abs_path_python,
            os.path.join(
                mock_client_dir,
                ConfConstEnv.default_dir_rel_path_venv,
            ),
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
                EnvVar.var_PROTOPRIMER_PY_EXEC.value: PythonExecutable.py_exec_venv.name,
                EnvVar.var_PROTOPRIMER_START_ID.value: "mock_start_id",
                EnvVar.var_PROTOPRIMER_PROTO_CODE.value: state_proto_code_file_abs_path_inited,
            },
        )
        mock_get_path_to_curr_python.assert_called_once()

    ####################################################################################################################
    @patch.dict(f"{os.__name__}.environ", {}, clear=True)
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_reinstall_triggered.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_py_exec_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_required_python_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_package_driver_prepared.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.get_path_to_curr_python",
        return_value="/mock_client_dir/venv/wrong/path/to/python",
    )
    @patch(f"{primer_kernel.__name__}.os.execve")
    @patch(f"{primer_kernel.__name__}.venv.create")
    @patch(
        f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_run_mode_arg_loaded.__name__}.eval_own_state"
    )
    def test_failure_when_path_to_curr_python_is_inside_venv(
        self,
        mock_state_input_run_mode_arg_loaded,
        mock_venv_create,
        mock_execve,
        mock_get_path_to_curr_python,
        mock_state_package_driver_prepared,
        mock_state_required_python_file_abs_path_inited,
        mock_state_local_venv_dir_abs_path_inited,
        mock_state_local_conf_file_abs_path_inited,
        mock_state_input_py_exec_var_loaded,
        mock_state_proto_code_file_abs_path_inited,
        mock_state_args_parsed,
        mock_state_reinstall_triggered,
        mock_state_input_start_id_var_loaded,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_py_exec_venv_reached.name,
        )

        mock_state_args_parsed.return_value = argparse.Namespace(
            **{
                ParsedArg.name_reinstall.value: False,
            }
        )
        mock_state_input_start_id_var_loaded.return_value = "mock_start_id"
        mock_state_reinstall_triggered.return_value = False
        mock_state_proto_code_file_abs_path_inited.return_value = (
            state_proto_code_file_abs_path_inited
        )
        mock_state_input_py_exec_var_loaded.return_value = (
            PythonExecutable.py_exec_required
        )
        mock_state_required_python_file_abs_path_inited.return_value = (
            ConfConstEnv.default_file_abs_path_python
        )
        mock_state_local_venv_dir_abs_path_inited.return_value = os.path.join(
            mock_client_dir, ConfConstEnv.default_dir_rel_path_venv
        )
        mock_state_local_conf_file_abs_path_inited.return_value = (
            "fake: " + EnvState.state_local_conf_file_abs_path_inited.name
        )

        # when:
        with self.assertRaises(AssertionError) as cm:
            self.env_ctx.state_graph.eval_state(
                EnvState.state_py_exec_venv_reached.name
            )

        # then:
        self.assertIn(
            "must be outside of the `venv`",
            str(cm.exception),
        )
        mock_venv_create.assert_not_called()
        mock_execve.assert_not_called()
        mock_get_path_to_curr_python.assert_called_once()

    ####################################################################################################################
    @patch.dict(f"{os.__name__}.environ", {}, clear=True)
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_reinstall_triggered.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_py_exec_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_required_python_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_package_driver_prepared.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.get_path_to_curr_python",
        # expected path to `python`:
        return_value="/mock_client_dir/venv/bin/python",
    )
    @patch(f"{primer_kernel.__name__}.os.execve")
    @patch(f"{primer_kernel.__name__}.venv.create")
    @patch(
        f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_run_mode_arg_loaded.__name__}.eval_own_state"
    )
    def test_failure_when_path_to_curr_python_is_inside_venv_initially_and_expected(
        self,
        mock_state_input_run_mode_arg_loaded,
        mock_venv_create,
        mock_execve,
        mock_get_path_to_curr_python,
        mock_state_package_driver_prepared,
        mock_state_required_python_file_abs_path_inited,
        mock_state_local_venv_dir_abs_path_inited,
        mock_state_local_conf_file_abs_path_inited,
        mock_state_input_py_exec_var_loaded,
        mock_state_proto_code_file_abs_path_inited,
        mock_state_args_parsed,
        mock_state_reinstall_triggered,
        mock_state_input_start_id_var_loaded,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_py_exec_venv_reached.name,
        )

        mock_state_args_parsed.return_value = argparse.Namespace(
            **{
                ParsedArg.name_reinstall.value: False,
            }
        )
        mock_state_input_start_id_var_loaded.return_value = "mock_start_id"
        mock_state_reinstall_triggered.return_value = False
        mock_state_proto_code_file_abs_path_inited.return_value = (
            state_proto_code_file_abs_path_inited
        )
        mock_state_input_py_exec_var_loaded.return_value = (
            PythonExecutable.py_exec_required
        )
        mock_state_required_python_file_abs_path_inited.return_value = (
            ConfConstEnv.default_file_abs_path_python
        )
        mock_state_local_venv_dir_abs_path_inited.return_value = os.path.join(
            mock_client_dir, ConfConstEnv.default_dir_rel_path_venv
        )
        mock_state_local_conf_file_abs_path_inited.return_value = (
            "fake: " + EnvState.state_local_conf_file_abs_path_inited.name
        )

        # when:
        with self.assertRaises(AssertionError) as cm:
            self.env_ctx.state_graph.eval_state(
                EnvState.state_py_exec_venv_reached.name
            )

        # then:
        self.assertIn(
            "must be outside of the `venv`",
            str(cm.exception),
        )
        mock_venv_create.assert_not_called()
        mock_execve.assert_not_called()
        mock_get_path_to_curr_python.assert_called_once()

    ####################################################################################################################
    @patch.dict(f"{os.__name__}.environ", {}, clear=True)
    @patch.object(sys, "argv", ["/path/to/script.py", "--some-arg"])
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_reinstall_triggered.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_py_exec_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_required_python_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_package_driver_prepared.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.get_path_to_curr_python",
        return_value=ConfConstEnv.default_file_abs_path_python,
    )
    @patch(f"{primer_kernel.__name__}.os.execve")
    @patch(f"{primer_kernel.__name__}.venv.create")
    @patch(
        f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_run_mode_arg_loaded.__name__}.eval_own_state"
    )
    def test_failure_when_path_to_python_differs_from_path_to_curr_python(
        self,
        mock_state_input_run_mode_arg_loaded,
        mock_venv_create,
        mock_execve,
        mock_get_path_to_curr_python,
        mock_state_package_driver_prepared,
        mock_state_required_python_file_abs_path_inited,
        mock_state_local_venv_dir_abs_path_inited,
        mock_state_local_conf_file_abs_path_inited,
        mock_state_input_py_exec_var_loaded,
        mock_state_proto_code_file_abs_path_inited,
        mock_state_args_parsed,
        mock_state_reinstall_triggered,
        mock_state_input_start_id_var_loaded,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_py_exec_venv_reached.name,
        )

        mock_state_args_parsed.return_value = argparse.Namespace(
            **{
                ParsedArg.name_reinstall.value: False,
            }
        )
        mock_state_input_start_id_var_loaded.return_value = "mock_start_id"
        mock_state_reinstall_triggered.return_value = False
        mock_state_proto_code_file_abs_path_inited.return_value = (
            state_proto_code_file_abs_path_inited
        )
        mock_state_input_py_exec_var_loaded.return_value = (
            PythonExecutable.py_exec_required
        )
        mock_state_required_python_file_abs_path_inited.return_value = (
            non_default_file_abs_path_python
        )
        mock_state_local_venv_dir_abs_path_inited.return_value = (
            ConfConstEnv.default_dir_rel_path_venv
        )
        mock_state_local_conf_file_abs_path_inited.return_value = (
            "fake: " + EnvState.state_local_conf_file_abs_path_inited.name
        )

        # when:
        with self.assertRaises(AssertionError) as cm:
            self.env_ctx.state_graph.eval_state(
                EnvState.state_py_exec_venv_reached.name
            )

        # then:
        self.assertIn(
            "must match the required",
            str(cm.exception),
        )
        mock_venv_create.assert_not_called()
        mock_execve.assert_not_called()
        mock_get_path_to_curr_python.assert_called_once()

    ####################################################################################################################
    @patch.dict(f"{os.__name__}.environ", {}, clear=True)
    @patch.object(sys, "argv", ["/path/to/script.py", "--some-arg"])
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_reinstall_triggered.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_py_exec_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_required_python_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_package_driver_prepared.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.get_path_to_curr_python",
        return_value=ConfConstEnv.default_file_abs_path_python,
    )
    @patch(f"{primer_kernel.__name__}.os.execve")
    @patch(f"{primer_kernel.__name__}.venv.create")
    @patch(
        f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_run_mode_arg_loaded.__name__}.eval_own_state"
    )
    def test_success_when_path_to_python_matches_path_to_curr_python_and_execv_is_called_for_venv_python(
        self,
        mock_state_input_run_mode_arg_loaded,
        mock_venv_create,
        mock_execve,
        mock_get_path_to_curr_python,
        mock_state_package_driver_prepared,
        mock_state_required_python_file_abs_path_inited,
        mock_state_local_venv_dir_abs_path_inited,
        mock_state_local_conf_file_abs_path_inited,
        mock_state_input_py_exec_var_loaded,
        mock_state_proto_code_file_abs_path_inited,
        mock_state_args_parsed,
        mock_state_reinstall_triggered,
        mock_state_input_start_id_var_loaded,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_py_exec_venv_reached.name,
        )

        mock_state_args_parsed.return_value = argparse.Namespace(
            **{
                ParsedArg.name_reinstall.value: False,
            }
        )
        mock_state_input_start_id_var_loaded.return_value = "mock_start_id"
        mock_state_reinstall_triggered.return_value = False
        mock_state_proto_code_file_abs_path_inited.return_value = (
            state_proto_code_file_abs_path_inited
        )
        mock_state_input_py_exec_var_loaded.return_value = (
            PythonExecutable.py_exec_required
        )
        mock_state_required_python_file_abs_path_inited.return_value = (
            ConfConstEnv.default_file_abs_path_python
        )
        mock_state_local_venv_dir_abs_path_inited.return_value = os.path.join(
            mock_client_dir, ConfConstEnv.default_dir_rel_path_venv
        )
        mock_state_local_conf_file_abs_path_inited.return_value = (
            "fake: " + EnvState.state_local_conf_file_abs_path_inited.name
        )

        # when:

        self.env_ctx.state_graph.eval_state(EnvState.state_py_exec_venv_reached.name)

        # then:

        path_to_venv = os.path.join(
            mock_client_dir,
            ConfConstEnv.default_dir_rel_path_venv,
        )
        mock_state_package_driver_prepared.return_value.create_venv.assert_called_once_with(
            ConfConstEnv.default_file_abs_path_python,
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
                EnvVar.var_PROTOPRIMER_PY_EXEC.value: PythonExecutable.py_exec_venv.name,
                EnvVar.var_PROTOPRIMER_START_ID.value: "mock_start_id",
                EnvVar.var_PROTOPRIMER_PROTO_CODE.value: state_proto_code_file_abs_path_inited,
            },
        )
        mock_get_path_to_curr_python.assert_called_once()

    ####################################################################################################################
    @patch.dict(f"{os.__name__}.environ", {}, clear=True)
    @patch.object(sys, "argv", ["/path/to/script.py", "--some-arg"])
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_reinstall_triggered.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_py_exec_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_required_python_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_package_driver_prepared.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.get_path_to_curr_python",
        return_value=non_default_file_abs_path_python,
    )
    @patch(f"{primer_kernel.__name__}.os.execve")
    @patch(f"{primer_kernel.__name__}.venv.create")
    @patch(
        f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_run_mode_arg_loaded.__name__}.eval_own_state"
    )
    def test_success_when_path_to_python_is_not_inside_existing_venv(
        self,
        mock_state_input_run_mode_arg_loaded,
        mock_venv_create,
        mock_execve,
        mock_get_path_to_curr_python,
        mock_state_package_driver_prepared,
        mock_state_required_python_file_abs_path_inited,
        mock_state_local_venv_dir_abs_path_inited,
        mock_state_local_conf_file_abs_path_inited,
        mock_state_input_py_exec_var_loaded,
        mock_state_proto_code_file_abs_path_inited,
        mock_state_args_parsed,
        mock_state_reinstall_triggered,
        mock_state_input_start_id_var_loaded,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_py_exec_venv_reached.name,
        )

        mock_state_args_parsed.return_value = argparse.Namespace(
            **{
                ParsedArg.name_reinstall.value: False,
            }
        )
        mock_state_input_start_id_var_loaded.return_value = "mock_start_id"
        mock_state_reinstall_triggered.return_value = False
        mock_state_proto_code_file_abs_path_inited.return_value = (
            state_proto_code_file_abs_path_inited
        )
        mock_state_input_py_exec_var_loaded.return_value = (
            PythonExecutable.py_exec_required
        )
        mock_state_required_python_file_abs_path_inited.return_value = (
            non_default_file_abs_path_python
        )
        mock_state_local_venv_dir_abs_path_inited.return_value = (
            non_default_dir_abs_path_venv
        )
        mock_state_local_conf_file_abs_path_inited.return_value = (
            "fake: " + EnvState.state_local_conf_file_abs_path_inited.name
        )

        # when:

        self.env_ctx.state_graph.eval_state(EnvState.state_py_exec_venv_reached.name)

        # then:

        mock_state_package_driver_prepared.return_value.create_venv.assert_called_once_with(
            non_default_file_abs_path_python,
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
                EnvVar.var_PROTOPRIMER_PY_EXEC.value: PythonExecutable.py_exec_venv.name,
                EnvVar.var_PROTOPRIMER_START_ID.value: "mock_start_id",
                EnvVar.var_PROTOPRIMER_PROTO_CODE.value: state_proto_code_file_abs_path_inited,
            },
        )

        mock_get_path_to_curr_python.assert_called_once()

    ####################################################################################################################
    @patch.dict(f"{os.__name__}.environ", {}, clear=True)
    @patch.object(sys, "argv", ["/path/to/script.py", "--some-arg"])
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_reinstall_triggered.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_py_exec_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_required_python_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_package_driver_prepared.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.get_path_to_curr_python",
        return_value="/a/different/python",
    )
    @patch(f"{primer_kernel.__name__}.os.execve")
    @patch(f"{primer_kernel.__name__}.venv.create")
    @patch(
        f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_run_mode_arg_loaded.__name__}.eval_own_state"
    )
    def test_success_on_arbitrary_py_exec_outside_venv(
        self,
        mock_state_input_run_mode_arg_loaded,
        mock_venv_create,
        mock_execve,
        mock_get_path_to_curr_python,
        mock_state_package_driver_prepared,
        mock_state_required_python_file_abs_path_inited,
        mock_state_local_venv_dir_abs_path_inited,
        mock_state_local_conf_file_abs_path_inited,
        mock_state_input_py_exec_var_loaded,
        mock_state_proto_code_file_abs_path_inited,
        mock_state_args_parsed,
        mock_state_reinstall_triggered,
        mock_state_input_start_id_var_loaded,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_py_exec_venv_reached.name,
        )

        mock_state_args_parsed.return_value = argparse.Namespace(
            **{
                ParsedArg.name_reinstall.value: False,
            }
        )
        mock_state_input_start_id_var_loaded.return_value = "mock_start_id"
        mock_state_reinstall_triggered.return_value = False
        mock_state_proto_code_file_abs_path_inited.return_value = "any/path"

        # Important: it should be `py_exec_arbitrary` for this test case:
        mock_state_input_py_exec_var_loaded.return_value = (
            PythonExecutable.py_exec_arbitrary
        )

        # Make sure `path_to_curr_python` != `configured python`:
        mock_state_required_python_file_abs_path_inited.return_value = (
            "/a/different/python"
        )

        # Make sure `is_sub_path` is false:
        mock_state_local_venv_dir_abs_path_inited.return_value = (
            "/not/the/parent/of/current/python"
        )

        mock_state_local_conf_file_abs_path_inited.return_value = "any/path"

        # when:
        self.env_ctx.state_graph.eval_state(EnvState.state_py_exec_venv_reached.name)

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
                EnvVar.var_PROTOPRIMER_PY_EXEC.value: PythonExecutable.py_exec_venv.name,
                EnvVar.var_PROTOPRIMER_START_ID.value: "mock_start_id",
                EnvVar.var_PROTOPRIMER_PROTO_CODE.value: "any/path",
            },
        )
        mock_state_package_driver_prepared.return_value.create_venv.assert_called_once()
        mock_get_path_to_curr_python.assert_called_once()

    ####################################################################################################################
    @patch.dict(
        f"{os.__name__}.environ",
        {
            primer_kernel.EnvVar.var_PROTOPRIMER_PY_EXEC.value: PythonExecutable.py_exec_venv.name
        },
        clear=True,
    )
    @patch.object(sys, "argv", ["/path/to/script.py", "--some-arg"])
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_reinstall_triggered.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_py_exec_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_required_python_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_package_driver_prepared.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.get_path_to_curr_python",
    )
    @patch(f"{primer_kernel.__name__}.os.execve")
    @patch(f"{primer_kernel.__name__}.venv.create")
    @patch(
        f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_run_mode_arg_loaded.__name__}.eval_own_state"
    )
    def test_success_when_py_exec_is_already_venv(
        self,
        mock_state_input_run_mode_arg_loaded,
        mock_venv_create,
        mock_execve,
        mock_get_path_to_curr_python,
        mock_state_package_driver_prepared,
        mock_state_required_python_file_abs_path_inited,
        mock_state_local_venv_dir_abs_path_inited,
        mock_state_local_conf_file_abs_path_inited,
        mock_state_input_py_exec_var_loaded,
        mock_state_proto_code_file_abs_path_inited,
        mock_state_args_parsed,
        mock_state_reinstall_triggered,
        mock_state_input_start_id_var_loaded,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_py_exec_venv_reached.name,
        )

        py_exec = PythonExecutable.py_exec_venv
        mock_state_input_py_exec_var_loaded.return_value = py_exec
        self.env_ctx.state_stride = py_exec

        # when:

        actual_result = self.env_ctx.state_graph.eval_state(
            EnvState.state_py_exec_venv_reached.name
        )

        # then:

        self.assertEqual(PythonExecutable.py_exec_venv, actual_result)

        mock_venv_create.assert_not_called()
        mock_execve.assert_not_called()

    ####################################################################################################################
    @patch.dict(f"{os.__name__}.environ", {}, clear=True)
    @patch.object(sys, "argv", ["/path/to/script.py", "--some-arg"])
    @patch(f"{primer_kernel.__name__}.logger.info")
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_reinstall_triggered.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_py_exec_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_required_python_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_package_driver_prepared.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.get_path_to_curr_python",
        return_value=ConfConstEnv.default_file_abs_path_python,
    )
    @patch(f"{primer_kernel.__name__}.os.execve")
    @patch(f"{primer_kernel.__name__}.venv.create")
    @patch(
        f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_run_mode_arg_loaded.__name__}.eval_own_state"
    )
    def test_success_when_reusing_existing_venv(
        self,
        mock_state_input_run_mode_arg_loaded,
        mock_venv_create,
        mock_execve,
        mock_get_path_to_curr_python,
        mock_state_package_driver_prepared,
        mock_state_required_python_file_abs_path_inited,
        mock_state_local_venv_dir_abs_path_inited,
        mock_state_local_conf_file_abs_path_inited,
        mock_state_input_py_exec_var_loaded,
        mock_state_proto_code_file_abs_path_inited,
        mock_state_args_parsed,
        mock_state_reinstall_triggered,
        mock_state_input_start_id_var_loaded,
        mock_logger_info,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_py_exec_venv_reached.name,
        )

        mock_state_args_parsed.return_value = argparse.Namespace(
            **{
                ParsedArg.name_reinstall.value: False,
            }
        )
        mock_state_input_start_id_var_loaded.return_value = "mock_start_id"
        mock_state_reinstall_triggered.return_value = False
        mock_state_proto_code_file_abs_path_inited.return_value = (
            state_proto_code_file_abs_path_inited
        )
        mock_state_input_py_exec_var_loaded.return_value = (
            PythonExecutable.py_exec_required
        )
        mock_state_required_python_file_abs_path_inited.return_value = (
            ConfConstEnv.default_file_abs_path_python
        )
        path_to_venv = os.path.join(
            mock_client_dir, ConfConstEnv.default_dir_rel_path_venv
        )
        mock_state_local_venv_dir_abs_path_inited.return_value = path_to_venv
        mock_state_local_conf_file_abs_path_inited.return_value = (
            "fake: " + EnvState.state_local_conf_file_abs_path_inited.name
        )

        self.fs.create_dir(path_to_venv)

        # when:

        self.env_ctx.state_graph.eval_state(EnvState.state_py_exec_venv_reached.name)

        # then:

        mock_venv_create.assert_not_called()
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
                EnvVar.var_PROTOPRIMER_PY_EXEC.value: PythonExecutable.py_exec_venv.name,
                EnvVar.var_PROTOPRIMER_START_ID.value: "mock_start_id",
                EnvVar.var_PROTOPRIMER_PROTO_CODE.value: state_proto_code_file_abs_path_inited,
            },
        )
        mock_get_path_to_curr_python.assert_called_once()

    ####################################################################################################################
    @patch.dict(f"{os.__name__}.environ", {}, clear=True)
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_reinstall_triggered.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_py_exec_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_required_python_file_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_package_driver_prepared.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.get_path_to_curr_python",
        return_value=ConfConstEnv.default_file_abs_path_python,
    )
    @patch(f"{primer_kernel.__name__}.os.execve")
    @patch(f"{primer_kernel.__name__}.venv.create")
    @patch(
        f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_run_mode_arg_loaded.__name__}.eval_own_state"
    )
    def test_failure_when_reusing_existing_venv_of_wrong_type(
        self,
        mock_state_input_run_mode_arg_loaded,
        mock_venv_create,
        mock_execve,
        mock_get_path_to_curr_python,
        mock_state_package_driver_prepared,
        mock_state_required_python_file_abs_path_inited,
        mock_state_local_venv_dir_abs_path_inited,
        mock_state_local_conf_file_abs_path_inited,
        mock_state_input_py_exec_var_loaded,
        mock_state_proto_code_file_abs_path_inited,
        mock_state_args_parsed,
        mock_state_reinstall_triggered,
        mock_state_input_start_id_var_loaded,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_py_exec_venv_reached.name,
        )

        mock_state_args_parsed.return_value = argparse.Namespace(
            **{
                ParsedArg.name_reinstall.value: False,
            }
        )
        mock_state_input_start_id_var_loaded.return_value = "mock_start_id"
        mock_state_reinstall_triggered.return_value = False
        mock_state_proto_code_file_abs_path_inited.return_value = (
            state_proto_code_file_abs_path_inited
        )
        mock_state_input_py_exec_var_loaded.return_value = (
            PythonExecutable.py_exec_required
        )
        mock_state_required_python_file_abs_path_inited.return_value = (
            ConfConstEnv.default_file_abs_path_python
        )
        path_to_venv = os.path.join(
            mock_client_dir, ConfConstEnv.default_dir_rel_path_venv
        )
        mock_state_local_venv_dir_abs_path_inited.return_value = path_to_venv
        mock_state_local_conf_file_abs_path_inited.return_value = (
            "fake: " + EnvState.state_local_conf_file_abs_path_inited.name
        )

        # Create an uv-style `venv`:
        self.fs.create_dir(path_to_venv)
        self.fs.create_file(
            os.path.join(path_to_venv, "pyvenv.cfg"), contents="uv = 1.2.3"
        )

        # But the driver is pip
        from protoprimer.primer_kernel import PackageDriverPip

        mock_state_package_driver_prepared.return_value = PackageDriverPip()

        # when:
        with self.assertRaises(AssertionError) as cm:
            self.env_ctx.state_graph.eval_state(
                EnvState.state_py_exec_venv_reached.name
            )

        # then:
        self.assertIn("was not created by this driver", str(cm.exception))
        mock_venv_create.assert_not_called()
        mock_execve.assert_not_called()
