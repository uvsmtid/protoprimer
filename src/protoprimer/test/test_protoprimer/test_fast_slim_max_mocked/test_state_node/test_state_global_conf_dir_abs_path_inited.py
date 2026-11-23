from unittest.mock import patch

from local_repo.cmd_prime_env import customize_env_context
from local_test.base_test_class import BasePyfakefsTestClass
from local_test.mock_verifier import (
    assert_parent_factories_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from local_test.path_helper import abs_path
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    _Node_state_primer_conf_file_data_loaded,
    _Node_state_ref_root_dir_abs_path_inited,
    ConfField,
    _EnvState,
)


# noinspection PyPep8Naming
class ThisTestClass(BasePyfakefsTestClass):

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = customize_env_context()

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_str(_EnvState.state_global_conf_dir_abs_path_inited.name)

    @patch(f"{primer_kernel.__name__}.{_Node_state_primer_conf_file_data_loaded.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.create_state_node")
    def test_ref_root_when_field_is_not_configured(
        self,
        mock_state_ref_root_dir_abs_path_inited,
        mock_state_primer_conf_file_data_loaded,
    ):
        # given:
        assert_parent_factories_mocked(
            self.env_ctx,
            _EnvState.state_global_conf_dir_abs_path_inited.name,
        )
        mock_state_ref_root_dir_abs_path_inited.return_value.eval_own_state.return_value = abs_path("/mock_ref_root")
        mock_state_primer_conf_file_data_loaded.return_value.eval_own_state.return_value = {}

        # when:
        result = self.env_ctx.eval_state(_EnvState.state_global_conf_dir_abs_path_inited.name)

        # then: no separate global config dir (min leaps shape)
        self.assertEqual(result, abs_path("/mock_ref_root"))

    @patch(f"{primer_kernel.__name__}.{_Node_state_primer_conf_file_data_loaded.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.create_state_node")
    def test_configured_dir_is_relative_to_ref_root(
        self,
        mock_state_ref_root_dir_abs_path_inited,
        mock_state_primer_conf_file_data_loaded,
    ):
        # given:
        assert_parent_factories_mocked(
            self.env_ctx,
            _EnvState.state_global_conf_dir_abs_path_inited.name,
        )
        mock_state_ref_root_dir_abs_path_inited.return_value.eval_own_state.return_value = abs_path("/mock_ref_root")
        mock_state_primer_conf_file_data_loaded.return_value.eval_own_state.return_value = {ConfField.field_global_conf_dir_rel_path.value: "gconf"}

        # when:
        result = self.env_ctx.eval_state(_EnvState.state_global_conf_dir_abs_path_inited.name)

        # then:
        self.assertEqual(result, abs_path("/mock_ref_root/gconf"))
