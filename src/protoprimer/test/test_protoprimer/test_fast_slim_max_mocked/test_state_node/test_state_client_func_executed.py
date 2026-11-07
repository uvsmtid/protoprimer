from unittest.mock import patch

import pytest

from local_test.mock_verifier import (
    assert_parent_factories_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    _Node_state_command_executed,
    _EnvContext,
    _EnvState,
)


@pytest.fixture
def env_ctx():
    return _EnvContext()


def test_relationship():
    assert_test_module_name_embeds_str(_EnvState.state_client_func_executed.name)


@patch(f"{primer_kernel.__name__}.{_Node_state_command_executed.__name__}.create_state_node")
def test_client_func_return_value_flows_through(
    mock_state_command_executed,
    env_ctx,
):
    # given:
    assert_parent_factories_mocked(
        env_ctx,
        _EnvState.state_client_func_executed.name,
    )
    mock_state_command_executed.return_value.eval_own_state.return_value = 0
    env_ctx._client_func = lambda: 7

    # when:
    state_value = env_ctx.eval_state(_EnvState.state_client_func_executed.name)

    # then:
    assert state_value == 7


@patch(f"{primer_kernel.__name__}.{_Node_state_command_executed.__name__}.create_state_node")
def test_client_func_none_is_coerced_to_zero(
    mock_state_command_executed,
    env_ctx,
):
    # given:
    assert_parent_factories_mocked(
        env_ctx,
        _EnvState.state_client_func_executed.name,
    )
    mock_state_command_executed.return_value.eval_own_state.return_value = 0
    env_ctx._client_func = lambda: None

    # when:
    state_value = env_ctx.eval_state(_EnvState.state_client_func_executed.name)

    # then:
    assert state_value == 0


@patch(f"{primer_kernel.__name__}.{_Node_state_command_executed.__name__}.create_state_node")
def test_client_func_not_set_raises(
    mock_state_command_executed,
    env_ctx,
):
    # given:
    assert_parent_factories_mocked(
        env_ctx,
        _EnvState.state_client_func_executed.name,
    )
    mock_state_command_executed.return_value.eval_own_state.return_value = 0

    # when/then:
    with pytest.raises(AssertionError):
        env_ctx.eval_state(_EnvState.state_client_func_executed.name)
