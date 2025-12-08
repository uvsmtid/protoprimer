from unittest.mock import patch

import pytest

from local_test.mock_verifier import (
    assert_parent_states_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_input_proto_code_file_abs_path_var_loaded,
    Bootstrapper_state_py_exec_arbitrary_reached,
    EnvContext,
    EnvState,
    PythonExecutable,
)


@pytest.fixture
def env_ctx():
    return EnvContext()


def test_relationship():
    assert_test_module_name_embeds_str(
        EnvState.state_proto_code_file_abs_path_inited.name
    )


@patch(f"{primer_kernel.__name__}.is_venv")
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_arbitrary_reached.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_proto_code_file_abs_path_var_loaded.__name__}.eval_own_state"
)
def test_py_exec_arbitrary_not_in_venv(
    mock_state_input_proto_code_file_abs_path_var_loaded,
    mock_state_py_exec_arbitrary_reached,
    mock_is_venv,
    env_ctx,
):
    # given:

    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_proto_code_file_abs_path_inited.name,
    )

    mock_state_py_exec_arbitrary_reached.return_value = (
        PythonExecutable.py_exec_arbitrary
    )

    mock_is_venv.return_value = False

    # when:

    state_value: str = env_ctx.state_graph.eval_state(
        EnvState.state_proto_code_file_abs_path_inited.name
    )

    # then:

    assert state_value == primer_kernel.__file__


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_arbitrary_reached.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_proto_code_file_abs_path_var_loaded.__name__}.eval_own_state"
)
def test_py_exec_venv(
    mock_state_input_proto_code_file_abs_path_var_loaded,
    mock_state_py_exec_arbitrary_reached,
    env_ctx,
):
    # given:

    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_proto_code_file_abs_path_inited.name,
    )

    proto_code_abs_file_path = "/path/to/proto_kernel.py"

    mock_state_input_proto_code_file_abs_path_var_loaded.return_value = (
        proto_code_abs_file_path
    )
    mock_state_py_exec_arbitrary_reached.return_value = PythonExecutable.py_exec_venv

    # when:

    state_value: str = env_ctx.state_graph.eval_state(
        EnvState.state_proto_code_file_abs_path_inited.name
    )

    # then:

    assert state_value == proto_code_abs_file_path


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_proto_code_file_abs_path_var_loaded.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_arbitrary_reached.__name__}.eval_own_state"
)
def test_py_exec_venv_no_arg(
    mock_state_py_exec_arbitrary_reached,
    mock_state_input_proto_code_file_abs_path_var_loaded,
    env_ctx,
):
    # given:

    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_proto_code_file_abs_path_inited.name,
    )

    mock_state_input_proto_code_file_abs_path_var_loaded.return_value = None
    mock_state_py_exec_arbitrary_reached.return_value = PythonExecutable.py_exec_venv

    # when/then:

    with pytest.raises(AssertionError) as exc_info:
        env_ctx.state_graph.eval_state(
            EnvState.state_proto_code_file_abs_path_inited.name
        )

    assert "is not specified at" in str(exc_info.value)
