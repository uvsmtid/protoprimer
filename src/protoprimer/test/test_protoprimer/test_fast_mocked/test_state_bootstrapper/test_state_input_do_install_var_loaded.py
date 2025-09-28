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
    ConfConstInput,
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
            EnvState.state_input_do_install_var_loaded.name
        )

    @patch.dict(
        f"{os.__name__}.environ",
        {},
        clear=True,
    )
    def test_default_case(
        self,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_input_do_install_var_loaded.name,
        )
        # when:
        state_value = self.env_ctx.state_graph.eval_state(
            EnvState.state_input_do_install_var_loaded.name
        )
        # then:
        self.assertEqual(
            primer_kernel.str2bool(ConfConstInput.default_PROTOPRIMER_DO_INSTALL),
            state_value,
        )

    @patch.dict(
        f"{os.__name__}.environ",
        {EnvVar.var_PROTOPRIMER_DO_INSTALL.value: f"{str(True)}"},
        clear=True,
    )
    def test_explicitly_true(
        self,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_input_do_install_var_loaded.name,
        )
        # when:
        state_value = self.env_ctx.state_graph.eval_state(
            EnvState.state_input_do_install_var_loaded.name
        )
        # then:
        self.assertEqual(True, state_value)

    @patch.dict(
        f"{os.__name__}.environ",
        {EnvVar.var_PROTOPRIMER_DO_INSTALL.value: f"{str(False)}"},
        clear=True,
    )
    def test_explicitly_false(
        self,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_input_do_install_var_loaded.name,
        )
        # when:
        state_value = self.env_ctx.state_graph.eval_state(
            EnvState.state_input_do_install_var_loaded.name
        )
        # then:
        self.assertEqual(False, state_value)
