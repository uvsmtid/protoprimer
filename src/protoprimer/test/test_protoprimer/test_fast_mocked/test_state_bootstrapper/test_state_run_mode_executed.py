from unittest.mock import (
    MagicMock,
    patch,
)

import pytest

from local_test.mock_verifier import (
    assert_parent_states_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_input_final_state_eval_finalized,
    Bootstrapper_state_input_run_mode_arg_loaded,
    Bootstrapper_state_input_stderr_log_level_eval_finalized,
    EnvContext,
    EnvState,
    ExitCodeReporter,
    GraphPrinter,
    RunMode,
    WizardState,
)


@pytest.fixture
def env_ctx():
    return EnvContext()


def test_relationship():
    assert_test_module_name_embeds_str(EnvState.state_run_mode_executed.name)


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_final_state_eval_finalized.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_eval_finalized.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_run_mode_arg_loaded.__name__}.eval_own_state"
)
@patch(f"{primer_kernel.__name__}.{GraphPrinter.__name__}.execute_strategy")
def test_run_mode_graph(
    mock_graph_printer_execute_strategy,
    mock_state_input_run_mode_arg_loaded,
    mock_state_input_stderr_log_level_eval_finalized,
    mock_state_input_final_state_eval_finalized,
    env_ctx,
):
    # given:

    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_run_mode_executed.name,
    )

    mock_state_input_run_mode_arg_loaded.return_value = RunMode.mode_graph
    mock_state_input_stderr_log_level_eval_finalized.return_value = 0
    mock_state_input_final_state_eval_finalized.return_value = "mock_final_state"

    mock_state_node = MagicMock()
    env_ctx.state_graph.state_nodes["mock_final_state"] = mock_state_node

    # when:

    state_value = env_ctx.state_graph.eval_state(EnvState.state_run_mode_executed.name)

    # then:

    assert state_value is True
    mock_graph_printer_execute_strategy.assert_called_once_with(mock_state_node)


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_final_state_eval_finalized.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_eval_finalized.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_run_mode_arg_loaded.__name__}.eval_own_state"
)
@patch(f"{primer_kernel.__name__}.{ExitCodeReporter.__name__}.execute_strategy")
def test_run_mode_prime(
    mock_exit_code_reporter_execute_strategy,
    mock_state_input_run_mode_arg_loaded,
    mock_state_input_stderr_log_level_eval_finalized,
    mock_state_input_final_state_eval_finalized,
    env_ctx,
):
    # given:

    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_run_mode_executed.name,
    )

    mock_state_input_run_mode_arg_loaded.return_value = RunMode.mode_prime
    mock_state_input_stderr_log_level_eval_finalized.return_value = 0
    mock_state_input_final_state_eval_finalized.return_value = "mock_final_state"

    mock_state_node = MagicMock()
    env_ctx.state_graph.state_nodes["mock_final_state"] = mock_state_node

    # when:

    state_value = env_ctx.state_graph.eval_state(EnvState.state_run_mode_executed.name)

    # then:

    assert state_value is True
    mock_exit_code_reporter_execute_strategy.assert_called_once_with(mock_state_node)


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_final_state_eval_finalized.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_eval_finalized.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_run_mode_arg_loaded.__name__}.eval_own_state"
)
@patch(f"{primer_kernel.__name__}.{ExitCodeReporter.__name__}.execute_strategy")
def test_run_mode_wizard(
    mock_exit_code_reporter_execute_strategy,
    mock_state_input_run_mode_arg_loaded,
    mock_state_input_stderr_log_level_eval_finalized,
    mock_state_input_final_state_eval_finalized,
    env_ctx,
):
    # given:

    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_run_mode_executed.name,
    )

    mock_state_input_run_mode_arg_loaded.return_value = RunMode.mode_wizard
    mock_state_input_stderr_log_level_eval_finalized.return_value = 0
    mock_state_input_final_state_eval_finalized.return_value = "mock_final_state"

    mock_state_node = MagicMock()
    env_ctx.state_graph.state_nodes["mock_final_state"] = mock_state_node

    # when:

    state_value = env_ctx.state_graph.eval_state(EnvState.state_run_mode_executed.name)

    # then:

    assert state_value is True
    mock_exit_code_reporter_execute_strategy.assert_called_once_with(mock_state_node)
    # Check that wizard states are registered
    for wizard_state in WizardState:
        assert wizard_state.name in env_ctx.state_graph.state_nodes
        assert isinstance(
            env_ctx.state_graph.state_nodes[wizard_state.name],
            wizard_state.value,
        )
