import argparse
import logging
import os
from unittest.mock import patch, ANY

import pytest

from local_test.mock_verifier import (
    assert_parent_states_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_args_parsed,
    Bootstrapper_state_default_stderr_log_handler_configured,
    Bootstrapper_state_py_exec_src_updated_reached,
    EnvContext,
    EnvState,
    ParsedArg,
    PythonExecutable,
    Bootstrapper_state_local_venv_dir_abs_path_inited,
    Bootstrapper_state_local_cache_dir_abs_path_inited,
)


@pytest.fixture
def env_ctx():
    return EnvContext()


def test_relationship():
    assert_test_module_name_embeds_str(EnvState.state_command_executed.name)


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_default_stderr_log_handler_configured.__name__}.eval_own_state"
)
@patch(f"{primer_kernel.__name__}.os.execve")
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_src_updated_reached.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_local_cache_dir_abs_path_inited.__name__}.eval_own_state"
)
@patch.dict(
    os.environ,
    {
        "SHELL": "/bin/bash",
    },
    clear=True,
)
def test_command_executed_in_bash(
    mock_state_local_cache_dir_abs_path_inited,
    mock_state_local_venv_dir_abs_path_inited,
    mock_state_args_parsed,
    mock_state_py_exec_src_updated_reached,
    mock_os_execve,
    mock_state_default_stderr_log_handler_configured,
    env_ctx,
    fs,
):
    # given:
    fs.create_dir("/fake")
    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_command_executed.name,
    )
    mock_state_args_parsed.return_value = argparse.Namespace(
        **{
            ParsedArg.name_command.value: "echo hello",
        }
    )
    mock_state_py_exec_src_updated_reached.return_value = (
        PythonExecutable.py_exec_src_updated
    )
    mock_state_default_stderr_log_handler_configured.return_value.level = logging.INFO
    mock_state_local_venv_dir_abs_path_inited.return_value = "/fake/venv"
    mock_state_local_cache_dir_abs_path_inited.return_value = "/fake/cache"

    # when:
    env_ctx.state_graph.eval_state(EnvState.state_command_executed.name)

    # then:
    mock_os_execve.assert_called_once_with(
        "/bin/bash",
        [
            "/bin/bash",
            "--init-file",
            "/fake/cache/bash/.bashrc",
            "-i",
            "-c",
            "echo hello",
        ],
        {
            "SHELL": "/bin/bash",
        },
    )


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_default_stderr_log_handler_configured.__name__}.eval_own_state"
)
@patch(f"{primer_kernel.__name__}.os.execve")
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_src_updated_reached.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_local_cache_dir_abs_path_inited.__name__}.eval_own_state"
)
@patch.dict(
    os.environ,
    {
        "SHELL": "/bin/zsh",
    },
    clear=True,
)
def test_command_executed_in_zsh(
    mock_state_local_cache_dir_abs_path_inited,
    mock_state_local_venv_dir_abs_path_inited,
    mock_state_args_parsed,
    mock_state_py_exec_src_updated_reached,
    mock_os_execve,
    mock_state_default_stderr_log_handler_configured,
    env_ctx,
    fs,
):
    # given:
    fs.create_dir("/fake")
    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_command_executed.name,
    )
    mock_state_args_parsed.return_value = argparse.Namespace(
        **{
            ParsedArg.name_command.value: "echo hello",
        }
    )
    mock_state_py_exec_src_updated_reached.return_value = (
        PythonExecutable.py_exec_src_updated
    )
    mock_state_default_stderr_log_handler_configured.return_value.level = logging.INFO
    mock_state_local_venv_dir_abs_path_inited.return_value = "/fake/venv"
    mock_state_local_cache_dir_abs_path_inited.return_value = "/fake/cache"

    # when:
    env_ctx.state_graph.eval_state(EnvState.state_command_executed.name)

    # then:
    # In ShellDriverZsh, there are no extra shell_args, just an env var `ZDOTDIR`.
    mock_os_execve.assert_called_once_with(
        "/bin/zsh",
        [
            "/bin/zsh",
            "-i",
            "-c",
            "echo hello",
        ],
        {
            "SHELL": "/bin/zsh",
            "ZDOTDIR": "/fake/cache/zsh",
        },
    )


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_default_stderr_log_handler_configured.__name__}.eval_own_state"
)
@patch(f"{primer_kernel.__name__}.os.execve")
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_src_updated_reached.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_local_cache_dir_abs_path_inited.__name__}.eval_own_state"
)
@patch.dict(
    os.environ,
    {
        "SHELL": "/bin/bash",
    },
    clear=True,
)
def test_command_not_executed_when_no_command_line_provided(
    mock_state_local_cache_dir_abs_path_inited,
    mock_state_local_venv_dir_abs_path_inited,
    mock_state_args_parsed,
    mock_state_py_exec_src_updated_reached,
    mock_os_execve,
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
    mock_state_py_exec_src_updated_reached.return_value = (
        PythonExecutable.py_exec_src_updated
    )
    mock_state_default_stderr_log_handler_configured.return_value.level = logging.INFO

    # when:
    state_value = env_ctx.state_graph.eval_state(EnvState.state_command_executed.name)

    # then:
    assert state_value == 0
    mock_os_execve.assert_not_called()


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_default_stderr_log_handler_configured.__name__}.eval_own_state"
)
@patch(f"{primer_kernel.__name__}.os.execve")
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_src_updated_reached.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_local_cache_dir_abs_path_inited.__name__}.eval_own_state"
)
@patch.dict(
    os.environ,
    {
        "SHELL": "/bin/bash",
    },
    clear=True,
)
def test_command_executed_empty(
    mock_state_local_cache_dir_abs_path_inited,
    mock_state_local_venv_dir_abs_path_inited,
    mock_state_args_parsed,
    mock_state_py_exec_src_updated_reached,
    mock_os_execve,
    mock_state_default_stderr_log_handler_configured,
    env_ctx,
    fs,
):
    # given:
    fs.create_dir("/fake")
    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_command_executed.name,
    )
    mock_state_args_parsed.return_value = argparse.Namespace(
        **{
            ParsedArg.name_command.value: "",
        }
    )
    mock_state_py_exec_src_updated_reached.return_value = (
        PythonExecutable.py_exec_src_updated
    )
    mock_state_default_stderr_log_handler_configured.return_value.level = logging.INFO
    mock_state_local_venv_dir_abs_path_inited.return_value = "/fake/venv"
    mock_state_local_cache_dir_abs_path_inited.return_value = "/fake/cache"

    # when:
    env_ctx.state_graph.eval_state(EnvState.state_command_executed.name)

    # then:
    mock_os_execve.assert_called_once_with(
        "/bin/bash",
        [
            "/bin/bash",
            "--init-file",
            "/fake/cache/bash/.bashrc",
            "-i",
            "-c",
            "",
        ],
        {
            "SHELL": "/bin/bash",
        },
    )


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_default_stderr_log_handler_configured.__name__}.eval_own_state"
)
@patch(f"{primer_kernel.__name__}.os.execve")
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_src_updated_reached.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_local_cache_dir_abs_path_inited.__name__}.eval_own_state"
)
@patch.dict(
    os.environ,
    {
        "SHELL": "/bin/bash",
    },
    clear=True,
)
def test_command_executed_with_whitespace(
    mock_state_local_cache_dir_abs_path_inited,
    mock_state_local_venv_dir_abs_path_inited,
    mock_state_args_parsed,
    mock_state_py_exec_src_updated_reached,
    mock_os_execve,
    mock_state_default_stderr_log_handler_configured,
    env_ctx,
    fs,
):
    # given:
    fs.create_dir("/fake")
    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_command_executed.name,
    )
    mock_state_args_parsed.return_value = argparse.Namespace(
        **{
            ParsedArg.name_command.value: "  echo hello  ",
        }
    )
    mock_state_py_exec_src_updated_reached.return_value = (
        PythonExecutable.py_exec_src_updated
    )
    mock_state_default_stderr_log_handler_configured.return_value.level = logging.INFO
    mock_state_local_venv_dir_abs_path_inited.return_value = "/fake/venv"
    mock_state_local_cache_dir_abs_path_inited.return_value = "/fake/cache"

    # when:
    env_ctx.state_graph.eval_state(EnvState.state_command_executed.name)

    # then:
    mock_os_execve.assert_called_once_with(
        "/bin/bash",
        [
            "/bin/bash",
            "--init-file",
            "/fake/cache/bash/.bashrc",
            "-i",
            "-c",
            "  echo hello  ",
        ],
        {
            "SHELL": "/bin/bash",
        },
    )
