import os
from unittest.mock import patch

import pytest

from local_test.mock_verifier import (
    assert_parent_factories_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    _Factory_state_local_conf_file_abs_path_inited,
    _Factory_state_local_conf_symlink_abs_path_inited,
    _Node_state_local_conf_file_abs_path_inited_is_app,
    _Node_state_local_conf_file_abs_path_inited_not_is_app,
    _ContextBuilder,
    _EntryFunc,
    _Node_state_primer_conf_file_abs_path_inited,
    _ConfConstClient,
    _EnvContext,
    _EnvState,
)


@pytest.fixture
def env_ctx():
    return _EnvContext()


def test_relationship():
    assert_test_module_name_embeds_str(_EnvState.state_local_conf_file_abs_path_inited.name)


@patch(f"{primer_kernel.__name__}.{_Node_state_primer_conf_file_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{_Factory_state_local_conf_symlink_abs_path_inited.__name__}.create_state_node")
def test_success(
    mock_state_local_conf_symlink_abs_path_inited,
    mock_state_primer_conf_file_abs_path_inited,
    env_ctx,
    fs,
):
    # given:
    assert_parent_factories_mocked(
        env_ctx,
        _EnvState.state_local_conf_file_abs_path_inited.name,
    )

    mock_client_dir = "/mock_client_dir"
    fs.create_dir(mock_client_dir)
    os.chdir(mock_client_dir)

    mock_state_local_conf_symlink_abs_path_inited.return_value.eval_own_state.return_value = os.path.join(
        mock_client_dir,
        _ConfConstClient.default_dir_rel_path_leap_env_link_name,
    )
    mock_state_primer_conf_file_abs_path_inited.return_value.eval_own_state.return_value = "protoprimer.json"

    # when:
    state_local_conf_file_abs_path_inited = env_ctx.eval_state(_EnvState.state_local_conf_file_abs_path_inited.name)

    # then:
    expected_path = os.path.join(
        mock_client_dir,
        _ConfConstClient.default_dir_rel_path_leap_env_link_name,
        _ConfConstClient.default_file_basename_leap_env,
    )
    assert state_local_conf_file_abs_path_inited == expected_path


def test_factory_is_app_node_depends_on_exec_operation_before_symlink():
    # given:
    env_ctx = _ContextBuilder().entry_func(_EntryFunc.func_boot_env).is_app(True).build_context()

    # when:
    state_node = _Factory_state_local_conf_file_abs_path_inited(env_ctx).create_state_node()

    # then: the exec operation selects the `Node` of the symlink state
    assert type(state_node) is _Node_state_local_conf_file_abs_path_inited_is_app
    assert state_node.get_parent_states() == [
        _EnvState.state_input_exec_operation_loaded.name,
        _EnvState.state_primer_conf_file_abs_path_inited.name,
        _EnvState.state_local_conf_symlink_abs_path_inited.name,
    ]


def test_factory_not_is_app_node_does_not_depend_on_exec_operation():
    # given:
    env_ctx = _ContextBuilder().entry_func(_EntryFunc.func_call_lib).is_app(False).build_context()

    # when:
    state_node = _Factory_state_local_conf_file_abs_path_inited(env_ctx).create_state_node()

    # then: `FT_77_15_06_50.dynamic_DAG.md`: the exec operation is not processed outside of `_is_app`
    assert type(state_node) is _Node_state_local_conf_file_abs_path_inited_not_is_app
    assert state_node.get_parent_states() == [
        _EnvState.state_primer_conf_file_abs_path_inited.name,
        _EnvState.state_local_conf_symlink_abs_path_inited.name,
    ]
