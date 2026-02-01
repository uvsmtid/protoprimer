import os
from unittest.mock import patch

import pytest

from local_test.mock_verifier import (
    assert_parent_states_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_input_py_exec_var_loaded,
    Bootstrapper_state_input_start_id_var_loaded,
    Bootstrapper_state_input_run_mode_arg_loaded,
    ConfConstInput,
    EnvContext,
    EnvState,
    StateStride,
)


@pytest.fixture
def env_ctx():
    return EnvContext()


def test_relationship():
    assert_test_module_name_embeds_str(EnvState.state_stride_py_arbitrary_reached.name)


@patch.dict(
    f"{os.__name__}.environ",
    {
        ConfConstInput.ext_env_var_VIRTUAL_ENV: "/path/to/venv",
        ConfConstInput.ext_env_var_PATH: "/path/to/venv/bin:/usr/bin",
    },
    clear=True,
)
@patch(
    f"{primer_kernel.__name__}.EnvContext.set_max_stride",
    return_value=StateStride.stride_py_arbitrary,
)
@patch(f"{primer_kernel.__name__}.get_path_to_curr_python")
@patch(f"{primer_kernel.__name__}.get_path_to_base_python")
@patch(f"{primer_kernel.__name__}.switch_python")
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_run_mode_arg_loaded.__name__}.eval_own_state"
)
def test_py_exec_stride_py_unknown_in_venv(
    mock_state_input_run_mode_arg_loaded,
    mock_state_input_start_id_var_loaded,
    mock_switch_python,
    mock_get_path_to_base_python,
    mock_get_path_to_curr_python,
    mock_set_max_stride,
    env_ctx,
):
    # given:

    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_stride_py_arbitrary_reached.name,
    )

    mock_state_input_start_id_var_loaded.return_value = "mock_start_id"

    mock_get_path_to_curr_python.return_value = "/path/to/venv/bin/python"
    mock_get_path_to_base_python.return_value = "/usr/bin/python"

    mock_switch_python.return_value = StateStride.stride_py_arbitrary

    # when:

    state_value = env_ctx.state_graph.eval_state(
        EnvState.state_stride_py_arbitrary_reached.name
    )

    # then:

    assert state_value == StateStride.stride_py_arbitrary

    mock_switch_python.assert_called_once_with(
        curr_python_path=mock_get_path_to_curr_python.return_value,
        next_py_exec=StateStride.stride_py_arbitrary,
        next_python_path=mock_get_path_to_base_python.return_value,
        start_id="mock_start_id",
        proto_code_abs_file_path=None,
        required_environ={
            ConfConstInput.ext_env_var_PATH: "/usr/bin",
            # NOTE: No more `ConfConstInput.ext_env_var_VIRTUAL_ENV`.
        },
    )


@patch.dict(
    f"{os.__name__}.environ",
    {
        # NOTE: Even if `venv` is part of the `PATH`, it is not detectable:
        ConfConstInput.ext_env_var_PATH: "/path/to/venv/bin:/usr/bin",
    },
    clear=True,
)
@patch(
    f"{primer_kernel.__name__}.EnvContext.set_max_stride",
    return_value=StateStride.stride_py_arbitrary,
)
@patch(f"{primer_kernel.__name__}.get_path_to_curr_python")
@patch(f"{primer_kernel.__name__}.get_path_to_base_python")
@patch(f"{primer_kernel.__name__}.switch_python")
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_run_mode_arg_loaded.__name__}.eval_own_state"
)
def test_py_exec_stride_py_unknown_not_in_venv(
    mock_state_input_run_mode_arg_loaded,
    mock_state_input_start_id_var_loaded,
    mock_switch_python,
    mock_get_path_to_base_python,
    mock_get_path_to_curr_python,
    mock_set_max_stride,
    env_ctx,
):
    # given:

    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_stride_py_arbitrary_reached.name,
    )

    mock_state_input_start_id_var_loaded.return_value = "mock_start_id"

    mock_get_path_to_curr_python.return_value = "/usr/bin/python"
    mock_get_path_to_base_python.return_value = "/usr/bin/python"

    mock_switch_python.return_value = StateStride.stride_py_arbitrary

    # when:

    state_value = env_ctx.state_graph.eval_state(
        EnvState.state_stride_py_arbitrary_reached.name
    )

    # then:

    assert state_value == StateStride.stride_py_arbitrary

    mock_switch_python.assert_called_once_with(
        curr_python_path=mock_get_path_to_curr_python.return_value,
        next_py_exec=StateStride.stride_py_arbitrary,
        next_python_path=mock_get_path_to_base_python.return_value,
        start_id="mock_start_id",
        proto_code_abs_file_path=None,
        required_environ={
            ConfConstInput.ext_env_var_PATH: "/path/to/venv/bin:/usr/bin",
        },
    )
