import os
from unittest.mock import patch

import pytest

from local_test.mock_verifier import (
    assert_parent_states_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_local_conf_symlink_abs_path_inited,
    Bootstrapper_state_primer_conf_file_abs_path_inited,
    ConfConstClient,
    EnvContext,
    EnvState,
)


@pytest.fixture
def env_ctx():
    return EnvContext()


def test_relationship():
    assert_test_module_name_embeds_str(
        EnvState.state_local_conf_file_abs_path_inited.name
    )


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_primer_conf_file_abs_path_inited.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_symlink_abs_path_inited.__name__}.eval_own_state"
)
def test_success(
    mock_state_local_conf_symlink_abs_path_inited,
    mock_state_primer_conf_file_abs_path_inited,
    env_ctx,
    fs,
):
    # given:
    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_local_conf_file_abs_path_inited.name,
    )

    mock_client_dir = "/mock_client_dir"
    fs.create_dir(mock_client_dir)
    os.chdir(mock_client_dir)

    mock_state_local_conf_symlink_abs_path_inited.return_value = os.path.join(
        mock_client_dir,
        ConfConstClient.default_dir_rel_path_leap_env_link_name,
    )
    mock_state_primer_conf_file_abs_path_inited.return_value = "protoprimer.json"

    # when:
    state_local_conf_file_abs_path_inited = env_ctx.state_graph.eval_state(
        EnvState.state_local_conf_file_abs_path_inited.name
    )

    # then:
    expected_path = os.path.join(
        mock_client_dir,
        ConfConstClient.default_dir_rel_path_leap_env_link_name,
        ConfConstClient.default_file_basename_leap_env,
    )
    assert state_local_conf_file_abs_path_inited == expected_path
