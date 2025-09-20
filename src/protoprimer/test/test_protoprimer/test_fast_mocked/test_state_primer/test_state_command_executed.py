import argparse
from unittest.mock import (
    patch,
)

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_args_parsed,
    Bootstrapper_state_py_exec_updated_proto_code,
    EnvContext,
    EnvState,
    ParsedArg,
    PythonExecutable,
)
from test_protoprimer.test_fast_mocked.misc_tools.mock_verifier import (
    assert_parent_states_mocked,
)


@pytest.fixture
def env_ctx():
    return EnvContext()


def test_relationship():
    assert_test_module_name_embeds_str(EnvState.state_command_executed.name)


@patch("subprocess.check_call")
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_updated_proto_code.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
)
def test_command_executed(
    mock_state_args_parsed,
    mock_state_py_exec_updated_proto_code,
    mock_subprocess_check_call,
    env_ctx,
):
    # given:
    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_command_executed,
    )
    mock_state_args_parsed.return_value = argparse.Namespace(
        **{
            ParsedArg.name_command.value: "echo hello",
        }
    )
    mock_state_py_exec_updated_proto_code.return_value = (
        PythonExecutable.py_exec_updated_proto_code
    )

    # when:
    result = env_ctx.state_graph.eval_state(EnvState.state_command_executed.name)

    # then:
    assert result is True
    mock_subprocess_check_call.assert_called_once_with("echo hello", shell=True)


@patch("subprocess.check_call")
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_updated_proto_code.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
)
def test_command_not_executed(
    mock_state_args_parsed,
    mock_state_py_exec_updated_proto_code,
    mock_subprocess_check_call,
    env_ctx,
):
    # given:
    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_command_executed,
    )
    mock_state_args_parsed.return_value = argparse.Namespace(
        **{
            ParsedArg.name_command.value: None,
        }
    )
    mock_state_py_exec_updated_proto_code.return_value = (
        PythonExecutable.py_exec_updated_proto_code
    )

    # when:
    result = env_ctx.state_graph.eval_state(EnvState.state_command_executed.name)

    # then:
    assert result is False
    mock_subprocess_check_call.assert_not_called()
