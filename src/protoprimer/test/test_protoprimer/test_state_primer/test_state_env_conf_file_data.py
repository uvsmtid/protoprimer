import json
import os
from unittest.mock import patch

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_client_conf_env_file_abs_path_eval_finalized,
    ConfConstEnv,
    ConfField,
    EnvContext,
    EnvState,
)
from test_protoprimer.misc_tools.mock_verifier import assert_parent_states_mocked


# noinspection PyPep8Naming
class ThisTestClass(BasePyfakefsTestClass):

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = EnvContext()

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_str(EnvState.state_env_conf_file_data.name)

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_env_file_abs_path_eval_finalized.__name__}._eval_state_once"
    )
    def test_state_env_conf_file_data_exists(
        self,
        mock_state_client_conf_env_file_abs_path_eval_finalized,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_env_conf_file_data,
        )

        mock_conf_file = "/mock/path/to/env_conf.json"
        mock_state_client_conf_env_file_abs_path_eval_finalized.return_value = (
            mock_conf_file
        )

        mock_data = {"test": "data"}
        self.fs.create_file(mock_conf_file, contents=json.dumps(mock_data))

        # when:

        state_value = self.env_ctx.state_graph.eval_state(
            EnvState.state_env_conf_file_data.name
        )

        # then:

        self.assertEqual(state_value, mock_data)

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_env_file_abs_path_eval_finalized.__name__}._eval_state_once"
    )
    def test_state_env_conf_file_data_missing(
        self,
        mock_state_client_conf_env_file_abs_path_eval_finalized,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_env_conf_file_data,
        )

        mock_conf_file = "/mock/path/to/env_conf.json"
        self.fs.create_dir("/mock/path/to")
        mock_state_client_conf_env_file_abs_path_eval_finalized.return_value = (
            mock_conf_file
        )

        self.assertFalse(os.path.exists(mock_conf_file))

        # when:

        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.state_graph.eval_state(EnvState.state_env_conf_file_data.name)

        # then:

        self.assertIn("does not exists", str(ctx.exception))
