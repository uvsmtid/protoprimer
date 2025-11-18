import os
from logging import WARNING
from unittest.mock import patch

import pytest

from local_test.mock_verifier import assert_parent_states_mocked
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized,
    Bootstrapper_state_primer_conf_file_data_loaded,
    ConfField,
    EnvContext,
    EnvState,
    SyntaxArg,
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
    f"{primer_kernel.__name__}.{Bootstrapper_state_primer_conf_file_data_loaded.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized.__name__}.eval_own_state"
)
def test_success_when_field_present(
    mock_state_primer_ref_root_dir_abs_path_eval_finalized,
    mock_state_primer_conf_file_data_loaded,
    env_ctx,
    mock_ref_root,
):
    # given:
    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_primer_conf_client_file_abs_path_eval_finalized.name,
    )
    mock_state_primer_ref_root_dir_abs_path_eval_finalized.return_value = mock_ref_root

    client_conf_rel_path = "client.conf.json"
    client_conf_abs_path = os.path.join(mock_ref_root, client_conf_rel_path)

    proto_conf_data = {
        ConfField.field_primer_conf_client_file_rel_path.value: client_conf_rel_path
    }
    mock_state_primer_conf_file_data_loaded.return_value = proto_conf_data

    # when:
    result = env_ctx.state_graph.eval_state(
        EnvState.state_primer_conf_client_file_abs_path_eval_finalized.name
    )

    # then:
    assert result == client_conf_abs_path


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_primer_conf_file_data_loaded.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized.__name__}.eval_own_state"
)
def test_warning_when_field_missing(
    mock_state_primer_ref_root_dir_abs_path_eval_finalized,
    mock_state_primer_conf_file_data_loaded,
    env_ctx,
    mock_ref_root,
    caplog,
):
    # given:
    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_primer_conf_client_file_abs_path_eval_finalized.name,
    )
    mock_state_primer_ref_root_dir_abs_path_eval_finalized.return_value = mock_ref_root
    mock_state_primer_conf_file_data_loaded.return_value = {}

    # when:
    caplog.set_level(WARNING)
    result = env_ctx.state_graph.eval_state(
        EnvState.state_primer_conf_client_file_abs_path_eval_finalized.name
    )

    # then:
    assert result is None
    assert (
        f"Field `{ConfField.field_primer_conf_client_file_rel_path.value}` is [None] - re-run with [{SyntaxArg.arg_mode_wizard}] to set it."
        in caplog.text
    )
