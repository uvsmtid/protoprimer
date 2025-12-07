import os
from unittest.mock import patch

import pytest

from local_test.mock_verifier import assert_parent_states_mocked
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_input_proto_conf_primer_file_abs_path_eval_finalized,
    Bootstrapper_state_primer_conf_client_dir_abs_path_eval_finalized,
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
        EnvState.state_primer_conf_client_file_abs_path_eval_finalized.name
    )


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_proto_conf_primer_file_abs_path_eval_finalized.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_primer_conf_client_dir_abs_path_eval_finalized.__name__}.eval_own_state"
)
def test_success_when_field_present(
    mock_state_primer_conf_client_dir_abs_path_eval_finalized,
    mock_state_input_proto_conf_primer_file_abs_path_eval_finalized,
    env_ctx,
    mock_ref_root,
):
    # given:

    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_primer_conf_client_file_abs_path_eval_finalized.name,
    )

    mock_state_primer_conf_client_dir_abs_path_eval_finalized.return_value = (
        os.path.join(
            mock_ref_root,
            ConfConstPrimer.default_client_conf_dir_rel_path,
        )
    )

    mock_state_input_proto_conf_primer_file_abs_path_eval_finalized.return_value = (
        os.path.join(
            mock_ref_root,
            ConfConstPrimer.default_client_conf_dir_rel_path,
            "some_basename.json",
        )
    )

    client_conf_abs_path = os.path.join(
        mock_ref_root,
        mock_state_input_proto_conf_primer_file_abs_path_eval_finalized.return_value,
    )

    # when:
    state_primer_conf_client_file_abs_path_eval_finalized = (
        env_ctx.state_graph.eval_state(
            EnvState.state_primer_conf_client_file_abs_path_eval_finalized.name
        )
    )

    # then:
    assert state_primer_conf_client_file_abs_path_eval_finalized == client_conf_abs_path
