import json
import os
from unittest.mock import patch

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_primer_conf_client_file_abs_path_eval_finalized,
    Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized,
    ConfConstClient,
    ConfConstPrimer,
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
        assert_test_module_name_embeds_str(EnvState.state_client_conf_file_data.name)

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized.__name__}._eval_state_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_primer_conf_client_file_abs_path_eval_finalized.__name__}._eval_state_once"
    )
    def test_state_primer_conf_client_file_abs_path_eval_finalized_exists(
        self,
        mock_state_primer_conf_client_file_abs_path_eval_finalized,
        mock_state_primer_ref_root_dir_abs_path_eval_finalized,
    ):

        # given:

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)
        mock_state_primer_ref_root_dir_abs_path_eval_finalized.return_value = (
            mock_client_dir
        )
        state_primer_conf_client_file_abs_path_eval_finalized = os.path.join(
            mock_client_dir,
            ConfConstPrimer.default_client_conf_file_rel_path,
        )
        mock_state_primer_conf_client_file_abs_path_eval_finalized.return_value = (
            state_primer_conf_client_file_abs_path_eval_finalized
        )
        self.fs.create_file(
            state_primer_conf_client_file_abs_path_eval_finalized,
            contents=json.dumps({}),
        )

        # when:

        self.assertTrue(
            os.path.isfile(state_primer_conf_client_file_abs_path_eval_finalized)
        )
        self.env_ctx.state_graph.eval_state(EnvState.state_client_conf_file_data.name)

        # then:

        # no exception happens

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized.__name__}._eval_state_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_primer_conf_client_file_abs_path_eval_finalized.__name__}._eval_state_once"
    )
    def test_state_primer_conf_client_file_abs_path_eval_finalized_missing(
        self,
        mock_state_primer_conf_client_file_abs_path_eval_finalized,
        mock_state_primer_ref_root_dir_abs_path_eval_finalized,
    ):

        # given:

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)
        mock_state_primer_ref_root_dir_abs_path_eval_finalized.return_value = (
            mock_client_dir
        )
        state_primer_conf_client_file_abs_path_eval_finalized = os.path.join(
            mock_client_dir,
            ConfConstPrimer.default_client_conf_file_rel_path,
        )
        mock_state_primer_conf_client_file_abs_path_eval_finalized.return_value = (
            state_primer_conf_client_file_abs_path_eval_finalized
        )

        # when:

        self.assertFalse(
            os.path.isfile(state_primer_conf_client_file_abs_path_eval_finalized)
        )
        state_value = self.env_ctx.state_graph.eval_state(
            EnvState.state_client_conf_file_data.name
        )

        # then:

        # file created:
        self.assertTrue(
            os.path.isfile(state_primer_conf_client_file_abs_path_eval_finalized)
        )

        expected_data = {
            ConfField.field_client_link_name_dir_rel_path.value: ConfConstClient.default_dir_rel_path_leap_env_link_name,
            ConfField.field_client_default_target_dir_rel_path.value: ConfConstClient.default_client_default_target_dir_rel_path,
        }

        with open(state_primer_conf_client_file_abs_path_eval_finalized, "r") as f:
            file_data = json.load(f)

        self.assertEqual(file_data, expected_data)
        self.assertEqual(state_value, expected_data)
