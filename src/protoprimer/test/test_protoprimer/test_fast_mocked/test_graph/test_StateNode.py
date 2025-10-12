from unittest.mock import MagicMock

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    StateNode,
)


def test_relationship():
    assert_test_module_name_embeds_str(StateNode.__name__)


def test_init():
    # given:
    mock_env_ctx = MagicMock()
    parent_states = ["parent1", "parent2"]
    state_name = "my_state"

    # when:
    state_node = StateNode(mock_env_ctx, parent_states, state_name)

    # then:
    assert state_node.env_ctx == mock_env_ctx
    assert state_node.parent_states == parent_states
    assert state_node.state_name == state_name


def test_get_state_name():
    # given:
    state_name = "my_state"
    state_node = StateNode(MagicMock(), [], state_name)

    # when:
    result = state_node.get_state_name()

    # then:
    assert result == state_name


def test_get_parent_states():
    # given:
    parent_states = ["parent1", "parent2"]
    state_node = StateNode(MagicMock(), parent_states, "my_state")

    # when:
    result = state_node.get_parent_states()

    # then:
    assert result == parent_states


def test_eval_parent_state():
    # given:
    mock_env_ctx = MagicMock()
    mock_env_ctx.state_graph.eval_state.return_value = "parent_value"
    parent_states = ["parent1"]
    state_node = StateNode(mock_env_ctx, parent_states, "my_state")

    # when:
    result = state_node.eval_parent_state("parent1")

    # then:
    assert result == "parent_value"
    mock_env_ctx.state_graph.eval_state.assert_called_once_with("parent1")


def test_eval_parent_state_not_declared():
    # given:
    state_node = StateNode(MagicMock(), [], "my_state")

    # when/then:
    with pytest.raises(AssertionError):
        state_node.eval_parent_state("not_a_parent")


def test_eval_own_state_raises_not_implemented_error():
    # given:
    state_node = StateNode(MagicMock(), [], "my_state")

    # when/then:
    with pytest.raises(NotImplementedError):
        state_node.eval_own_state()
