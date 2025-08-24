import json
import os
from unittest.mock import patch

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_input_proto_conf_primer_file_abs_path_eval_finalized,
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
        assert_test_module_name_embeds_str(EnvState.state_proto_conf_file_data.name)

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_proto_conf_primer_file_abs_path_eval_finalized.__name__}._eval_state_once"
    )
    def test_conf_file_exists(
        self,
        mock_state_input_proto_conf_primer_file_abs_path_eval_finalized,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_proto_conf_file_data,
        )

        mock_file_path = "/mock/path/to/file"
        mock_state_input_proto_conf_primer_file_abs_path_eval_finalized.return_value = (
            mock_file_path
        )
        self.fs.create_file(mock_file_path, contents=json.dumps({"test": "data"}))

        # when:

        state_value = self.env_ctx.state_graph.eval_state(
            EnvState.state_proto_conf_file_data.name
        )

        # then:

        self.assertEqual(state_value, {"test": "data"})

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_input_proto_conf_primer_file_abs_path_eval_finalized.__name__}._eval_state_once"
    )
    def test_conf_file_missing(
        self,
        mock_state_input_proto_conf_primer_file_abs_path_eval_finalized,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_proto_conf_file_data,
        )

        mock_file_path = "/mock/path/to/file"
        self.fs.create_dir("/mock/path/to")
        mock_state_input_proto_conf_primer_file_abs_path_eval_finalized.return_value = (
            mock_file_path
        )

        # when:

        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.state_graph.eval_state(
                EnvState.state_proto_conf_file_data.name
            )

        # then:

        self.assertIn("does not exists", str(ctx.exception))
