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
from protoprimer.primer_kernel import (
    ConfConstInput,
    EnvContext,
    EnvState,
    EnvVar,
)


@pytest.fixture
def env_ctx():
    return EnvContext()


# noinspection PyMethodMayBeStatic
def test_relationship():
    assert_test_module_name_embeds_str(
        EnvState.state_input_stderr_log_level_var_loaded.name
    )


@patch.dict(f"{os.__name__}.environ", {}, clear=True)
def test_default_case(env_ctx):
    # given:
    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_input_stderr_log_level_var_loaded.name,
    )
    # when:
    state_value = env_ctx.state_graph.eval_state(
        EnvState.state_input_stderr_log_level_var_loaded.name
    )
    # then:
    assert (
        getattr(logging, ConfConstInput.default_PROTOPRIMER_STDERR_LOG_LEVEL)
        == state_value
    )


@patch.dict(
    f"{os.__name__}.environ",
    {EnvVar.var_PROTOPRIMER_STDERR_LOG_LEVEL.value: "DEBUG"},
    clear=True,
)
def test_env_var_set_to_debug(env_ctx):
    # given:
    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_input_stderr_log_level_var_loaded.name,
    )
    # when:
    state_value = env_ctx.state_graph.eval_state(
        EnvState.state_input_stderr_log_level_var_loaded.name
    )
    # then:
    assert logging.DEBUG == state_value


@patch.dict(
    f"{os.__name__}.environ",
    {EnvVar.var_PROTOPRIMER_STDERR_LOG_LEVEL.value: "10"},
    clear=True,
)
def test_env_var_set_to_10(env_ctx):
    # given:
    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_input_stderr_log_level_var_loaded.name,
    )
    # when:
    state_value = env_ctx.state_graph.eval_state(
        EnvState.state_input_stderr_log_level_var_loaded.name
    )
    # then:
    assert 10 == state_value


@patch.dict(
    f"{os.__name__}.environ",
    {EnvVar.var_PROTOPRIMER_STDERR_LOG_LEVEL.value: "-1"},
    clear=True,
)
def test_env_var_set_to_negative_1(env_ctx):
    # given:
    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_input_stderr_log_level_var_loaded.name,
    )
    # when:
    with pytest.raises(AttributeError) as cm:
        env_ctx.state_graph.eval_state(
            EnvState.state_input_stderr_log_level_var_loaded.name
        )
    # then:
    assert "'-1'" in str(cm.value)


@patch.dict(
    f"{os.__name__}.environ",
    {EnvVar.var_PROTOPRIMER_STDERR_LOG_LEVEL.value: "NOTSET"},
    clear=True,
)
def test_env_var_set_to_notset(env_ctx):
    # given:
    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_input_stderr_log_level_var_loaded.name,
    )
    # when:
    state_value = env_ctx.state_graph.eval_state(
        EnvState.state_input_stderr_log_level_var_loaded.name
    )
    # then:
    assert logging.NOTSET == state_value


@patch.dict(
    f"{os.__name__}.environ",
    {EnvVar.var_PROTOPRIMER_STDERR_LOG_LEVEL.value: "NOT_A_LOG_LEVEL"},
    clear=True,
)
def test_env_var_set_to_invalid_string(env_ctx):
    # given:
    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_input_stderr_log_level_var_loaded.name,
    )
    # when:
    with pytest.raises(AttributeError) as cm:
        env_ctx.state_graph.eval_state(
            EnvState.state_input_stderr_log_level_var_loaded.name
        )
    # then:
    assert "NOT_A_LOG_LEVEL" in str(cm.value)
