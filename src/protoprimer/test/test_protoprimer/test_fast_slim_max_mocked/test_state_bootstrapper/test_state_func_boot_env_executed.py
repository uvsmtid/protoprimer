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
    Factory_state_input_final_state_eval_finalized,
    Factory_state_input_sub_command_arg_loaded,
    Bootstrapper_state_input_stderr_log_level_handler_configured,
    EntryFunc,
    EnvContext,
    EnvState,
    SubCommand,
)


@pytest.fixture
def env_ctx():
    ctx = EnvContext()
    ctx._entry_func = EntryFunc.func_boot_env
    return ctx


def test_relationship():
    assert_test_module_name_embeds_str(EnvState.state_func_boot_env_executed.name)


@patch(f"{primer_kernel.__name__}.{Factory_state_input_final_state_eval_finalized.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_handler_configured.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Factory_state_input_sub_command_arg_loaded.__name__}.create_state_node")
def test_sub_command_boot(
    mock_state_input_sub_command_arg_loaded,
    mock_state_input_stderr_log_level_handler_configured,
    mock_state_input_final_state_eval_finalized,
    env_ctx,
):
    # given:

    assert_parent_factories_mocked(
        env_ctx,
        EnvState.state_func_boot_env_executed.name,
    )

    mock_state_input_sub_command_arg_loaded.return_value.eval_own_state.return_value = SubCommand.command_boot
    mock_state_input_final_state_eval_finalized.return_value.eval_own_state.return_value = "mock_final_state"

    mock_state_node = MagicMock()
    mock_state_node.state_name = "mock_final_state"
    mock_state_node.eval_own_state.return_value = 0
    env_ctx.state_graph.state_nodes["mock_final_state"] = mock_state_node

    # when/then:

    with pytest.raises(SystemExit) as exc_info:
        env_ctx.state_graph.eval_state(EnvState.state_func_boot_env_executed.name)

    assert exc_info.value.code == 0


@patch(f"{primer_kernel.__name__}.{Factory_state_input_final_state_eval_finalized.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_handler_configured.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Factory_state_input_sub_command_arg_loaded.__name__}.create_state_node")
def test_sub_command_none(
    mock_state_input_sub_command_arg_loaded,
    mock_state_input_stderr_log_level_handler_configured,
    mock_state_input_final_state_eval_finalized,
    env_ctx,
):
    # given:

    assert_parent_factories_mocked(
        env_ctx,
        EnvState.state_func_boot_env_executed.name,
    )

    mock_state_input_sub_command_arg_loaded.return_value.eval_own_state.return_value = None
    mock_state_input_final_state_eval_finalized.return_value.eval_own_state.return_value = "mock_final_state"

    mock_state_node = MagicMock()
    env_ctx.state_graph.state_nodes["mock_final_state"] = mock_state_node

    # when/then:
    with pytest.raises(ValueError, match="sub command is not defined"):
        env_ctx.state_graph.eval_state(EnvState.state_func_boot_env_executed.name)


@patch(f"{primer_kernel.__name__}.{Factory_state_input_final_state_eval_finalized.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_handler_configured.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Factory_state_input_sub_command_arg_loaded.__name__}.create_state_node")
def test_sub_command_invalid(
    mock_state_input_sub_command_arg_loaded,
    mock_state_input_stderr_log_level_handler_configured,
    mock_state_input_final_state_eval_finalized,
    env_ctx,
):
    # given:

    assert_parent_factories_mocked(
        env_ctx,
        EnvState.state_func_boot_env_executed.name,
    )

    mock_state_input_sub_command_arg_loaded.return_value.eval_own_state.return_value = "invalid_sub_command"
    mock_state_input_final_state_eval_finalized.return_value.eval_own_state.return_value = "mock_final_state"

    mock_state_node = MagicMock()
    env_ctx.state_graph.state_nodes["mock_final_state"] = mock_state_node

    # when/then:
    with pytest.raises(ValueError, match="cannot handle sub command"):
        env_ctx.state_graph.eval_state(EnvState.state_func_boot_env_executed.name)
