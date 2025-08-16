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

        mock_conf_file = "/mock/path/to/env_conf.json"
        self.fs.create_dir("/mock/path/to")
        mock_state_client_conf_env_file_abs_path_eval_finalized.return_value = (
            mock_conf_file
        )

        self.assertFalse(os.path.exists(mock_conf_file))

        # when:

        state_value = self.env_ctx.state_graph.eval_state(
            EnvState.state_env_conf_file_data.name
        )

        # then:

        self.assertTrue(os.path.exists(mock_conf_file))

        expected_data = {
            ConfField.field_env_local_python_file_abs_path.value: ConfConstEnv.default_file_abs_path_python,
            ConfField.field_env_local_venv_dir_rel_path.value: ConfConstEnv.default_dir_rel_path_venv,
            ConfField.field_env_project_descriptors.value: ConfConstEnv.default_project_descriptors,
        }

        with open(mock_conf_file, "r") as f:
            file_data = json.load(f)

        self.assertEqual(file_data, expected_data)
        self.assertEqual(state_value, expected_data)
