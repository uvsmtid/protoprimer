import os
import sys
from unittest import (
    skip,
)
from unittest.mock import patch

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.name_assertion import assert_test_func_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    ArgConst,
    Bootstrapper_state_input_proto_code_dir_abs_path_eval_finalized,
    Bootstrapper_state_input_proto_code_file_abs_path_eval_finalized,
    CommandArg,
    ConfConstEnv,
    ConfConstGeneral,
    ConfConstPrimer,
    main,
    PythonExecutable,
)


class ThisTestClass(BasePyfakefsTestClass):

    def setUp(self):
        self.setUpPyfakefs()

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_proto_code_file_abs_path_eval_finalized.__name__}._bootstrap_once"
    )
    @patch(f"{primer_kernel.__name__}.os.execv")
    def test_bootstrap_succeeds_with_py_exec_unknown(
        self,
        mock_execv,
        mock_state_input_proto_code_file_abs_path_eval_finalized,
    ):
        assert_test_func_name_embeds_str(PythonExecutable.py_exec_unknown.name)

        # given:

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        state_input_proto_code_file_abs_path_eval_finalized = os.path.join(
            mock_client_dir,
            ConfConstGeneral.default_proto_code_basename,
        )
        self.fs.create_file(state_input_proto_code_file_abs_path_eval_finalized)
        mock_state_input_proto_code_file_abs_path_eval_finalized.return_value = (
            state_input_proto_code_file_abs_path_eval_finalized
        )

        script_basename = os.path.basename(os.path.abspath(__file__))

        dst_dir_path = os.path.join(
            "dst_env_conf",
            "default_env",
        )
        self.fs.create_dir(dst_dir_path)

        test_args = [
            script_basename,
            ArgConst.arg_local_env_dir_rel_path,
            dst_dir_path,
            ArgConst.arg_ref_root_dir_rel_path,
            mock_client_dir,
        ]

        execv_args = [
            ConfConstEnv.default_file_abs_path_python,
            *test_args,
            ArgConst.arg_py_exec,
            PythonExecutable.py_exec_required.name,
            ArgConst.arg_proto_code_abs_file_path,
            state_input_proto_code_file_abs_path_eval_finalized,
        ]

        def execv_side_effect_with_exception(exec_path, argv):
            raise AssertionError(argv)

        mock_execv.side_effect = execv_side_effect_with_exception

        # when:

        with patch.object(sys, "argv", test_args):
            with self.assertRaises(AssertionError) as cm:
                main()
            self.assertEqual(execv_args, cm.exception.args[0])

        # then:

        mock_execv.assert_called_once_with(
            ConfConstEnv.default_file_abs_path_python,
            execv_args,
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_proto_code_dir_abs_path_eval_finalized.__name__}._bootstrap_once"
    )
    # TODO: Repurpose, this is not applicable anymore (we allow missing target dst):
    #       For example, assert behaviour when both config and arg provide value but it is different.
    @skip
    def test_bootstrap_proceeds_on_existing_gconf_file_fails_on_missing_target_dst_dir_path(
        self,
        mock_state_script_dir_path,
    ):

        # given:

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        mock_state_script_dir_path.return_value = script_dir
        self.fs.create_dir(script_dir)
        test_args = [
            os.path.basename(primer_kernel.__file__),
            ArgConst.arg_ref_root_dir_rel_path,
            mock_client_dir,
        ]
        self.fs.create_file(
            os.path.join(
                mock_client_dir,
                ConfConstPrimer.default_client_conf_file_rel_path,
            ),
            contents="{}",
        )

        # when/then:

        with patch.object(sys, "argv", test_args):
            with self.assertRaises(AssertionError) as cm:
                main()
            self.assertIn(
                f"`{CommandArg.name_local_env.value}` is not provided",
                str(cm.exception),
            )
