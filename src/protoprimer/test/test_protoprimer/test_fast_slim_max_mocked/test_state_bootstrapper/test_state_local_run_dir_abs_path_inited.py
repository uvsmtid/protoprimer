import os
from unittest.mock import patch

import pytest

from local_test.mock_verifier import assert_parent_factories_mocked
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_client_conf_file_data_loaded,
    Bootstrapper_state_env_conf_file_data_loaded,
    Bootstrapper_state_ref_root_dir_abs_path_inited,
    ConfConstEnv,
    ConfField,
    EnvContext,
    EnvState,
)


@pytest.fixture
def env_ctx():
    return EnvContext()


def test_relationship():
    assert_test_module_name_embeds_str(EnvState.state_local_run_dir_abs_path_inited.name)


@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_env_conf_file_data_loaded.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data_loaded.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_ref_root_dir_abs_path_inited.__name__}.create_state_node")
def test_default_when_field_absent(
    mock_state_ref_root_dir_abs_path_inited,
    mock_state_client_conf_file_data_loaded,
    mock_state_env_conf_file_data_loaded,
    env_ctx,
):
    # given:
    assert_parent_factories_mocked(
        env_ctx,
        EnvState.state_local_run_dir_abs_path_inited.name,
    )
    ref_root_abs_path = os.path.normpath("/ref_root")
    mock_state_ref_root_dir_abs_path_inited.return_value.eval_own_state.return_value = ref_root_abs_path
    mock_state_client_conf_file_data_loaded.return_value.eval_own_state.return_value = {}
    mock_state_env_conf_file_data_loaded.return_value.eval_own_state.return_value = {}

    # when:
    result = env_ctx.eval_state(EnvState.state_local_run_dir_abs_path_inited.name)

    # then:
    assert result == os.path.join(ref_root_abs_path, ConfConstEnv.default_dir_rel_path_run)


@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_env_conf_file_data_loaded.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data_loaded.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_ref_root_dir_abs_path_inited.__name__}.create_state_node")
def test_client_conf_overrides_default(
    mock_state_ref_root_dir_abs_path_inited,
    mock_state_client_conf_file_data_loaded,
    mock_state_env_conf_file_data_loaded,
    env_ctx,
):
    # given:
    assert_parent_factories_mocked(
        env_ctx,
        EnvState.state_local_run_dir_abs_path_inited.name,
    )
    ref_root_abs_path = os.path.normpath("/ref_root")
    mock_state_ref_root_dir_abs_path_inited.return_value.eval_own_state.return_value = ref_root_abs_path
    mock_state_client_conf_file_data_loaded.return_value.eval_own_state.return_value = {
        ConfField.field_local_run_dir_rel_path.value: "client_run",
    }
    mock_state_env_conf_file_data_loaded.return_value.eval_own_state.return_value = {}

    # when:
    result = env_ctx.eval_state(EnvState.state_local_run_dir_abs_path_inited.name)

    # then:
    assert result == os.path.join(ref_root_abs_path, "client_run")


@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_env_conf_file_data_loaded.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data_loaded.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_ref_root_dir_abs_path_inited.__name__}.create_state_node")
def test_env_conf_overrides_client_conf(
    mock_state_ref_root_dir_abs_path_inited,
    mock_state_client_conf_file_data_loaded,
    mock_state_env_conf_file_data_loaded,
    env_ctx,
):
    # given:
    assert_parent_factories_mocked(
        env_ctx,
        EnvState.state_local_run_dir_abs_path_inited.name,
    )
    ref_root_abs_path = os.path.normpath("/ref_root")
    mock_state_ref_root_dir_abs_path_inited.return_value.eval_own_state.return_value = ref_root_abs_path
    mock_state_client_conf_file_data_loaded.return_value.eval_own_state.return_value = {
        ConfField.field_local_run_dir_rel_path.value: "client_run",
    }
    mock_state_env_conf_file_data_loaded.return_value.eval_own_state.return_value = {
        ConfField.field_local_run_dir_rel_path.value: "env_run",
    }

    # when:
    result = env_ctx.eval_state(EnvState.state_local_run_dir_abs_path_inited.name)

    # then:
    assert result == os.path.join(ref_root_abs_path, "env_run")
