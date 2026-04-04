from unittest.mock import (
    MagicMock,
    patch,
)

import pytest

from local_test.mock_verifier import (
    assert_parent_factories_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_input_final_state_eval_finalized,
    Bootstrapper_state_input_exec_mode_arg_loaded,
    Bootstrapper_state_input_stderr_log_level_eval_finalized,
    EnvContext,
    EnvState,
    ExitCodeReporter,
    ExecMode,
)


@pytest.fixture
def env_ctx():
    return EnvContext()


def test_relationship():
    assert_test_module_name_embeds_str(EnvState.state_exec_mode_executed.name)


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_final_state_eval_finalized.__name__}.create_state_node"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_eval_finalized.__name__}.create_state_node"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_exec_mode_arg_loaded.__name__}.create_state_node"
)
@patch(f"{primer_kernel.__name__}.{ExitCodeReporter.__name__}.execute_strategy")
def test_exec_mode_prime(
    mock_exit_code_reporter_execute_strategy,
    mock_state_input_exec_mode_arg_loaded,
    mock_state_input_stderr_log_level_eval_finalized,
    mock_state_input_final_state_eval_finalized,
    env_ctx,
):
    # given:

    assert_parent_factories_mocked(
        env_ctx,
        EnvState.state_exec_mode_executed.name,
    )

    mock_state_input_exec_mode_arg_loaded.return_value.eval_own_state.return_value = (
        ExecMode.mode_prime
    )
    mock_state_input_stderr_log_level_eval_finalized.return_value.eval_own_state.return_value = (
        0
    )
    mock_state_input_final_state_eval_finalized.return_value.eval_own_state.return_value = (
        "mock_final_state"
    )

    mock_state_node = MagicMock()
    env_ctx.state_graph.state_nodes["mock_final_state"] = mock_state_node

    # when:

    state_value = env_ctx.state_graph.eval_state(
        EnvState.state_exec_mode_executed.name, env_ctx
    )

    # then:

    assert state_value is True
    mock_exit_code_reporter_execute_strategy.assert_called_once_with(mock_state_node)


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_final_state_eval_finalized.__name__}.create_state_node"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_eval_finalized.__name__}.create_state_node"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_exec_mode_arg_loaded.__name__}.create_state_node"
)
def test_exec_mode_none(
    mock_state_input_exec_mode_arg_loaded,
    mock_state_input_stderr_log_level_eval_finalized,
    mock_state_input_final_state_eval_finalized,
    env_ctx,
):
    # given:

    assert_parent_factories_mocked(
        env_ctx,
        EnvState.state_exec_mode_executed.name,
    )

    mock_state_input_exec_mode_arg_loaded.return_value.eval_own_state.return_value = (
        None
    )

    mock_state_input_stderr_log_level_eval_finalized.return_value.eval_own_state.return_value = (
        0
    )
    mock_state_input_final_state_eval_finalized.return_value.eval_own_state.return_value = (
        "mock_final_state"
    )

    mock_state_node = MagicMock()
    env_ctx.state_graph.state_nodes["mock_final_state"] = mock_state_node

    # when/then:
    with pytest.raises(ValueError, match="exec mode is not defined"):
        env_ctx.state_graph.eval_state(EnvState.state_exec_mode_executed.name, env_ctx)


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_final_state_eval_finalized.__name__}.create_state_node"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_eval_finalized.__name__}.create_state_node"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_exec_mode_arg_loaded.__name__}.create_state_node"
)
def test_exec_mode_invalid(
    mock_state_input_exec_mode_arg_loaded,
    mock_state_input_stderr_log_level_eval_finalized,
    mock_state_input_final_state_eval_finalized,
    env_ctx,
):
    # given:

    assert_parent_factories_mocked(
        env_ctx,
        EnvState.state_exec_mode_executed.name,
    )

    mock_state_input_exec_mode_arg_loaded.return_value.eval_own_state.return_value = (
        "invalid_exec_mode"
    )
    mock_state_input_stderr_log_level_eval_finalized.return_value.eval_own_state.return_value = (
        0
    )
    mock_state_input_final_state_eval_finalized.return_value.eval_own_state.return_value = (
        "mock_final_state"
    )

    mock_state_node = MagicMock()
    env_ctx.state_graph.state_nodes["mock_final_state"] = mock_state_node

    # when/then:
    with pytest.raises(ValueError, match="cannot handle exec mode"):
        env_ctx.state_graph.eval_state(EnvState.state_exec_mode_executed.name, env_ctx)
