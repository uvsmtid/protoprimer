import os
from unittest.mock import patch

import pytest

from local_test.mock_verifier import (
    assert_parent_states_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_client_conf_env_dir_abs_path_eval_finalized,
    Bootstrapper_state_client_link_name_dir_rel_path_eval_finalized,
    Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized,
    ConfConstClient,
    EnvContext,
    EnvState,
)


@pytest.fixture
def env_ctx():
    return EnvContext()


def test_relationship():
    assert_test_module_name_embeds_str(
        EnvState.state_client_conf_env_file_abs_path_eval_finalized.name
    )


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_client_link_name_dir_rel_path_eval_finalized.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_env_dir_abs_path_eval_finalized.__name__}.eval_own_state"
)
def test_success_when_all_parent_states_are_set(
    mock_state_client_conf_env_dir_abs_path_eval_finalized,
    mock_state_primer_ref_root_dir_abs_path_eval_finalized,
    mock_state_client_link_name_dir_rel_path_eval_finalized,
    env_ctx,
    fs,
):
    # given:
    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_client_conf_env_file_abs_path_eval_finalized.name,
    )

    mock_client_dir = "/mock_client_dir"
    fs.create_dir(mock_client_dir)
    os.chdir(mock_client_dir)

    mock_state_primer_ref_root_dir_abs_path_eval_finalized.return_value = (
        mock_client_dir
    )
    mock_state_client_conf_env_dir_abs_path_eval_finalized.return_value = os.path.join(
        mock_client_dir,
        ConfConstClient.default_dir_rel_path_leap_env_link_name,
    )
    mock_state_client_link_name_dir_rel_path_eval_finalized.return_value = (
        ConfConstClient.default_dir_rel_path_leap_env_link_name
    )

    # when:
    state_client_conf_env_file_abs_path_eval_finalized = env_ctx.state_graph.eval_state(
        EnvState.state_client_conf_env_file_abs_path_eval_finalized.name
    )

    # then:
    expected_path = os.path.join(
        mock_client_dir,
        ConfConstClient.default_dir_rel_path_leap_env_link_name,
        ConfConstClient.default_file_basename_leap_env,
    )
    assert state_client_conf_env_file_abs_path_eval_finalized == expected_path


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_client_link_name_dir_rel_path_eval_finalized.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_env_dir_abs_path_eval_finalized.__name__}.eval_own_state"
)
def test_failure_when_path_is_not_sub_path(
    mock_state_client_conf_env_dir_abs_path_eval_finalized,
    mock_state_primer_ref_root_dir_abs_path_eval_finalized,
    mock_state_client_link_name_dir_rel_path_eval_finalized,
    env_ctx,
    fs,
):
    # given:
    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_client_conf_env_file_abs_path_eval_finalized.name,
    )

    mock_client_dir = "/mock_client_dir"
    fs.create_dir(mock_client_dir)
    os.chdir(mock_client_dir)

    # This will cause the path to be outside:
    mock_state_primer_ref_root_dir_abs_path_eval_finalized.return_value = "/another_dir"
    mock_state_client_conf_env_dir_abs_path_eval_finalized.return_value = os.path.join(
        mock_client_dir,
        ConfConstClient.default_dir_rel_path_leap_env_link_name,
    )
    mock_state_client_link_name_dir_rel_path_eval_finalized.return_value = (
        ConfConstClient.default_dir_rel_path_leap_env_link_name
    )

    # when/then:
    with pytest.raises(AssertionError) as excinfo:
        env_ctx.state_graph.eval_state(
            EnvState.state_client_conf_env_file_abs_path_eval_finalized.name
        )
    assert "is not under the config dir path" in str(excinfo.value)


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_client_link_name_dir_rel_path_eval_finalized.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_env_dir_abs_path_eval_finalized.__name__}.eval_own_state"
)
def test_success_when_link_name_is_none(
    mock_state_client_conf_env_dir_abs_path_eval_finalized,
    mock_state_primer_ref_root_dir_abs_path_eval_finalized,
    mock_state_client_link_name_dir_rel_path_eval_finalized,
    env_ctx,
    fs,
):
    # given:
    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_client_conf_env_file_abs_path_eval_finalized.name,
    )

    mock_client_dir = "/mock_client_dir"
    fs.create_dir(mock_client_dir)

    mock_state_primer_ref_root_dir_abs_path_eval_finalized.return_value = (
        mock_client_dir
    )
    mock_state_client_conf_env_dir_abs_path_eval_finalized.return_value = (
        mock_client_dir
    )
    mock_state_client_link_name_dir_rel_path_eval_finalized.return_value = None

    # when:
    result = env_ctx.state_graph.eval_state(
        EnvState.state_client_conf_env_file_abs_path_eval_finalized.name
    )

    # then:
    expected_path = os.path.join(
        mock_client_dir,
        ConfConstClient.default_file_basename_leap_env,
    )
    assert result == expected_path
