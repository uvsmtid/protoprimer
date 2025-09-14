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
from test_protoprimer.misc_tools.mock_verifier import assert_parent_states_mocked


@pytest.fixture
def env_ctx():
    return EnvContext()


def test_relationship():
    assert_test_module_name_embeds_str(
        EnvState.state_env_project_descriptors_eval_finalized.name
    )


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_env_conf_file_data.__name__}.eval_own_state"
)
def test_py_exec_venv(
    mock_state_env_conf_file_data,
    env_ctx,
):
    # given:

    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_env_project_descriptors_eval_finalized,
    )

    project_descriptors: list[dict] = [
        {
            ConfField.field_env_build_root_dir_rel_path.value: "path/to/project/a",
            ConfField.field_env_install_extras.value: [],
        },
        {
            ConfField.field_env_build_root_dir_rel_path.value: "path/to/project/b",
            ConfField.field_env_install_extras.value: ["test"],
        },
    ]

    mock_state_env_conf_file_data.return_value = {
        ConfField.field_env_project_descriptors.value: project_descriptors,
    }

    # when:

    ret_val: str = env_ctx.state_graph.eval_state(
        EnvState.state_env_project_descriptors_eval_finalized.name
    )

    # then:

    assert project_descriptors == ret_val
