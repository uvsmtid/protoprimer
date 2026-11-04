from unittest.mock import patch

from local_test.mock_verifier import assert_parent_factories_mocked
from local_test.name_assertion import assert_test_module_name_embeds_str
from metaprimer import conf_renderer
from metaprimer.conf_renderer import customize_env_context
from metaprimer.conf_renderer import (
    _Node_state_all_conf_data_rendered,
    _Node_state_derived_conf_data_loaded_rendered,
    RendererState,
)


def test_relationship():
    assert_test_module_name_embeds_str(_Node_state_all_conf_data_rendered.__name__)


@patch(f"{conf_renderer.__name__}.{_Node_state_derived_conf_data_loaded_rendered.__name__}.create_state_node")
def test_state_evaluation(
    mock_create_state_derived_conf_data_loaded_rendered,
):

    # given:

    env_ctx = customize_env_context()

    assert_parent_factories_mocked(
        env_ctx,
        _Node_state_all_conf_data_rendered._state_name(),
    )

    # when:

    result = env_ctx.eval_state(
        _Node_state_all_conf_data_rendered._state_name(),
    )

    # then:

    assert result == 0
    mock_create_state_derived_conf_data_loaded_rendered.return_value.eval_own_state.assert_called_once()
