from unittest.mock import patch

import pytest

from local_test.mock_verifier import (
    assert_parent_factories_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    EnvContext,
    EnvState,
)


@pytest.fixture
def env_ctx():
    return EnvContext()


def test_relationship():
    assert_test_module_name_embeds_str(EnvState.state_selected_python_file_abs_path_inited.name)


@patch(f"{primer_kernel.__name__}.probe_python_file_abs_path")
@patch(f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_python_selector_file_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_required_python_version_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_client_conf_file_data_loaded.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{primer_kernel.Bootstrapper_state_ref_root_dir_abs_path_inited.__name__}.create_state_node")
def test_python_selection(
    mock_state_ref_root_dir_abs_path_inited,
    mock_state_client_conf_file_data_loaded,
    mock_state_required_python_version_inited,
    mock_state_python_selector_file_abs_path_inited,
    mock_probe_python_file_abs_path,
    env_ctx,
):
    # given
    from protoprimer.primer_kernel import parse_python_version

    assert_parent_factories_mocked(
        env_ctx,
        EnvState.state_selected_python_file_abs_path_inited.name,
    )
    mock_state_required_python_version_inited.return_value.eval_own_state.return_value = "3.10"
    mock_state_python_selector_file_abs_path_inited.return_value.eval_own_state.return_value = "python3.10"
    mock_probe_python_file_abs_path.return_value = "/usr/bin/python3.10"

    # when
    result = env_ctx.state_graph.eval_state(EnvState.state_selected_python_file_abs_path_inited.name)

    # then
    mock_probe_python_file_abs_path.assert_called_once_with("python3.10", parse_python_version("3.10"))
    assert result == "/usr/bin/python3.10"
