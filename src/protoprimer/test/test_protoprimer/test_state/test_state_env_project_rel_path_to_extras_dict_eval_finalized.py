from unittest.mock import patch

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_env_conf_file_data,
    ConfField,
    EnvContext,
    EnvState,
)


@pytest.fixture
def env_ctx():
    return EnvContext()


def test_relationship():
    assert_test_module_name_embeds_str(
        EnvState.state_env_project_rel_path_to_extras_dict_eval_finalized.name
    )


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_env_conf_file_data.__name__}._bootstrap_once"
)
def test_py_exec_venv(
    mock_state_env_conf_file_data,
    env_ctx,
):
    # given:

    project_rel_path_to_extras_dict: list[str] = {
        "path/to/project/a": [],
        "path/to/project/b": ["test"],
    }

    mock_state_env_conf_file_data.return_value = {
        ConfField.field_env_project_rel_path_to_extras_dict.value: project_rel_path_to_extras_dict,
    }

    # when:

    ret_val: str = env_ctx.bootstrap_state(
        EnvState.state_env_project_rel_path_to_extras_dict_eval_finalized.name
    )

    # then:

    assert project_rel_path_to_extras_dict == ret_val
