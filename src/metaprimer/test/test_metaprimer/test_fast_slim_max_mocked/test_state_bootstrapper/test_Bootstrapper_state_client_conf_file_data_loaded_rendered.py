import json
import os
from logging import WARNING
from unittest.mock import patch

import pytest

from local_test.mock_verifier import assert_parent_factories_mocked
from local_test.name_assertion import assert_test_module_name_embeds_str
from metaprimer import conf_renderer
from metaprimer.cmd_eval_conf import customize_env_context
from metaprimer.conf_renderer import (
    Bootstrapper_state_client_conf_file_data_loaded_rendered,
    Bootstrapper_state_primer_conf_file_data_loaded_rendered,
)
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_global_conf_file_abs_path_inited,
    Bootstrapper_state_input_sub_command_arg_loaded,
    Bootstrapper_state_input_stderr_log_level_eval_finalized,
    ConfConstPrimer,
    EnvState,
    StateStride,
)


@pytest.fixture
def env_ctx():
    return customize_env_context()


def test_relationship():
    assert_test_module_name_embeds_str(Bootstrapper_state_client_conf_file_data_loaded_rendered.__name__)


@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_eval_finalized.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_sub_command_arg_loaded.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_global_conf_file_abs_path_inited.__name__}.create_state_node")
@patch(f"{conf_renderer.__name__}.{Bootstrapper_state_primer_conf_file_data_loaded_rendered.__name__}.create_state_node")
def test_conf_file_exists(
    mock_factory_primer_conf_file_data_loaded_rendered,
    mock_factory_global_conf_file_abs_path_inited,
    mock_factory_input_sub_command_arg_loaded,
    mock_factory_input_stderr_log_level_eval_finalized,
    env_ctx,
    fs,
):

    # given:

    assert_parent_factories_mocked(
        env_ctx,
        Bootstrapper_state_client_conf_file_data_loaded_rendered._state_name(),
    )

    mock_client_dir = "/mock_client_dir"
    fs.create_dir(mock_client_dir)
    os.chdir(mock_client_dir)
    state_global_conf_file_abs_path_inited = os.path.join(
        mock_client_dir,
        ConfConstPrimer.default_client_conf_file_rel_path,
    )
    mock_factory_global_conf_file_abs_path_inited.return_value.eval_own_state.return_value = state_global_conf_file_abs_path_inited
    fs.create_file(state_global_conf_file_abs_path_inited, contents=json.dumps({}))

    # when:

    state_value = env_ctx.state_graph.eval_state(
        Bootstrapper_state_client_conf_file_data_loaded_rendered._state_name(),
    )

    # then:

    assert state_value == {}


@patch(f"{primer_kernel.__name__}.EnvContext.get_stride")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_eval_finalized.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_sub_command_arg_loaded.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_global_conf_file_abs_path_inited.__name__}.create_state_node")
@patch(f"{conf_renderer.__name__}.{Bootstrapper_state_primer_conf_file_data_loaded_rendered.__name__}.create_state_node")
def test_conf_file_missing(
    mock_factory_primer_conf_file_data_loaded_rendered,
    mock_factory_global_conf_file_abs_path_inited,
    mock_factory_input_sub_command_arg_loaded,
    mock_factory_input_stderr_log_level_eval_finalized,
    mock_get_stride,
    env_ctx,
    fs,
    caplog,
):

    # given:

    assert_parent_factories_mocked(
        env_ctx,
        Bootstrapper_state_client_conf_file_data_loaded_rendered._state_name(),
    )

    mock_client_dir = "/mock_client_dir"
    fs.create_dir(mock_client_dir)
    os.chdir(mock_client_dir)
    state_global_conf_file_abs_path_inited = os.path.join(
        mock_client_dir,
        ConfConstPrimer.default_client_conf_file_rel_path,
    )
    mock_factory_global_conf_file_abs_path_inited.return_value.eval_own_state.return_value = state_global_conf_file_abs_path_inited
    mock_get_stride.return_value = StateStride.stride_py_arbitrary

    # when:

    caplog.set_level(WARNING)
    state_value = env_ctx.state_graph.eval_state(
        Bootstrapper_state_client_conf_file_data_loaded_rendered._state_name(),
    )

    # then:

    assert state_value == {}
    assert "does not exist" in caplog.text
