import json
import os
from unittest.mock import patch

import pytest

from local_test.mock_verifier import assert_parent_factories_mocked
from local_test.name_assertion import assert_test_module_name_embeds_str
from neoprimer import conf_renderer
from neoprimer.cmd_eval_conf import customize_env_context
from neoprimer.conf_renderer import (
    Bootstrapper_state_client_conf_file_data_loaded_rendered,
    Bootstrapper_state_env_conf_file_data_loaded_rendered,
)
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_input_exec_mode_arg_loaded,
    Bootstrapper_state_input_stderr_log_level_eval_finalized,
    Bootstrapper_state_local_conf_file_abs_path_inited,
    EnvState,
)


@pytest.fixture
def env_ctx():
    return customize_env_context()


def test_relationship():
    assert_test_module_name_embeds_str(Bootstrapper_state_env_conf_file_data_loaded_rendered.__name__)


@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_eval_finalized.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_exec_mode_arg_loaded.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_file_abs_path_inited.__name__}.create_state_node")
@patch(f"{conf_renderer.__name__}.{Bootstrapper_state_client_conf_file_data_loaded_rendered.__name__}.create_state_node")
def test_conf_file_exists(
    mock_factory_client_conf_file_data_loaded_rendered,
    mock_factory_local_conf_file_abs_path_inited,
    mock_factory_input_exec_mode_arg_loaded,
    mock_factory_input_stderr_log_level_eval_finalized,
    env_ctx,
    fs,
):

    # given:

    assert_parent_factories_mocked(
        env_ctx,
        Bootstrapper_state_env_conf_file_data_loaded_rendered._state_name(),
    )

    mock_conf_file = "/mock/path/to/env_conf.json"
    mock_factory_local_conf_file_abs_path_inited.return_value.eval_own_state.return_value = mock_conf_file

    mock_data = {"test": "data"}
    fs.create_file(mock_conf_file, contents=json.dumps(mock_data))

    # when:

    state_value = env_ctx.state_graph.eval_state(
        Bootstrapper_state_env_conf_file_data_loaded_rendered._state_name(),
    )

    # then:

    assert state_value == mock_data


@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_eval_finalized.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_exec_mode_arg_loaded.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_file_abs_path_inited.__name__}.create_state_node")
@patch(f"{conf_renderer.__name__}.{Bootstrapper_state_client_conf_file_data_loaded_rendered.__name__}.create_state_node")
def test_conf_file_missing(
    mock_factory_client_conf_file_data_loaded_rendered,
    mock_factory_local_conf_file_abs_path_inited,
    mock_factory_input_exec_mode_arg_loaded,
    mock_factory_input_stderr_log_level_eval_finalized,
    env_ctx,
    fs,
    caplog,
):

    # given:

    assert_parent_factories_mocked(
        env_ctx,
        Bootstrapper_state_env_conf_file_data_loaded_rendered._state_name(),
    )

    mock_conf_file = "/mock/path/to/env_conf.json"
    fs.create_dir("/mock/path/to")
    mock_factory_local_conf_file_abs_path_inited.return_value.eval_own_state.return_value = mock_conf_file

    assert not os.path.exists(mock_conf_file)

    # when:

    state_value = env_ctx.state_graph.eval_state(
        Bootstrapper_state_env_conf_file_data_loaded_rendered._state_name(),
    )

    # then:

    assert state_value == {}
    assert "does not exist" not in caplog.text


@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_eval_finalized.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_exec_mode_arg_loaded.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_file_abs_path_inited.__name__}.create_state_node")
@patch(f"{conf_renderer.__name__}.{Bootstrapper_state_client_conf_file_data_loaded_rendered.__name__}.create_state_node")
def test_conf_file_malformed(
    mock_factory_client_conf_file_data_loaded_rendered,
    mock_factory_local_conf_file_abs_path_inited,
    mock_factory_input_exec_mode_arg_loaded,
    mock_factory_input_stderr_log_level_eval_finalized,
    env_ctx,
    fs,
):

    # given:

    assert_parent_factories_mocked(
        env_ctx,
        Bootstrapper_state_env_conf_file_data_loaded_rendered._state_name(),
    )

    mock_conf_file = "/mock/path/to/env_conf.json"
    mock_factory_local_conf_file_abs_path_inited.return_value.eval_own_state.return_value = mock_conf_file
    fs.create_file(mock_conf_file, contents="not a valid json")

    # when/then:

    with pytest.raises(json.decoder.JSONDecodeError):
        env_ctx.state_graph.eval_state(
            Bootstrapper_state_env_conf_file_data_loaded_rendered._state_name(),
        )
