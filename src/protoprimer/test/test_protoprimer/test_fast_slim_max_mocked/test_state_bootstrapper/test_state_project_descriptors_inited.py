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
    ConfField,
    EnvContext,
    EnvState,
)


@pytest.fixture
def env_ctx():
    return EnvContext()


def test_relationship():
    assert_test_module_name_embeds_str(EnvState.state_project_descriptors_inited.name)


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data_loaded.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_env_conf_file_data_loaded.__name__}.eval_own_state"
)
def test_stride_py_venv(
    mock_state_env_conf_file_data_loaded,
    mock_state_client_conf_file_data_loaded,
    env_ctx,
):
    # given:

    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_project_descriptors_inited.name,
    )

    project_descriptors: list[dict] = [
        {
            ConfField.field_build_root_dir_rel_path.value: "path/to/project/a",
            ConfField.field_install_extras.value: [],
        },
        {
            ConfField.field_build_root_dir_rel_path.value: "path/to/project/b",
            ConfField.field_install_extras.value: ["test"],
        },
    ]

    mock_state_client_conf_file_data_loaded.return_value = {}

    mock_state_env_conf_file_data_loaded.return_value = {
        ConfField.field_project_descriptors.value: project_descriptors,
    }

    # when:

    state_value: str = env_ctx.state_graph.eval_state(
        EnvState.state_project_descriptors_inited.name
    )

    # then:

    assert project_descriptors == state_value
