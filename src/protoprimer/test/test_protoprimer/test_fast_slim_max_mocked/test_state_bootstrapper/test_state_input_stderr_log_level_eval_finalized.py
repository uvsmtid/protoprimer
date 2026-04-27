import argparse
import logging
import os
from unittest.mock import (
    patch,
)

import pytest

from local_test.mock_verifier import (
    assert_parent_factories_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_args_parsed,
    Bootstrapper_state_input_stderr_log_level_var_loaded,
    ConfConstInput,
    EnvContext,
    EnvState,
    EnvVar,
    SyntaxArg,
)


@pytest.fixture
def env_ctx():
    return EnvContext()


def test_relationship():
    assert_test_module_name_embeds_str(EnvState.state_input_stderr_log_level_eval_finalized.name)


@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_var_loaded.__name__}.create_state_node")
def test_default_case_no_flags_uses_default_from_var(
    mock_state_input_stderr_log_level_var_loaded,
    mock_state_args_parsed,
    env_ctx,
):
    # given:

    assert_parent_factories_mocked(
        env_ctx,
        EnvState.state_input_stderr_log_level_eval_finalized.name,
    )
    mock_state_input_stderr_log_level_var_loaded.return_value.eval_own_state.return_value = logging.INFO
    mock_state_args_parsed.return_value.eval_own_state.return_value = argparse.Namespace(
        **{SyntaxArg.dest_quiet: 0},
        **{SyntaxArg.dest_verbose: 0},
    )

    # when:

    state_value = env_ctx.state_graph.eval_state(EnvState.state_input_stderr_log_level_eval_finalized.name)

    # then:

    assert state_value == logging.INFO


@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_var_loaded.__name__}.create_state_node")
def test_default_case_no_flags_uses_warning(
    mock_state_input_stderr_log_level_var_loaded,
    mock_state_args_parsed,
    env_ctx,
):
    # given:

    assert_parent_factories_mocked(
        env_ctx,
        EnvState.state_input_stderr_log_level_eval_finalized.name,
    )
    default_log_level: int = getattr(
        logging,
        ConfConstInput.default_PROTOPRIMER_STDERR_LOG_LEVEL,
    )
    mock_state_input_stderr_log_level_var_loaded.return_value.eval_own_state.return_value = default_log_level
    mock_state_args_parsed.return_value.eval_own_state.return_value = argparse.Namespace(
        **{SyntaxArg.dest_quiet: 0},
        **{SyntaxArg.dest_verbose: 0},
    )

    # when:

    state_value = env_ctx.state_graph.eval_state(EnvState.state_input_stderr_log_level_eval_finalized.name)

    # then:

    assert state_value == logging.WARNING


@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_var_loaded.__name__}.create_state_node")
def test_quiet_1_only(
    mock_state_input_stderr_log_level_var_loaded,
    mock_state_args_parsed,
    env_ctx,
):
    # given:

    assert_parent_factories_mocked(
        env_ctx,
        EnvState.state_input_stderr_log_level_eval_finalized.name,
    )
    default_log_level: int = getattr(
        logging,
        ConfConstInput.default_PROTOPRIMER_STDERR_LOG_LEVEL,
    )
    mock_state_input_stderr_log_level_var_loaded.return_value.eval_own_state.return_value = default_log_level
    mock_state_args_parsed.return_value.eval_own_state.return_value = argparse.Namespace(
        **{SyntaxArg.dest_quiet: 1},
        **{SyntaxArg.dest_verbose: 0},
    )

    # when:

    state_value = env_ctx.state_graph.eval_state(EnvState.state_input_stderr_log_level_eval_finalized.name)

    # then:

    assert state_value == logging.ERROR


