from logging import WARNING
from unittest.mock import patch

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.mock_verifier import (
    assert_parent_states_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_client_conf_file_data,
    ConfField,
    EnvContext,
    EnvState,
    SyntaxArg,
)


# noinspection PyPep8Naming
class ThisTestClass(BasePyfakefsTestClass):

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = EnvContext()

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_str(
            EnvState.state_client_link_name_dir_rel_path_eval_finalized.name
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data.__name__}.eval_own_state"
    )
    def test_success_when_field_is_present(
        self,
        mock_state_client_conf_file_data,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_client_link_name_dir_rel_path_eval_finalized.name,
        )
        link_name_value = "my_link_name"
        client_conf_file_data = {
            ConfField.field_client_link_name_dir_rel_path.value: link_name_value,
        }
        mock_state_client_conf_file_data.return_value = client_conf_file_data

        # when:
        result = self.env_ctx.state_graph.eval_state(
            EnvState.state_client_link_name_dir_rel_path_eval_finalized.name
        )

        # then:
        self.assertEqual(result, link_name_value)

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data.__name__}.eval_own_state"
    )
    def test_failure_when_field_is_missing(
        self,
        mock_state_client_conf_file_data,
    ):
        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_client_link_name_dir_rel_path_eval_finalized.name,
        )
        mock_state_client_conf_file_data.return_value = {}

        # when:

        with self.assertLogs(primer_kernel.logger, level=WARNING) as log_dst:
            self.env_ctx.state_graph.eval_state(
                EnvState.state_client_link_name_dir_rel_path_eval_finalized.name
            )

        # then:

        self.assertIn(
            f"Field `{ConfField.field_client_link_name_dir_rel_path.value}` is [None] - re-run with [{SyntaxArg.arg_mode_wizard}] to set it.",
            log_dst.output[0],
        )
