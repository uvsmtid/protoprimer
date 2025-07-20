from unittest.mock import patch

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_env_conf_file_data,
    ConfConstEnv,
    EnvContext,
    EnvState,
)


@pytest.fixture
def env_ctx():
    return EnvContext()


# noinspection PyMethodMayBeStatic
def test_relationship():
    assert_test_module_name_embeds_str(EnvState.state_project_path_list_finalized.name)


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_env_conf_file_data.__name__}._bootstrap_once"
)
def test_py_exec_venv(
    mock_state_env_conf_file_data,
    env_ctx,
):
    # given:

    project_rel_path_list: list[str] = [
        "path/to/project/a",
        "path/to/project/b",
    ]

    mock_state_env_conf_file_data.return_value = {
        ConfConstEnv.field_project_rel_path_list: project_rel_path_list,
    }

    # when:

    ret_val: str = env_ctx.bootstrap_state(
        EnvState.state_project_path_list_finalized.name
    )

    # then:

    assert project_rel_path_list == ret_val
