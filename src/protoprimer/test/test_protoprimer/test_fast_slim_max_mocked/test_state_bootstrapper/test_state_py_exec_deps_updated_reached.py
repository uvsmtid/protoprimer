import argparse
from unittest.mock import patch

import pytest

from local_test.mock_verifier import (
    assert_parent_states_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_args_parsed,
    Bootstrapper_state_proto_code_file_abs_path_inited,
    Bootstrapper_state_input_py_exec_var_loaded,
    Bootstrapper_state_input_start_id_var_loaded,
    Bootstrapper_state_version_constraints_generated,
    EnvContext,
    EnvState,
    ParsedArg,
    PythonExecutable,
)


@pytest.fixture
def env_ctx():
    return EnvContext()


def test_relationship():
    assert_test_module_name_embeds_str(EnvState.state_py_exec_deps_updated_reached.name)


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
)
@patch(f"{primer_kernel.__name__}.get_path_to_curr_python")
@patch(f"{primer_kernel.__name__}.switch_python")
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_file_abs_path_inited.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_py_exec_var_loaded.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_version_constraints_generated.__name__}.eval_own_state"
)
def test_py_exec_required(
    mock_state_version_constraints_generated,
    mock_state_input_py_exec_var_loaded,
    mock_state_proto_code_file_abs_path_inited,
    mock_switch_python,
    mock_get_path_to_curr_python,
    mock_state_args_parsed,
    mock_state_input_start_id_var_loaded,
    env_ctx,
):

    # given:

    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_py_exec_deps_updated_reached.name,
    )

    mock_state_args_parsed.return_value = argparse.Namespace(
        **{
            ParsedArg.name_reinstall.value: False,
        }
    )
    mock_state_input_start_id_var_loaded.return_value = "mock_start_id"

    mock_state_version_constraints_generated.return_value = True

    mock_state_input_py_exec_var_loaded.return_value = PythonExecutable.py_exec_required

    mock_state_proto_code_file_abs_path_inited.return_value = "path/to/whatever"

    mock_get_path_to_curr_python.return_value = "/path/to/venv/bin/python"

    # when:

    state_value = env_ctx.state_graph.eval_state(
        EnvState.state_py_exec_deps_updated_reached.name
    )

    # then:

    mock_switch_python.assert_called_once_with(
        curr_py_exec=PythonExecutable.py_exec_required,
        curr_python_path=mock_get_path_to_curr_python.return_value,
        next_py_exec=PythonExecutable.py_exec_deps_updated,
        next_python_path=mock_get_path_to_curr_python.return_value,
        start_id="mock_start_id",
        proto_code_abs_file_path=mock_state_proto_code_file_abs_path_inited.return_value,
    )

    assert state_value == PythonExecutable.py_exec_deps_updated


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_start_id_var_loaded.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_file_abs_path_inited.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_py_exec_var_loaded.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_version_constraints_generated.__name__}.eval_own_state"
)
def test_py_exec_deps_updated(
    mock_state_version_constraints_generated,
    mock_state_input_py_exec_var_loaded,
    mock_state_proto_code_file_abs_path_inited,
    mock_state_args_parsed,
    mock_state_input_start_id_var_loaded,
    env_ctx,
):

    # given:

    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_py_exec_deps_updated_reached.name,
    )

    mock_state_args_parsed.return_value = argparse.Namespace(
        **{
            ParsedArg.name_reinstall.value: False,
        }
    )
    mock_state_input_start_id_var_loaded.return_value = "mock_start_id"
    mock_state_version_constraints_generated.return_value = True

    mock_state_input_py_exec_var_loaded.return_value = (
        PythonExecutable.py_exec_deps_updated
    )

    mock_state_proto_code_file_abs_path_inited.return_value = "path/to/whatever"

    # when:

    state_value = env_ctx.state_graph.eval_state(
        EnvState.state_py_exec_deps_updated_reached.name
    )

    # then:

    assert state_value == PythonExecutable.py_exec_deps_updated
