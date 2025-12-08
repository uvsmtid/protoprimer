import os
from unittest.mock import patch

import pytest

from local_test.mock_verifier import assert_parent_states_mocked
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_primer_conf_file_abs_path_inited,
    Bootstrapper_state_global_conf_dir_abs_path_inited,
    ConfConstPrimer,
    EnvContext,
    EnvState,
)


@pytest.fixture
def env_ctx():
    return EnvContext()


@pytest.fixture
def mock_ref_root(fs):
    path = "/mock_ref_root"
    fs.create_dir(path)
    return path


def test_relationship():
    assert_test_module_name_embeds_str(
        EnvState.state_global_conf_file_abs_path_inited.name
    )


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_primer_conf_file_abs_path_inited.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_global_conf_dir_abs_path_inited.__name__}.eval_own_state"
)
def test_success_when_field_present(
    mock_state_global_conf_dir_abs_path_inited,
    mock_state_primer_conf_file_abs_path_inited,
    env_ctx,
    mock_ref_root,
):
    # given:

    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_global_conf_file_abs_path_inited.name,
    )

    mock_state_global_conf_dir_abs_path_inited.return_value = os.path.join(
        mock_ref_root,
        ConfConstPrimer.default_client_conf_dir_rel_path,
    )

    mock_state_primer_conf_file_abs_path_inited.return_value = os.path.join(
        mock_ref_root,
        ConfConstPrimer.default_client_conf_dir_rel_path,
        "some_basename.json",
    )

    client_conf_abs_path = os.path.join(
        mock_ref_root,
        mock_state_primer_conf_file_abs_path_inited.return_value,
    )

    # when:
    state_global_conf_file_abs_path_inited = env_ctx.state_graph.eval_state(
        EnvState.state_global_conf_file_abs_path_inited.name
    )

    # then:
    assert state_global_conf_file_abs_path_inited == client_conf_abs_path
