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
from protoprimer.primer_kernel import (
    ConfConstInput,
    EnvContext,
    EnvState,
    EnvVar,
)

default_stderr_log_level = getattr(
    logging,
    ConfConstInput.default_PROTOPRIMER_STDERR_LOG_LEVEL,
)


@pytest.fixture
def env_ctx():
    return EnvContext()


# noinspection PyMethodMayBeStatic
def test_relationship():
    assert_test_module_name_embeds_str(EnvState.state_input_stderr_log_level_var_loaded.name)


@patch("protoprimer.primer_kernel.Bootstrapper_state_input_py_exec_var_loaded.create_state_node")
@patch.dict(f"{os.__name__}.environ", {}, clear=True)
def test_default_case(mock_state_input_py_exec_var_loaded, env_ctx):
    # given:
    assert_parent_factories_mocked(
        env_ctx,
        EnvState.state_input_stderr_log_level_var_loaded.name,
    )
    # when:
    state_value = env_ctx.state_graph.eval_state(EnvState.state_input_stderr_log_level_var_loaded.name, env_ctx)
    # then:
    assert getattr(logging, ConfConstInput.default_PROTOPRIMER_STDERR_LOG_LEVEL) == state_value


@patch("protoprimer.primer_kernel.Bootstrapper_state_input_py_exec_var_loaded.create_state_node")
@patch.dict(
    f"{os.__name__}.environ",
    {EnvVar.var_PROTOPRIMER_STDERR_LOG_LEVEL.value: "DEBUG"},
    clear=True,
)
def test_env_var_set_to_debug(mock_state_input_py_exec_var_loaded, env_ctx):
    # given:
    assert_parent_factories_mocked(
        env_ctx,
        EnvState.state_input_stderr_log_level_var_loaded.name,
    )
    # when:
    state_value = env_ctx.state_graph.eval_state(EnvState.state_input_stderr_log_level_var_loaded.name, env_ctx)
    # then:
    assert logging.DEBUG == state_value


@patch("protoprimer.primer_kernel.Bootstrapper_state_input_py_exec_var_loaded.create_state_node")
@patch.dict(
    f"{os.__name__}.environ",
    {EnvVar.var_PROTOPRIMER_STDERR_LOG_LEVEL.value: "10"},
    clear=True,
)
def test_env_var_set_to_10(mock_state_input_py_exec_var_loaded, env_ctx):
    # given:
    assert_parent_factories_mocked(
        env_ctx,
        EnvState.state_input_stderr_log_level_var_loaded.name,
    )
    # when:
    state_value = env_ctx.state_graph.eval_state(EnvState.state_input_stderr_log_level_var_loaded.name, env_ctx)
    # then:
    assert 10 == state_value


@patch("protoprimer.primer_kernel.Bootstrapper_state_input_py_exec_var_loaded.create_state_node")
@patch.dict(
    f"{os.__name__}.environ",
    {EnvVar.var_PROTOPRIMER_STDERR_LOG_LEVEL.value: "-1"},
    clear=True,
)
def test_env_var_set_to_negative_1(mock_state_input_py_exec_var_loaded, env_ctx):
    # given:
    assert_parent_factories_mocked(
        env_ctx,
        EnvState.state_input_stderr_log_level_var_loaded.name,
    )
    # when:
    state_value = env_ctx.state_graph.eval_state(EnvState.state_input_stderr_log_level_var_loaded.name, env_ctx)
    # then:
    assert default_stderr_log_level == state_value


@patch("protoprimer.primer_kernel.Bootstrapper_state_input_py_exec_var_loaded.create_state_node")
@patch.dict(
    f"{os.__name__}.environ",
    {EnvVar.var_PROTOPRIMER_STDERR_LOG_LEVEL.value: "NOTSET"},
    clear=True,
)
def test_env_var_set_to_notset(mock_state_input_py_exec_var_loaded, env_ctx):
    # given:
    assert_parent_factories_mocked(
        env_ctx,
        EnvState.state_input_stderr_log_level_var_loaded.name,
    )
    # when:
    state_value = env_ctx.state_graph.eval_state(EnvState.state_input_stderr_log_level_var_loaded.name, env_ctx)
    # then:
    assert logging.NOTSET == state_value


@patch("protoprimer.primer_kernel.Bootstrapper_state_input_py_exec_var_loaded.create_state_node")
@patch.dict(
    f"{os.__name__}.environ",
    {EnvVar.var_PROTOPRIMER_STDERR_LOG_LEVEL.value: "NOT_A_LOG_LEVEL"},
    clear=True,
)
def test_env_var_set_to_invalid_string(mock_state_input_py_exec_var_loaded, env_ctx):
    # given:
    assert_parent_factories_mocked(
        env_ctx,
        EnvState.state_input_stderr_log_level_var_loaded.name,
    )
    # when:
    state_value = env_ctx.state_graph.eval_state(EnvState.state_input_stderr_log_level_var_loaded.name, env_ctx)
    # then:
    assert default_stderr_log_level == state_value
