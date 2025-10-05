import os
from unittest.mock import (
    patch,
)

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.mock_verifier import (
    assert_parent_states_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
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
            EnvState.state_input_start_id_var_loaded.name
        )

    @patch.dict(
        f"{os.__name__}.environ",
        {},
        clear=True,
    )
    @patch(f"{primer_kernel.__name__}.get_default_start_id")
    def test_default_case(
        self,
        mock_get_default_start_id,
    ):
        # given:
        mock_get_default_start_id.return_value = "default_start_id"
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_input_start_id_var_loaded.name,
        )
        # when:
        state_value = self.env_ctx.state_graph.eval_state(
            EnvState.state_input_start_id_var_loaded.name
        )
        # then:
        self.assertEqual(
            "default_start_id",
            state_value,
        )

    @patch.dict(
        f"{os.__name__}.environ",
        {EnvVar.var_PROTOPRIMER_START_ID.value: "explicit_start_id"},
        clear=True,
    )
    def test_explicitly_set(
        self,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_input_start_id_var_loaded.name,
        )
        # when:
        state_value = self.env_ctx.state_graph.eval_state(
            EnvState.state_input_start_id_var_loaded.name
        )
        # then:
        self.assertEqual("explicit_start_id", state_value)