@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_var_loaded.__name__}.create_state_node")
def test_quiet_2_only(
    mock_state_input_stderr_log_level_var_loaded,
    mock_state_args_parsed,
    env_ctx,
):
    # given:

    assert_parent_factories_mocked(
        env_ctx,
        EnvState.state_input_stderr_log_level_eval_finalized.name,
    )
    default_log_level: int = getattr(
        logging,
        ConfConstInput.default_PROTOPRIMER_STDERR_LOG_LEVEL,
    )
    mock_state_input_stderr_log_level_var_loaded.return_value.eval_own_state.return_value = default_log_level
    mock_state_args_parsed.return_value.eval_own_state.return_value = argparse.Namespace(
        **{SyntaxArg.dest_quiet: 2},
        **{SyntaxArg.dest_verbose: 0},
    )

    # when:

    state_value = env_ctx.state_graph.eval_state(EnvState.state_input_stderr_log_level_eval_finalized.name)

    # then:

    assert state_value == logging.CRITICAL


@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_var_loaded.__name__}.create_state_node")
def test_quiet_5_only(
    mock_state_input_stderr_log_level_var_loaded,
    mock_state_args_parsed,
    env_ctx,
):
    # given:

    assert_parent_factories_mocked(
        env_ctx,
        EnvState.state_input_stderr_log_level_eval_finalized.name,
    )
    default_log_level: int = getattr(
        logging,
        ConfConstInput.default_PROTOPRIMER_STDERR_LOG_LEVEL,
    )
    mock_state_input_stderr_log_level_var_loaded.return_value.eval_own_state.return_value = default_log_level
    mock_state_args_parsed.return_value.eval_own_state.return_value = argparse.Namespace(
        **{SyntaxArg.dest_quiet: 5},
        **{SyntaxArg.dest_verbose: 0},
    )

    # when:

    state_value = env_ctx.state_graph.eval_state(EnvState.state_input_stderr_log_level_eval_finalized.name)

    # then:

    assert state_value == 80


@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_var_loaded.__name__}.create_state_node")
def test_verbose_1_only(
    mock_state_input_stderr_log_level_var_loaded,
    mock_state_args_parsed,
    env_ctx,
):
    # given:

    assert_parent_factories_mocked(
        env_ctx,
        EnvState.state_input_stderr_log_level_eval_finalized.name,
    )
    default_log_level: int = getattr(
        logging,
        ConfConstInput.default_PROTOPRIMER_STDERR_LOG_LEVEL,
    )
    mock_state_input_stderr_log_level_var_loaded.return_value.eval_own_state.return_value = default_log_level
    mock_state_args_parsed.return_value.eval_own_state.return_value = argparse.Namespace(
        **{SyntaxArg.dest_quiet: 0},
        **{SyntaxArg.dest_verbose: 1},
    )

    # when:

    state_value = env_ctx.state_graph.eval_state(EnvState.state_input_stderr_log_level_eval_finalized.name)

    # then:

    assert state_value == logging.INFO


@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_var_loaded.__name__}.create_state_node")
def test_verbose_2_only(
    mock_state_input_stderr_log_level_var_loaded,
    mock_state_args_parsed,
    env_ctx,
):
    # given:

    assert_parent_factories_mocked(
        env_ctx,
        EnvState.state_input_stderr_log_level_eval_finalized.name,
    )
    default_log_level: int = getattr(
        logging,
        ConfConstInput.default_PROTOPRIMER_STDERR_LOG_LEVEL,
    )
    mock_state_input_stderr_log_level_var_loaded.return_value.eval_own_state.return_value = default_log_level
    mock_state_args_parsed.return_value.eval_own_state.return_value = argparse.Namespace(
        **{SyntaxArg.dest_quiet: 0},
        **{SyntaxArg.dest_verbose: 2},
    )

    # when:

    state_value = env_ctx.state_graph.eval_state(EnvState.state_input_stderr_log_level_eval_finalized.name)

    # then:

    assert state_value == logging.DEBUG


