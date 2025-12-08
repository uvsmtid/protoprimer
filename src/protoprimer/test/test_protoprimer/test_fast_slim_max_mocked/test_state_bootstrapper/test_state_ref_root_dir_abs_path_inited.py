import os
from logging import WARNING
from unittest.mock import patch

import pytest

from local_test.mock_verifier import assert_parent_states_mocked
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_proto_code_file_abs_path_inited,
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
def mock_proto_code_dir(fs):
    path = "/path/to/proto/code"
    fs.create_dir(path)
    return os.path.join(path, "proto_kernel.py")


def test_relationship():
    assert_test_module_name_embeds_str(EnvState.state_ref_root_dir_abs_path_inited.name)


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_file_abs_path_inited.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_primer_conf_file_data_loaded.__name__}.eval_own_state"
)
def test_success_when_field_present(
    mock_state_primer_conf_file_data_loaded,
    state_proto_code_file_abs_path_inited,
    env_ctx,
    mock_proto_code_dir,
):
    # given:
    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_ref_root_dir_abs_path_inited.name,
    )
    state_proto_code_file_abs_path_inited.return_value = mock_proto_code_dir

    ref_root_rel_path = "../../ref_root"
    ref_root_abs_path = os.path.normpath(
        os.path.join(os.path.dirname(mock_proto_code_dir), ref_root_rel_path)
    )

    primer_conf_data = {ConfField.field_ref_root_dir_rel_path.value: ref_root_rel_path}
    mock_state_primer_conf_file_data_loaded.return_value = primer_conf_data

    # when:
    result = env_ctx.state_graph.eval_state(
        EnvState.state_ref_root_dir_abs_path_inited.name
    )

    # then:
    assert result == ref_root_abs_path


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_file_abs_path_inited.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_primer_conf_file_data_loaded.__name__}.eval_own_state"
)
def test_warning_when_field_missing(
    mock_state_primer_conf_file_data_loaded,
    state_proto_code_file_abs_path_inited,
    env_ctx,
    mock_proto_code_dir,
    caplog,
):
    # given:
    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_ref_root_dir_abs_path_inited.name,
    )
    state_proto_code_file_abs_path_inited.return_value = mock_proto_code_dir

    mock_state_primer_conf_file_data_loaded.return_value = {}

    # when:
    caplog.set_level(WARNING)
    result = env_ctx.state_graph.eval_state(
        EnvState.state_ref_root_dir_abs_path_inited.name
    )

    # then:
    assert result == os.path.dirname(mock_proto_code_dir)
    assert (
        f"Field `{ConfField.field_ref_root_dir_rel_path.value}` is [None] - use [{SyntaxArg.arg_mode_config}] for description."
        in caplog.text
    )
