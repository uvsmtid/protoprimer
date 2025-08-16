import json
import os
from unittest.mock import patch

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_input_proto_code_dir_abs_path_eval_finalized,
    Bootstrapper_state_input_proto_conf_primer_file_abs_path_eval_finalized,
    Bootstrapper_state_primer_ref_root_dir_any_path_arg_loaded,
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
        assert_test_module_name_embeds_str(EnvState.state_proto_conf_file_data.name)

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_primer_ref_root_dir_any_path_arg_loaded.__name__}._eval_state_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_proto_code_dir_abs_path_eval_finalized.__name__}._eval_state_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_proto_conf_primer_file_abs_path_eval_finalized.__name__}._eval_state_once"
    )
    def test_conf_file_exists(
        self,
        mock_input_proto_conf_primer_file_abs_path,
        mock_input_proto_code_dir_abs_path,
        mock_primer_ref_root_dir_any_path_arg_loaded,
    ):

        # given:

        mock_file_path = "/mock/path/to/file"
        mock_input_proto_conf_primer_file_abs_path.return_value = mock_file_path
        self.fs.create_file(mock_file_path, contents=json.dumps({"test": "data"}))

        # when:

        state_value = self.env_ctx.state_graph.eval_state(
            EnvState.state_proto_conf_file_data.name
        )

        # then:

        self.assertEqual(state_value, {"test": "data"})

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_primer_ref_root_dir_any_path_arg_loaded.__name__}._eval_state_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_proto_code_dir_abs_path_eval_finalized.__name__}._eval_state_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_proto_conf_primer_file_abs_path_eval_finalized.__name__}._eval_state_once"
    )
    def test_conf_file_missing(
        self,
        mock_input_proto_conf_primer_file_abs_path,
        mock_input_proto_code_dir_abs_path,
        mock_primer_ref_root_dir_any_path_arg_loaded,
    ):

        # given:

        mock_file_path = "/mock/path/to/file"
        self.fs.create_dir("/mock/path/to")
        mock_input_proto_conf_primer_file_abs_path.return_value = mock_file_path
        mock_input_proto_code_dir_abs_path.return_value = "/mock/path/to"
        mock_primer_ref_root_dir_any_path_arg_loaded.return_value = "/mock/ref/root"

        # when:

        state_value = self.env_ctx.state_graph.eval_state(
            EnvState.state_proto_conf_file_data.name
        )

        # then:

        self.assertTrue(os.path.exists(mock_file_path))
        with open(mock_file_path, "r") as mock_file_obj:
            file_data = json.load(mock_file_obj)
        self.assertIn(ConfField.field_primer_ref_root_dir_rel_path.value, file_data)
        self.assertIn(ConfField.field_primer_conf_client_file_rel_path.value, file_data)
        self.assertEqual(state_value, file_data)
