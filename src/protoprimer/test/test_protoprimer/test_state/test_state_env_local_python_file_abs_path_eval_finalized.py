import os
from unittest.mock import patch

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_env_conf_file_data,
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
        EnvState.state_env_local_python_file_abs_path_eval_finalized.name
    )


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_env_conf_file_data.__name__}._bootstrap_once"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized.__name__}._bootstrap_once"
)
# TODO: if `rel, it should not be named `abs` - see: ConfConstEnv.field_env_local_python_file_abs_path.value
def test_allow_rel_file_abs_path_python(
    mock_state_primer_ref_root_dir_abs_path_eval_finalized,
    mock_state_env_conf_file_data,
    env_ctx,
):

    # given:

    mock_state_primer_ref_root_dir_abs_path_eval_finalized.return_value = (
        "/abs/to/ref/dir"
    )

    rel_path_to_python = "rel/path/to/python"

    mock_state_env_conf_file_data.return_value = {
        ConfField.field_env_local_python_file_abs_path.value: rel_path_to_python,
    }

    # when:

    ret_val: str = env_ctx.bootstrap_state(
        EnvState.state_env_local_python_file_abs_path_eval_finalized.name
    )

    # then:

    assert ret_val == os.path.join(
        mock_state_primer_ref_root_dir_abs_path_eval_finalized.return_value,
        rel_path_to_python,
    )
