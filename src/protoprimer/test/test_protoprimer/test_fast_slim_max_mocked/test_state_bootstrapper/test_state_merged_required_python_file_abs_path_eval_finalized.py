import os
from unittest.mock import patch

import pytest

from local_test.mock_verifier import (
    assert_parent_states_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_client_conf_file_data_loaded,
    Bootstrapper_state_env_conf_file_data_loaded,
    Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized,
    ConfField,
    EnvContext,
    EnvState,
)


@pytest.fixture
def env_ctx():
    return EnvContext()


def test_relationship():
    assert_test_module_name_embeds_str(
        EnvState.state_merged_required_python_file_abs_path_eval_finalized.name
    )


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data_loaded.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_env_conf_file_data_loaded.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized.__name__}.eval_own_state"
)
# TODO: if `rel` is possible, the field should not be named `abs`, but `any` instead - see: ConfConstEnv.field_required_python_file_abs_path.value
def test_allow_rel_path_for_required_python_abs_path(
    mock_state_primer_ref_root_dir_abs_path_eval_finalized,
    mock_state_env_conf_file_data_loaded,
    mock_state_client_conf_file_data_loaded,
    env_ctx,
):

    # given:

    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_merged_required_python_file_abs_path_eval_finalized.name,
    )

    mock_state_primer_ref_root_dir_abs_path_eval_finalized.return_value = (
        "/abs/to/ref/dir"
    )

    rel_path_to_python = "rel/path/to/python"

    mock_state_client_conf_file_data_loaded.return_value = {}
    mock_state_env_conf_file_data_loaded.return_value = {
        ConfField.field_required_python_file_abs_path.value: rel_path_to_python,
    }

    # when:

    state_value: str = env_ctx.state_graph.eval_state(
        EnvState.state_merged_required_python_file_abs_path_eval_finalized.name
    )

    # then:

    assert state_value == os.path.join(
        mock_state_primer_ref_root_dir_abs_path_eval_finalized.return_value,
        rel_path_to_python,
    )
