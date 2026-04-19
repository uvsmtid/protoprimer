from unittest.mock import patch

from local_test.mock_verifier import assert_parent_factories_mocked
from local_test.name_assertion import assert_test_module_name_embeds_str
from neoprimer import conf_renderer
from neoprimer.cmd_eval_conf import customize_env_context
from neoprimer.conf_renderer import (
    Bootstrapper_state_all_conf_data_rendered,
    Bootstrapper_state_derived_conf_data_loaded_rendered,
    RendererState,
)


def test_relationship():
    assert_test_module_name_embeds_str(Bootstrapper_state_all_conf_data_rendered.__name__)


@patch(f"{conf_renderer.__name__}.{Bootstrapper_state_derived_conf_data_loaded_rendered.__name__}.create_state_node")
def test_state_evaluation(
    mock_create_state_derived_conf_data_loaded_rendered,
):

    # given:

    env_ctx = customize_env_context()

    assert_parent_factories_mocked(
        env_ctx,
        Bootstrapper_state_all_conf_data_rendered._state_name(),
    )

    # when:

    result = env_ctx.state_graph.eval_state(
        Bootstrapper_state_all_conf_data_rendered._state_name(),
    )

    # then:

    assert result == 0
    mock_create_state_derived_conf_data_loaded_rendered.return_value.eval_own_state.assert_called_once()
