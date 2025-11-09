import os
from unittest.mock import patch
import pytest
from logging import WARNING

from local_test.mock_verifier import assert_parent_states_mocked
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_input_proto_code_dir_abs_path_eval_finalized,
    Bootstrapper_state_proto_conf_file_data,
    ConfField,
    EnvContext,
    EnvState,
    SyntaxArg,
)


@pytest.fixture
def env_ctx():
    return EnvContext()


@pytest.fixture
def mock_proto_code_dir(fs):
    path = "/path/to/proto/code"
    fs.create_dir(path)
    return path


def test_relationship():
    assert_test_module_name_embeds_str(
        EnvState.state_primer_ref_root_dir_abs_path_eval_finalized.name
    )


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_proto_code_dir_abs_path_eval_finalized.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_proto_conf_file_data.__name__}.eval_own_state"
)
def test_success_when_field_present(
    mock_state_proto_conf_file_data,
    mock_state_input_proto_code_dir_abs_path_eval_finalized,
    env_ctx,
    mock_proto_code_dir,
):
    # given:
    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_primer_ref_root_dir_abs_path_eval_finalized.name,
    )
    mock_state_input_proto_code_dir_abs_path_eval_finalized.return_value = (
        mock_proto_code_dir
    )

    ref_root_rel_path = "../../ref_root"
    ref_root_abs_path = os.path.normpath(
        os.path.join(mock_proto_code_dir, ref_root_rel_path)
    )

    primer_conf_data = {
        ConfField.field_primer_ref_root_dir_rel_path.value: ref_root_rel_path
    }
    mock_state_proto_conf_file_data.return_value = primer_conf_data

    # when:
    result = env_ctx.state_graph.eval_state(
        EnvState.state_primer_ref_root_dir_abs_path_eval_finalized.name
    )

    # then:
    assert result == ref_root_abs_path


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_proto_code_dir_abs_path_eval_finalized.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_proto_conf_file_data.__name__}.eval_own_state"
)
def test_warning_when_field_missing(
    mock_state_proto_conf_file_data,
    mock_state_input_proto_code_dir_abs_path_eval_finalized,
    env_ctx,
    mock_proto_code_dir,
    caplog,
):
    # given:
    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_primer_ref_root_dir_abs_path_eval_finalized.name,
    )
    mock_state_input_proto_code_dir_abs_path_eval_finalized.return_value = (
        mock_proto_code_dir
    )

    mock_state_proto_conf_file_data.return_value = {}

    # when:
    caplog.set_level(WARNING)
    result = env_ctx.state_graph.eval_state(
        EnvState.state_primer_ref_root_dir_abs_path_eval_finalized.name
    )

    # then:
    assert result == mock_proto_code_dir
    assert (
        f"Field `{ConfField.field_primer_ref_root_dir_rel_path.value}` is [None] - re-run with [{SyntaxArg.arg_mode_wizard}] to set it."
        in caplog.text
    )
