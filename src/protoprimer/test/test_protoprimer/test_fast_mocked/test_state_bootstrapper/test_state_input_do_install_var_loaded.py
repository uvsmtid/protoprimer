from unittest.mock import (
    patch,
)

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.line_number import line_no
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_input_do_install_var_loaded,
    EnvContext,
    EnvState,
    EnvVar,
    ConfConstInput,
)
from test_protoprimer.test_fast_mocked.misc_tools.mock_verifier import (
    assert_parent_states_mocked,
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
        "os.environ",
        {},
        clear=True,
    )
    def test_default_case(
        self,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_input_do_install_var_loaded,
        )
        # when:
        actual = self.env_ctx.state_graph.eval_state(
            EnvState.state_input_do_install_var_loaded.name
        )
        # then:
        self.assertEqual(
            primer_kernel.str2bool(ConfConstInput.default_PROTOPRIMER_DO_INSTALL),
            actual,
        )

    @patch.dict(
        "os.environ",
        {EnvVar.evn_var_PROTOPRIMER_DO_INSTALL.value: "True"},
        clear=True,
    )
    def test_explicitly_true(
        self,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_input_do_install_var_loaded,
        )
        # when:
        actual = self.env_ctx.state_graph.eval_state(
            EnvState.state_input_do_install_var_loaded.name
        )
        # then:
        self.assertEqual(True, actual)

    @patch.dict(
        "os.environ",
        {EnvVar.evn_var_PROTOPRIMER_DO_INSTALL.value: "False"},
        clear=True,
    )
    def test_explicitly_false(
        self,
    ):
        # given:
        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_input_do_install_var_loaded,
        )
        # when:
        actual = self.env_ctx.state_graph.eval_state(
            EnvState.state_input_do_install_var_loaded.name
        )
        # then:
        self.assertEqual(False, actual)
