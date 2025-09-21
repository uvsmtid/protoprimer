import os
import sys
from unittest.mock import patch

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.name_assertion import assert_test_func_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    SyntaxArg,
    Bootstrapper_state_input_proto_code_file_abs_path_eval_finalized,
    ConfConstClient,
    ConfConstEnv,
    ConfConstGeneral,
    ConfConstInput,
    ConfConstPrimer,
    ConfField,
    main,
    PythonExecutable,
    write_json_file,
)


class ThisTestClass(BasePyfakefsTestClass):

    def setUp(self):
        self.setUpPyfakefs()

    @patch(
        f"{primer_kernel.__name__}.get_default_start_id", return_value="mock_start_id"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_proto_code_file_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    @patch(f"{primer_kernel.__name__}.os.execv")
    def test_prime_switches_from_py_exec_unknown(
        self,
        mock_execv,
        mock_state_input_proto_code_file_abs_path_eval_finalized,
        mock_get_default_start_id,
    ):
        assert_test_func_name_embeds_str(PythonExecutable.py_exec_unknown.name)

        # given:

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        default_env_dir_rel_path = os.path.join(
            "dst_env_conf",
            "default_env",
        )
        self.fs.create_dir(default_env_dir_rel_path)
        self.fs.create_dir(
            os.path.dirname(ConfConstPrimer.default_client_conf_file_rel_path)
        )

        primer_conf_data = {
            ConfField.field_primer_ref_root_dir_rel_path.value: ".",
            ConfField.field_primer_conf_client_file_rel_path.value: ConfConstPrimer.default_client_conf_file_rel_path,
        }
        write_json_file(
            os.path.join(
                mock_client_dir,
                ConfConstInput.default_file_basename_conf_primer,
            ),
            primer_conf_data,
        )

        client_conf_data = {
            ConfField.field_client_link_name_dir_rel_path.value: ConfConstClient.default_dir_rel_path_leap_env_link_name,
            ConfField.field_client_default_env_dir_rel_path.value: default_env_dir_rel_path,
        }
        write_json_file(
            os.path.join(
                mock_client_dir,
                ConfConstPrimer.default_client_conf_file_rel_path,
            ),
            client_conf_data,
        )

        env_conf_data = {
            ConfField.field_env_local_python_file_abs_path.value: ConfConstEnv.default_file_abs_path_python,
            ConfField.field_env_local_venv_dir_rel_path.value: ConfConstEnv.default_dir_rel_path_venv,
            ConfField.field_env_project_descriptors.value: ConfConstEnv.default_project_descriptors,
        }
        write_json_file(
            os.path.join(
                mock_client_dir,
                default_env_dir_rel_path,
                ConfConstClient.default_file_basename_leap_env,
            ),
            env_conf_data,
        )

        state_input_proto_code_file_abs_path_eval_finalized = os.path.join(
            mock_client_dir,
            ConfConstGeneral.default_proto_code_basename,
        )
        self.fs.create_file(state_input_proto_code_file_abs_path_eval_finalized)
        mock_state_input_proto_code_file_abs_path_eval_finalized.return_value = (
            state_input_proto_code_file_abs_path_eval_finalized
        )

        script_basename = os.path.basename(os.path.abspath(__file__))

        test_args = [
            script_basename,
        ]

        execv_args = [
            ConfConstEnv.default_file_abs_path_python,
            *test_args,
            SyntaxArg.arg_py_exec,
            PythonExecutable.py_exec_required.name,
            SyntaxArg.arg_start_id,
            "mock_start_id",
            SyntaxArg.arg_proto_code_abs_file_path,
            state_input_proto_code_file_abs_path_eval_finalized,
        ]

        def execv_side_effect_with_exception(
            exec_path,
            argv,
        ):
            raise AssertionError(argv)

        mock_execv.side_effect = execv_side_effect_with_exception

        # when:

        with patch.object(sys, "argv", test_args):
            # this assertion comes from `mock_execv`:
            with self.assertRaises(AssertionError) as cm:
                main()
            self.assertEqual(execv_args, cm.exception.args[0])

        # then:

        mock_execv.assert_called_once_with(
            ConfConstEnv.default_file_abs_path_python,
            execv_args,
        )
