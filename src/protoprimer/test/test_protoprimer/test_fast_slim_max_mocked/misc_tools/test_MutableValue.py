from unittest.mock import MagicMock

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    MutableValue,
    StateNode,
)


def test_relationship():
    assert_test_module_name_embeds_str(MutableValue.__name__)


def test_init():
    # given:
    mutable_value = MutableValue("my_state")

    # then:
    assert mutable_value.state_name == "my_state"
    assert mutable_value.curr_value is None


def test_get_curr_value():
    # given:
    mutable_value = MutableValue("my_state")
    mock_state_node = MagicMock(spec=StateNode)
    mock_state_node.eval_parent_state.return_value = "initial_value"

    # when:
    result = mutable_value.get_curr_value(mock_state_node)

    # then:
    assert result == "initial_value"
    mock_state_node.eval_parent_state.assert_called_once_with("my_state")
    assert mutable_value.curr_value == "initial_value"


def test_get_curr_value_already_set():
    # given:
    mutable_value = MutableValue("my_state")
    mutable_value.curr_value = "already_set"
    mock_state_node = MagicMock(spec=StateNode)
    mock_state_node.eval_parent_state.return_value = "initial_value"

    # when:
    result = mutable_value.get_curr_value(mock_state_node)

    # then:
    assert result == "already_set"
    mock_state_node.eval_parent_state.assert_called_once_with("my_state")


def test_set_curr_value():
    # given:
    mutable_value = MutableValue("my_state")
    mutable_value.curr_value = "initial_value"
    mock_state_node = MagicMock(spec=StateNode)

    # when:
    mutable_value.set_curr_value(mock_state_node, "new_value")

    # then:
    assert mutable_value.curr_value == "new_value"


def test_set_curr_value_not_initialized():
    # given:
    mutable_value = MutableValue("my_state")
    mock_state_node = MagicMock(spec=StateNode)

    # when/then:
    with pytest.raises(AssertionError):
        mutable_value.set_curr_value(mock_state_node, "new_value")
