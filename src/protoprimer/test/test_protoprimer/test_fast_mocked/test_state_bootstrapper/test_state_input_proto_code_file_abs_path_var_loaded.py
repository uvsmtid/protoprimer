import os
from unittest.mock import (
    patch,
)

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.mock_verifier import (
    assert_parent_states_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    EnvContext,
    EnvState,
    EnvVar,
)


# noinspection PyPep8Naming
class ThisTestClass(BasePyfakefsTestClass):

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = EnvContext()

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_str(
            EnvState.state_input_proto_code_file_abs_path_var_loaded.name
        )

    @patch.dict(
        f"{os.__name__}.environ",
        {},
        clear=True,
    )
    def test_success_when_proto_code_file_abs_path_is_not_set(
        self,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_input_proto_code_file_abs_path_var_loaded.name,
        )
        # when:
        state_value = self.env_ctx.state_graph.eval_state(
            EnvState.state_input_proto_code_file_abs_path_var_loaded.name
        )
        # then:
        self.assertIsNone(state_value)

    @patch.dict(
        f"{os.__name__}.environ",
        {EnvVar.var_PROTOPRIMER_PROTO_CODE.value: "relative/path"},
        clear=True,
    )
    def test_failure_when_proto_code_file_abs_path_is_not_abs(
        self,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_input_proto_code_file_abs_path_var_loaded.name,
        )
        # when/then:
        with self.assertRaises(AssertionError):
            self.env_ctx.state_graph.eval_state(
                EnvState.state_input_proto_code_file_abs_path_var_loaded.name
            )

    @patch.dict(
        f"{os.__name__}.environ",
        {EnvVar.var_PROTOPRIMER_PROTO_CODE.value: "/abs/path/not_exist"},
        clear=True,
    )
    def test_failure_when_proto_code_file_abs_path_does_not_exist(
        self,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_input_proto_code_file_abs_path_var_loaded.name,
        )
        # when/then:
        with self.assertRaises(AssertionError):
            self.env_ctx.state_graph.eval_state(
                EnvState.state_input_proto_code_file_abs_path_var_loaded.name
            )

    @patch.dict(
        f"{os.__name__}.environ",
        {EnvVar.var_PROTOPRIMER_PROTO_CODE.value: "/abs/path/exists"},
        clear=True,
    )
    def test_success_when_proto_code_file_abs_path_is_set_and_exists(
        self,
    ):
        # given:
        self.fs.create_file("/abs/path/exists")
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_input_proto_code_file_abs_path_var_loaded.name,
        )
        # when:
        state_value = self.env_ctx.state_graph.eval_state(
            EnvState.state_input_proto_code_file_abs_path_var_loaded.name
        )
        # then:
        self.assertEqual("/abs/path/exists", state_value)
