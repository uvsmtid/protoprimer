import json
import os
from logging import WARNING
from unittest.mock import patch

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.mock_verifier import (
    assert_parent_states_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_global_conf_file_abs_path_inited,
    ConfConstPrimer,
    EnvContext,
    EnvState,
)


# noinspection PyPep8Naming
class ThisTestClass(BasePyfakefsTestClass):

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = EnvContext()

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_str(
            EnvState.state_client_conf_file_data_loaded.name
        )

    @patch(
        f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_py_exec_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_run_mode_arg_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_global_conf_file_abs_path_inited.__name__}.eval_own_state"
    )
    def test_state_global_conf_file_abs_path_inited_exists(
        self,
        mock_state_global_conf_file_abs_path_inited,
        mock_state_input_run_mode_arg_loaded,
        mock_state_input_py_exec_var_loaded,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_client_conf_file_data_loaded.name,
        )

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)
        state_global_conf_file_abs_path_inited = os.path.join(
            mock_client_dir,
            ConfConstPrimer.default_client_conf_file_rel_path,
        )
        mock_state_global_conf_file_abs_path_inited.return_value = (
            state_global_conf_file_abs_path_inited
        )
        self.fs.create_file(
            state_global_conf_file_abs_path_inited,
            contents=json.dumps({}),
        )

        # when:

        self.assertTrue(os.path.isfile(state_global_conf_file_abs_path_inited))
        self.env_ctx.state_graph.eval_state(
            EnvState.state_client_conf_file_data_loaded.name
        )

        # then:

        # no exception happens

    @patch(
        f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_py_exec_var_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_input_run_mode_arg_loaded.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_global_conf_file_abs_path_inited.__name__}.eval_own_state"
    )
    def test_state_global_conf_file_abs_path_inited_missing(
        self,
        mock_state_global_conf_file_abs_path_inited,
        mock_state_input_run_mode_arg_loaded,
        mock_state_input_py_exec_var_loaded,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_client_conf_file_data_loaded.name,
        )

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)
        state_global_conf_file_abs_path_inited = os.path.join(
            mock_client_dir,
            ConfConstPrimer.default_client_conf_file_rel_path,
        )
        mock_state_global_conf_file_abs_path_inited.return_value = (
            state_global_conf_file_abs_path_inited
        )

        self.assertFalse(os.path.isfile(state_global_conf_file_abs_path_inited))

        # when:

        with self.assertLogs(primer_kernel.logger, level=WARNING) as log_dst:
            self.env_ctx.state_graph.eval_state(
                EnvState.state_client_conf_file_data_loaded.name
            )

        # then:

        self.assertIn("does not exist", log_dst.output[0])
