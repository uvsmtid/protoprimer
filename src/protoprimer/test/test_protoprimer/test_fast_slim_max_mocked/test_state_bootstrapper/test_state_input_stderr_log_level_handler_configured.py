import logging
import sys
from unittest.mock import patch

import pytest

from local_test.mock_verifier import (
    assert_parent_factories_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_args_parsed,
    Bootstrapper_state_default_stderr_log_handler_configured,
    Bootstrapper_state_input_stderr_log_level_eval_finalized,
    EnvContext,
    EnvState,
    _PrimerStderrLogFormatter,
)


@pytest.fixture
def env_ctx():
    return EnvContext()


@pytest.fixture
def stderr_handler():
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        _PrimerStderrLogFormatter(
            verbosity_level=logging.WARNING,
        )
    )
    return handler


def test_relationship():
    assert_test_module_name_embeds_str(EnvState.state_input_stderr_log_level_handler_configured.name)


@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_eval_finalized.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_default_stderr_log_handler_configured.__name__}.create_state_node")
def test_handler_level_configured(
    mock_state_default_stderr_log_handler_configured,
    mock_state_args_parsed,
    mock_state_input_stderr_log_level_eval_finalized,
    env_ctx,
    stderr_handler,
):
    # given:

    assert_parent_factories_mocked(
        env_ctx,
        EnvState.state_input_stderr_log_level_handler_configured.name,
    )
    stderr_handler.setLevel(logging.WARNING)
    mock_state_default_stderr_log_handler_configured.return_value.eval_own_state.return_value = stderr_handler
    mock_state_input_stderr_log_level_eval_finalized.return_value.eval_own_state.return_value = logging.DEBUG

    # when:

    result_handler = env_ctx.state_graph.eval_state(EnvState.state_input_stderr_log_level_handler_configured.name)

    # then:

    assert result_handler is stderr_handler
    assert stderr_handler.level == logging.DEBUG


@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_eval_finalized.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_default_stderr_log_handler_configured.__name__}.create_state_node")
def test_returns_handler(
    mock_state_default_stderr_log_handler_configured,
    mock_state_args_parsed,
    mock_state_input_stderr_log_level_eval_finalized,
    env_ctx,
    stderr_handler,
):
    # given:

    assert_parent_factories_mocked(
        env_ctx,
        EnvState.state_input_stderr_log_level_handler_configured.name,
    )
    mock_state_default_stderr_log_handler_configured.return_value.eval_own_state.return_value = stderr_handler
    mock_state_input_stderr_log_level_eval_finalized.return_value.eval_own_state.return_value = logging.WARNING

    # when:

    result = env_ctx.state_graph.eval_state(EnvState.state_input_stderr_log_level_handler_configured.name)

    # then:

    assert isinstance(result, logging.Handler)
