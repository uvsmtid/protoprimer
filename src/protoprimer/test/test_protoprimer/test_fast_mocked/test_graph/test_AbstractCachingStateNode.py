from unittest.mock import MagicMock

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    AbstractCachingStateNode,
)


def test_relationship():
    assert_test_module_name_embeds_str(AbstractCachingStateNode.__name__)


def test_caching():
    # given:
    mock_env_ctx = MagicMock()
    state_node = AbstractCachingStateNode(mock_env_ctx, [], "my_state")
    state_node._eval_state_once = MagicMock(return_value="my_value")

    # when:
    result1 = state_node.eval_own_state()
    result2 = state_node.eval_own_state()

    # then:
    assert result1 == "my_value"
    assert result2 == "my_value"
    state_node._eval_state_once.assert_called_once()


def test_eval_parents():
    # given:
    mock_env_ctx = MagicMock()
    parent_states = ["parent1"]
    state_node = AbstractCachingStateNode(mock_env_ctx, parent_states, "my_state")
    state_node._eval_state_once = MagicMock(return_value="my_value")

    # when:
    state_node.eval_own_state()

    # then:
    mock_env_ctx.state_graph.eval_state.assert_called_once_with("parent1")
    state_node._eval_state_once.assert_called_once()


def test_no_eval_parents():
    # given:
    mock_env_ctx = MagicMock()
    parent_states = ["parent1"]
    state_node = AbstractCachingStateNode(
        mock_env_ctx, parent_states, "my_state", auto_bootstrap_parents=False
    )
    state_node._eval_state_once = MagicMock(return_value="my_value")

    # when:
    state_node.eval_own_state()

    # then:
    mock_env_ctx.state_graph.eval_state.assert_not_called()
    state_node._eval_state_once.assert_called_once()


def test_eval_state_once_raises_not_implemented_error():
    # given:
    state_node = AbstractCachingStateNode(MagicMock(), [], "my_state")

    # when/then:
    with pytest.raises(NotImplementedError):
        state_node._eval_state_once()
