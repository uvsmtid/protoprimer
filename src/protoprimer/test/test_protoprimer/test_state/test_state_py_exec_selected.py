import os
import sys
from unittest.mock import patch

from local_test.name_assertion import assert_test_module_name_embeds_str
from local_test.base_test_class import BasePyfakefsTestClass
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    ArgConst,
    Bootstrapper_state_client_dir_path_specified,
    Bootstrapper_state_env_conf_file_data,
    Bootstrapper_state_env_conf_file_path,
    Bootstrapper_state_proto_kernel_abs_path,
    Bootstrapper_state_py_exec_specified,
    Bootstrapper_state_target_dst_dir_path,
    ConfConstEnv,
    ConfConstGeneral,
    EnvContext,
    EnvState,
    PythonExecutable,
)

mock_client_dir = "/mock_client_dir"
state_proto_kernel_abs_path = os.path.join(
    mock_client_dir,
    ConfConstGeneral.default_proto_kernel_basename,
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

        self.fs.create_file(state_proto_kernel_abs_path)

        self.fs.create_dir(target_dst_dir_path)

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_str(EnvState.state_py_exec_selected.name)

    def test_assumptions_used_in_other_tests(self):
        self.assertNotEqual(
            non_default_file_abs_path_python,
            ConfConstEnv.default_file_abs_path_python,
        )

    ####################################################################################################################
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_target_dst_dir_path.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_proto_kernel_abs_path.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_specified.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_dir_path_specified.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_env_conf_file_data.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.get_path_to_curr_python",
        return_value=ConfConstEnv.default_file_abs_path_python,
    )
    @patch(f"{primer_kernel.__name__}.os.execv")
    @patch(f"{primer_kernel.__name__}.venv.create")
    def test_success_on_path_to_curr_python_is_outside_of_path_to_venv_when_venv_is_created(
        self,
        mock_venv_create,
        mock_execv,
        mock_get_path_to_curr_python,
        mock_state_env_conf_file_data,
        mock_state_client_dir_path_specified,
        mock_state_py_exec_specified,
        mock_state_proto_kernel_abs_path,
        mock_state_target_dst_dir_path,
    ):

        # given:

        mock_state_target_dst_dir_path.return_value = target_dst_dir_path

        mock_state_proto_kernel_abs_path.return_value = state_proto_kernel_abs_path

        mock_state_py_exec_specified.return_value = PythonExecutable.py_exec_required

        mock_state_client_dir_path_specified.return_value = mock_client_dir
        mock_state_env_conf_file_data.return_value = {
            ConfConstEnv.field_file_abs_path_python: ConfConstEnv.default_file_abs_path_python,
            ConfConstEnv.field_dir_rel_path_venv: ConfConstEnv.default_dir_rel_path_venv,
        }

        # when:

        self.env_ctx.bootstrap_state(EnvState.state_py_exec_selected.name)

        # then:

        mock_venv_create.assert_called_once_with(
            os.path.join(
                mock_client_dir,
                ConfConstEnv.default_dir_rel_path_venv,
            ),
            with_pip=True,
        )
        path_to_required_python = os.path.join(
            mock_client_dir,
            ConfConstEnv.default_dir_rel_path_venv,
            ConfConstGeneral.file_rel_path_venv_python,
        )
        mock_execv.assert_called_once_with(
            path_to_required_python,
            [
                path_to_required_python,
                *sys.argv,
                ArgConst.arg_py_exec,
                PythonExecutable.py_exec_venv.name,
                ArgConst.arg_proto_kernel_abs_path,
                state_proto_kernel_abs_path,
            ],
        )
        mock_get_path_to_curr_python.assert_called_once()

    ####################################################################################################################
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_target_dst_dir_path.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_proto_kernel_abs_path.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_specified.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_env_conf_file_path.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_dir_path_specified.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_env_conf_file_data.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.get_path_to_curr_python",
        return_value=ConfConstEnv.default_file_abs_path_python,
    )
    @patch(f"{primer_kernel.__name__}.os.execv")
    @patch(f"{primer_kernel.__name__}.venv.create")
    def test_failure_when_path_to_python_is_inside_venv(
        self,
        mock_venv_create,
        mock_execv,
        mock_get_path_to_curr_python,
        mock_state_env_conf_file_data,
        mock_state_client_dir_path_specified,
        mock_state_env_conf_file_path,
        mock_state_py_exec_specified,
        mock_state_proto_kernel_abs_path,
        mock_state_target_dst_dir_path,
    ):

        # given:

        mock_state_target_dst_dir_path.return_value = target_dst_dir_path

        mock_state_proto_kernel_abs_path.return_value = state_proto_kernel_abs_path

        mock_state_py_exec_specified.return_value = PythonExecutable.py_exec_required

        mock_state_client_dir_path_specified.return_value = mock_client_dir

        mock_state_env_conf_file_path.return_value = (
            "fake: " + EnvState.state_env_conf_file_path.name
        )

        mock_state_env_conf_file_data.return_value = {
            # NOTE: `python` path is inside `venv`:
            ConfConstEnv.field_file_abs_path_python: os.path.join(
                mock_client_dir,
                ConfConstEnv.default_dir_rel_path_venv,
                ConfConstGeneral.file_rel_path_venv_python,
            ),
            ConfConstEnv.field_dir_rel_path_venv: ConfConstEnv.default_dir_rel_path_venv,
        }

        # when:

        with self.assertRaises(AssertionError) as cm:
            self.env_ctx.bootstrap_state(EnvState.state_py_exec_selected.name)

        # then:

        self.assertIn(
            f"This is not allowed because `path_to_python` is used to init `venv` and cannot rely on `venv` existance.",
            str(cm.exception),
        )

        mock_venv_create.assert_not_called()
        mock_execv.assert_not_called()
        mock_get_path_to_curr_python.assert_not_called()

    ####################################################################################################################
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_target_dst_dir_path.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_proto_kernel_abs_path.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_specified.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_dir_path_specified.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_env_conf_file_data.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.get_path_to_curr_python",
        return_value="/mock_client_dir/venv/wrong/path/to/python",
    )
    @patch(f"{primer_kernel.__name__}.os.execv")
    @patch(f"{primer_kernel.__name__}.venv.create")
    def test_success_when_path_to_curr_python_is_inside_venv_but_different_from_venv_triggers_switch_to_required_python(
        self,
        mock_venv_create,
        mock_execv,
        mock_get_path_to_curr_python,
        mock_state_env_conf_file_data,
        mock_state_client_dir_path_specified,
        mock_state_py_exec_specified,
        mock_state_proto_kernel_abs_path,
        mock_state_target_dst_dir_path,
    ):

        # given:

        mock_state_target_dst_dir_path.return_value = target_dst_dir_path

        mock_state_proto_kernel_abs_path.return_value = state_proto_kernel_abs_path

        mock_state_py_exec_specified.return_value = PythonExecutable.py_exec_unknown

        mock_state_client_dir_path_specified.return_value = mock_client_dir

        mock_state_env_conf_file_data.return_value = {
            ConfConstEnv.field_file_abs_path_python: ConfConstEnv.default_file_abs_path_python,
            ConfConstEnv.field_dir_rel_path_venv: ConfConstEnv.default_dir_rel_path_venv,
        }

        # when:

        self.env_ctx.bootstrap_state(EnvState.state_py_exec_selected.name)

        # then:

        path_to_required_python = ConfConstEnv.default_file_abs_path_python
        mock_execv.assert_called_once_with(
            path_to_required_python,
            [
                path_to_required_python,
                *sys.argv,
                ArgConst.arg_py_exec,
                PythonExecutable.py_exec_required.name,
                ArgConst.arg_proto_kernel_abs_path,
                state_proto_kernel_abs_path,
            ],
        )
        mock_get_path_to_curr_python.assert_called_once()
        mock_venv_create.assert_not_called()
        mock_get_path_to_curr_python.assert_called_once()

    ####################################################################################################################
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_target_dst_dir_path.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_proto_kernel_abs_path.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_specified.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_dir_path_specified.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_env_conf_file_data.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.get_path_to_curr_python",
        # expected path to `python`:
        return_value="/mock_client_dir/venv/bin/python",
    )
    @patch(f"{primer_kernel.__name__}.os.execv")
    @patch(f"{primer_kernel.__name__}.venv.create")
    def test_success_when_path_to_curr_python_is_inside_venv_initially_and_expected(
        self,
        mock_venv_create,
        mock_execv,
        mock_get_path_to_curr_python,
        mock_state_env_conf_file_data,
        mock_state_client_dir_path_specified,
        mock_state_py_exec_specified,
        mock_state_proto_kernel_abs_path,
        mock_state_target_dst_dir_path,
    ):

        # given:

        mock_state_target_dst_dir_path.return_value = target_dst_dir_path

        mock_state_proto_kernel_abs_path.return_value = state_proto_kernel_abs_path

        mock_state_py_exec_specified.return_value = PythonExecutable.py_exec_unknown

        mock_state_client_dir_path_specified.return_value = mock_client_dir

        mock_state_env_conf_file_data.return_value = {
            ConfConstEnv.field_file_abs_path_python: ConfConstEnv.default_file_abs_path_python,
            ConfConstEnv.field_dir_rel_path_venv: ConfConstEnv.default_dir_rel_path_venv,
        }

        # when:

        self.env_ctx.bootstrap_state(EnvState.state_py_exec_selected.name)

        # then:

        mock_venv_create.assert_not_called()
        mock_execv.assert_not_called()
        mock_get_path_to_curr_python.assert_called_once()

    ####################################################################################################################
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_target_dst_dir_path.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_proto_kernel_abs_path.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_specified.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_dir_path_specified.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_env_conf_file_data.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.get_path_to_curr_python",
        return_value=ConfConstEnv.default_file_abs_path_python,
    )
    @patch(f"{primer_kernel.__name__}.os.execv")
    @patch(f"{primer_kernel.__name__}.venv.create")
    def test_success_when_path_to_python_matches_interpreter_and_venv_does_not_exist(
        self,
        mock_venv_create,
        mock_execv,
        mock_get_path_to_curr_python,
        mock_state_env_conf_file_data,
        mock_state_client_dir_path_specified,
        mock_state_py_exec_specified,
        mock_state_proto_kernel_abs_path,
        mock_state_target_dst_dir_path,
    ):

        # given:

        mock_state_target_dst_dir_path.return_value = target_dst_dir_path

        mock_state_proto_kernel_abs_path.return_value = state_proto_kernel_abs_path

        mock_state_py_exec_specified.return_value = PythonExecutable.py_exec_required

        mock_state_client_dir_path_specified.return_value = mock_client_dir

        mock_state_env_conf_file_data.return_value = {
            ConfConstEnv.field_file_abs_path_python: ConfConstEnv.default_file_abs_path_python,
            ConfConstEnv.field_dir_rel_path_venv: ConfConstEnv.default_dir_rel_path_venv,
        }

        # when:

        self.env_ctx.bootstrap_state(EnvState.state_py_exec_selected.name)

        # then:

        path_to_venv = os.path.join(
            mock_client_dir,
            ConfConstEnv.default_dir_rel_path_venv,
        )
        mock_venv_create.assert_called_once_with(
            path_to_venv,
            with_pip=True,
        )
        path_to_venv_python = os.path.join(
            path_to_venv,
            ConfConstGeneral.file_rel_path_venv_python,
        )
        mock_execv.assert_called_once_with(
            path_to_venv_python,
            [
                path_to_venv_python,
                *sys.argv,
                ArgConst.arg_py_exec,
                PythonExecutable.py_exec_venv.name,
                ArgConst.arg_proto_kernel_abs_path,
                state_proto_kernel_abs_path,
            ],
        )
        mock_get_path_to_curr_python.assert_called_once()

    ####################################################################################################################
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_target_dst_dir_path.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_proto_kernel_abs_path.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_specified.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_dir_path_specified.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_env_conf_file_data.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.get_path_to_curr_python",
        return_value=ConfConstEnv.default_file_abs_path_python,
    )
    @patch(f"{primer_kernel.__name__}.os.execv")
    @patch(f"{primer_kernel.__name__}.venv.create")
    def test_success_when_path_to_python_differs_from_path_to_curr_python_and_execv_called_for_required_python(
        self,
        mock_venv_create,
        mock_execv,
        mock_get_path_to_curr_python,
        mock_state_env_conf_file_data,
        mock_state_client_dir_path_specified,
        mock_state_py_exec_specified,
        mock_state_proto_kernel_abs_path,
        mock_state_target_dst_dir_path,
    ):

        # given:

        mock_state_target_dst_dir_path.return_value = target_dst_dir_path

        mock_state_proto_kernel_abs_path.return_value = state_proto_kernel_abs_path

        mock_state_py_exec_specified.return_value = PythonExecutable.py_exec_unknown

        mock_state_client_dir_path_specified.return_value = mock_client_dir

        mock_state_env_conf_file_data.return_value = {
            ConfConstEnv.field_file_abs_path_python: non_default_file_abs_path_python,
            ConfConstEnv.field_dir_rel_path_venv: ConfConstEnv.default_dir_rel_path_venv,
        }

        # when:

        self.env_ctx.bootstrap_state(EnvState.state_py_exec_selected.name)

        # then:

        mock_venv_create.assert_not_called()
        mock_execv.assert_called_once_with(
            non_default_file_abs_path_python,
            [
                non_default_file_abs_path_python,
                *sys.argv,
                ArgConst.arg_py_exec,
                PythonExecutable.py_exec_required.name,
                ArgConst.arg_proto_kernel_abs_path,
                state_proto_kernel_abs_path,
            ],
        )
        mock_get_path_to_curr_python.assert_called_once()

    ####################################################################################################################
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_target_dst_dir_path.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_proto_kernel_abs_path.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_specified.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_dir_path_specified.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_env_conf_file_data.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.get_path_to_curr_python",
        return_value=ConfConstEnv.default_file_abs_path_python,
    )
    @patch(f"{primer_kernel.__name__}.os.execv")
    @patch(f"{primer_kernel.__name__}.venv.create")
    def test_success_when_path_to_python_matches_path_to_curr_python_and_execv_is_called_for_venv_python(
        self,
        mock_venv_create,
        mock_execv,
        mock_get_path_to_curr_python,
        mock_state_env_conf_file_data,
        mock_state_client_dir_path_specified,
        mock_state_py_exec_specified,
        mock_state_proto_kernel_abs_path,
        mock_state_target_dst_dir_path,
    ):

        # given:

        mock_state_target_dst_dir_path.return_value = target_dst_dir_path

        mock_state_proto_kernel_abs_path.return_value = state_proto_kernel_abs_path

        mock_state_py_exec_specified.return_value = PythonExecutable.py_exec_unknown

        mock_state_client_dir_path_specified.return_value = mock_client_dir

        mock_state_env_conf_file_data.return_value = {
            ConfConstEnv.field_file_abs_path_python: ConfConstEnv.default_file_abs_path_python,
            ConfConstEnv.field_dir_rel_path_venv: ConfConstEnv.default_dir_rel_path_venv,
        }

        # when:

        self.env_ctx.bootstrap_state(EnvState.state_py_exec_selected.name)

        # then:

        path_to_venv = os.path.join(
            mock_client_dir,
            ConfConstEnv.default_dir_rel_path_venv,
        )
        mock_venv_create.assert_called_once_with(
            path_to_venv,
            with_pip=True,
        )
        path_to_venv_python = os.path.join(
            path_to_venv,
            ConfConstGeneral.file_rel_path_venv_python,
        )
        mock_execv.assert_called_once_with(
            path_to_venv_python,
            [
                path_to_venv_python,
                *sys.argv,
                ArgConst.arg_py_exec,
                PythonExecutable.py_exec_venv.name,
                ArgConst.arg_proto_kernel_abs_path,
                state_proto_kernel_abs_path,
            ],
        )
        mock_get_path_to_curr_python.assert_called_once()

    ####################################################################################################################
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_target_dst_dir_path.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_proto_kernel_abs_path.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_specified.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_dir_path_specified.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_env_conf_file_data.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.get_path_to_curr_python",
        return_value=non_default_file_abs_path_python,
    )
    @patch(f"{primer_kernel.__name__}.os.execv")
    @patch(f"{primer_kernel.__name__}.venv.create")
    def test_success_when_path_to_python_is_not_inside_existing_venv(
        self,
        mock_venv_create,
        mock_execv,
        mock_get_path_to_curr_python,
        mock_state_env_conf_file_data,
        mock_state_client_dir_path_specified,
        mock_state_py_exec_specified,
        mock_state_proto_kernel_abs_path,
        mock_state_target_dst_dir_path,
    ):

        # given:

        mock_state_target_dst_dir_path.return_value = target_dst_dir_path

        mock_state_proto_kernel_abs_path.return_value = state_proto_kernel_abs_path

        mock_state_py_exec_specified.return_value = PythonExecutable.py_exec_required

        mock_state_client_dir_path_specified.return_value = mock_client_dir

        mock_state_env_conf_file_data.return_value = {
            ConfConstEnv.field_file_abs_path_python: non_default_file_abs_path_python,
            ConfConstEnv.field_dir_rel_path_venv: non_default_dir_abs_path_venv,
        }

        # when:

        self.env_ctx.bootstrap_state(EnvState.state_py_exec_selected.name)

        # then:

        mock_venv_create.assert_called_once_with(
            non_default_dir_abs_path_venv,
            with_pip=True,
        )

        path_to_venv_python = os.path.join(
            non_default_dir_abs_path_venv,
            ConfConstGeneral.file_rel_path_venv_python,
        )
        mock_execv.assert_called_once_with(
            path_to_venv_python,
            [
                path_to_venv_python,
                *sys.argv,
                ArgConst.arg_py_exec,
                PythonExecutable.py_exec_venv.name,
                ArgConst.arg_proto_kernel_abs_path,
                state_proto_kernel_abs_path,
            ],
        )

        mock_get_path_to_curr_python.assert_called_once()

    ####################################################################################################################
