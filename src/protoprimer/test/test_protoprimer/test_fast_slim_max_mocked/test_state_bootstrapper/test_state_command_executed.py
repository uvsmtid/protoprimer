import argparse
import logging
import os
from unittest.mock import (
    patch,
)

import pytest

from local_test.mock_verifier import (
    assert_parent_states_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_args_parsed,
    Bootstrapper_state_default_stderr_log_handler_configured,
    Bootstrapper_state_merged_conf_data_printed,
    Bootstrapper_state_py_exec_updated_proto_code,
    EnvContext,
    EnvState,
    ParsedArg,
    PythonExecutable,
)


@pytest.fixture
def env_ctx():
    return EnvContext()


def test_relationship():
    assert_test_module_name_embeds_str(EnvState.state_command_executed.name)


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_default_stderr_log_handler_configured.__name__}.eval_own_state"
)
@patch(f"{os.__name__}.execv")
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_updated_proto_code.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
)
def test_command_executed(
    mock_state_args_parsed,
    mock_state_py_exec_updated_proto_code,
    mock_os_execv,
    mock_state_default_stderr_log_handler_configured,
    env_ctx,
):
    # given:
    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_command_executed.name,
    )
    mock_state_args_parsed.return_value = argparse.Namespace(
        **{
            ParsedArg.name_command.value: "echo hello",
        }
    )
    mock_state_py_exec_updated_proto_code.return_value = (
        PythonExecutable.py_exec_updated_proto_code
    )
    mock_state_default_stderr_log_handler_configured.return_value.level = logging.INFO

    # when:
    state_value = env_ctx.state_graph.eval_state(EnvState.state_command_executed.name)

    # then:
    assert state_value is None
    mock_os_execv.assert_called_once_with(
        "/usr/bin/bash",
        [
            "bash",
            "-c",
            "echo hello",
        ],
    )


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_default_stderr_log_handler_configured.__name__}.eval_own_state"
)
@patch(f"{os.__name__}.execv")
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_updated_proto_code.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
)
def test_command_not_executed_when_no_command_line_provided(
    mock_state_args_parsed,
    mock_state_py_exec_updated_proto_code,
    mock_os_execv,
    mock_state_default_stderr_log_handler_configured,
    env_ctx,
):
    # given:
    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_command_executed.name,
    )
    mock_state_args_parsed.return_value = argparse.Namespace(
        **{
            ParsedArg.name_command.value: None,
        }
    )
    mock_state_py_exec_updated_proto_code.return_value = (
        PythonExecutable.py_exec_updated_proto_code
    )
    mock_state_default_stderr_log_handler_configured.return_value.level = logging.INFO

    # when:
    state_value = env_ctx.state_graph.eval_state(EnvState.state_command_executed.name)

    # then:
    assert state_value == 0
    mock_os_execv.assert_not_called()


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_default_stderr_log_handler_configured.__name__}.eval_own_state"
)
@patch(f"{os.__name__}.execv")
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_updated_proto_code.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
)
def test_command_executed_empty(
    mock_state_args_parsed,
    mock_state_py_exec_updated_proto_code,
    mock_os_execv,
    mock_state_default_stderr_log_handler_configured,
    env_ctx,
):
    # given:
    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_command_executed.name,
    )
    mock_state_args_parsed.return_value = argparse.Namespace(
        **{
            ParsedArg.name_command.value: "",
        }
    )
    mock_state_py_exec_updated_proto_code.return_value = (
        PythonExecutable.py_exec_updated_proto_code
    )
    mock_state_default_stderr_log_handler_configured.return_value.level = logging.INFO

    # when:
    state_value = env_ctx.state_graph.eval_state(EnvState.state_command_executed.name)

    # then:
    assert state_value is None
    mock_os_execv.assert_called_once_with(
        "/usr/bin/bash",
        [
            "bash",
            "-c",
            "",
        ],
    )


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_default_stderr_log_handler_configured.__name__}.eval_own_state"
)
@patch(f"{os.__name__}.execv")
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_updated_proto_code.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
)
def test_command_executed_with_whitespace(
    mock_state_args_parsed,
    mock_state_py_exec_updated_proto_code,
    mock_os_execv,
    mock_state_default_stderr_log_handler_configured,
    env_ctx,
):
    # given:
    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_command_executed.name,
    )
    mock_state_args_parsed.return_value = argparse.Namespace(
        **{
            ParsedArg.name_command.value: "  echo hello  ",
        }
    )
    mock_state_py_exec_updated_proto_code.return_value = (
        PythonExecutable.py_exec_updated_proto_code
    )
    mock_state_default_stderr_log_handler_configured.return_value.level = logging.INFO

    # when:
    state_value = env_ctx.state_graph.eval_state(EnvState.state_command_executed.name)

    # then:
    assert state_value is None
    mock_os_execv.assert_called_once_with(
        "/usr/bin/bash",
        [
            "bash",
            "-c",
            "  echo hello  ",
        ],
    )