@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_var_loaded.__name__}.create_state_node")
def test_verbose_3_only(
    mock_state_input_stderr_log_level_var_loaded,
    mock_state_args_parsed,
    env_ctx,
):
    # given:

    assert_parent_factories_mocked(
        env_ctx,
        EnvState.state_input_stderr_log_level_eval_finalized.name,
    )
    default_log_level: int = getattr(
        logging,
        ConfConstInput.default_PROTOPRIMER_STDERR_LOG_LEVEL,
    )
    mock_state_input_stderr_log_level_var_loaded.return_value.eval_own_state.return_value = default_log_level
    mock_state_args_parsed.return_value.eval_own_state.return_value = argparse.Namespace(
        **{SyntaxArg.dest_quiet: 0},
        **{SyntaxArg.dest_verbose: 3},
    )

    # when:

    state_value = env_ctx.state_graph.eval_state(EnvState.state_input_stderr_log_level_eval_finalized.name)

    # then:

    assert state_value == logging.NOTSET


@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_var_loaded.__name__}.create_state_node")
def test_verbose_4_only(
    mock_state_input_stderr_log_level_var_loaded,
    mock_state_args_parsed,
    env_ctx,
):
    # given:

    assert_parent_factories_mocked(
        env_ctx,
        EnvState.state_input_stderr_log_level_eval_finalized.name,
    )
    default_log_level: int = getattr(
        logging,
        ConfConstInput.default_PROTOPRIMER_STDERR_LOG_LEVEL,
    )
    mock_state_input_stderr_log_level_var_loaded.return_value.eval_own_state.return_value = default_log_level
    mock_state_args_parsed.return_value.eval_own_state.return_value = argparse.Namespace(
        **{SyntaxArg.dest_quiet: 0},
        **{SyntaxArg.dest_verbose: 4},
    )

    # when:

    state_value = env_ctx.state_graph.eval_state(EnvState.state_input_stderr_log_level_eval_finalized.name)

    # then:

    assert state_value == logging.NOTSET


@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_var_loaded.__name__}.create_state_node")
def test_quiet_and_verbose(
    mock_state_input_stderr_log_level_var_loaded,
    mock_state_args_parsed,
    env_ctx,
):
    # given:

    assert_parent_factories_mocked(
        env_ctx,
        EnvState.state_input_stderr_log_level_eval_finalized.name,
    )
    default_log_level: int = getattr(
        logging,
        ConfConstInput.default_PROTOPRIMER_STDERR_LOG_LEVEL,
    )
    mock_state_input_stderr_log_level_var_loaded.return_value.eval_own_state.return_value = default_log_level
    mock_state_args_parsed.return_value.eval_own_state.return_value = argparse.Namespace(
        **{SyntaxArg.dest_quiet: 2},
        **{SyntaxArg.dest_verbose: 1},
    )

    # when:

    state_value = env_ctx.state_graph.eval_state(EnvState.state_input_stderr_log_level_eval_finalized.name)

    # then:

    assert state_value == logging.ERROR


@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_var_loaded.__name__}.create_state_node")
@patch.dict(f"{os.__name__}.environ", {}, clear=True)
def test_env_var_not_updated_read_only(
    mock_state_input_stderr_log_level_var_loaded,
    mock_state_args_parsed,
    env_ctx,
):
    # given:

    assert_parent_factories_mocked(
        env_ctx,
        EnvState.state_input_stderr_log_level_eval_finalized.name,
    )
    default_log_level: int = getattr(
        logging,
        ConfConstInput.default_PROTOPRIMER_STDERR_LOG_LEVEL,
    )
    mock_state_input_stderr_log_level_var_loaded.return_value.eval_own_state.return_value = default_log_level
    mock_state_args_parsed.return_value.eval_own_state.return_value = argparse.Namespace(
        **{SyntaxArg.dest_quiet: 1},
        **{SyntaxArg.dest_verbose: 0},
    )

    # when:

    state_value = env_ctx.state_graph.eval_state(EnvState.state_input_stderr_log_level_eval_finalized.name)

    # then:

    assert state_value == logging.ERROR
    assert os.environ.get(EnvVar.var_PROTOPRIMER_STDERR_LOG_LEVEL.value, None) is None
