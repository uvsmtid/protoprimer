from unittest.mock import patch

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.mock_verifier import (
    assert_parent_states_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_args_parsed,
    EnvContext,
    EnvState,
    WizardStage,
)


# noinspection PyPep8Naming
class ThisTestClass(BasePyfakefsTestClass):

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = EnvContext()

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_str(
            EnvState.state_input_wizard_stage_arg_loaded.name
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    def test_default_wizard_stage(
        self,
        mock_state_args_parsed,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_input_wizard_stage_arg_loaded.name,
        )

        mock_state_args_parsed.return_value = (
            primer_kernel.init_arg_parser().parse_args([])
        )

        # when:

        state_input_wizard_stage_arg_loaded: WizardStage = (
            self.env_ctx.state_graph.eval_state(
                EnvState.state_input_wizard_stage_arg_loaded.name
            )
        )

        # then:

        self.assertEqual(
            state_input_wizard_stage_arg_loaded,
            WizardStage.wizard_started,
        )
