from unittest.mock import patch

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_proto_kernel_code_file_abs_path_finalized,
    Bootstrapper_state_protoprimer_package_installed,
    Bootstrapper_state_py_exec_arg,
    EnvContext,
    EnvState,
    PythonExecutable,
)


@pytest.fixture
def env_ctx():
    return EnvContext()


# noinspection PyMethodMayBeStatic
def test_relationship():
    assert_test_module_name_embeds_str(
        EnvState.state_py_exec_updated_protoprimer_package_reached.name
    )


@patch(f"{primer_kernel.__name__}.get_path_to_curr_python")
@patch(f"{primer_kernel.__name__}.switch_python")
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_proto_kernel_code_file_abs_path_finalized.__name__}._bootstrap_once"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_arg.__name__}._bootstrap_once"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_protoprimer_package_installed.__name__}._bootstrap_once"
)
def test_py_exec_required(
    mock_state_protoprimer_package_installed,
    mock_state_py_exec_arg,
    mock_state_proto_kernel_code_file_abs_path_finalized,
    mock_switch_python,
    mock_get_path_to_curr_python,
    env_ctx,
):

    # given:

    mock_state_protoprimer_package_installed.return_value = True

    mock_state_py_exec_arg.return_value = PythonExecutable.py_exec_required

    mock_state_proto_kernel_code_file_abs_path_finalized.return_value = (
        "path/to/whatever"
    )

    mock_get_path_to_curr_python.return_value = "/path/to/venv/bin/python"

    # when:

    ret_val = env_ctx.bootstrap_state(
        EnvState.state_py_exec_updated_protoprimer_package_reached.name
    )

    # then:

    mock_switch_python.assert_called_once_with(
        curr_py_exec=PythonExecutable.py_exec_required,
        curr_python_path=mock_get_path_to_curr_python.return_value,
        next_py_exec=PythonExecutable.py_exec_updated_protoprimer_package,
        next_python_path=mock_get_path_to_curr_python.return_value,
        proto_kernel_abs_file_path=mock_state_proto_kernel_code_file_abs_path_finalized.return_value,
    )

    assert ret_val == PythonExecutable.py_exec_updated_protoprimer_package


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_proto_kernel_code_file_abs_path_finalized.__name__}._bootstrap_once"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_arg.__name__}._bootstrap_once"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_protoprimer_package_installed.__name__}._bootstrap_once"
)
def test_py_exec_updated_protoprimer_package(
    mock_state_protoprimer_package_installed,
    mock_state_py_exec_arg,
    mock_state_proto_kernel_code_file_abs_path_finalized,
    env_ctx,
):

    # given:

    mock_state_protoprimer_package_installed.return_value = True

    mock_state_py_exec_arg.return_value = (
        PythonExecutable.py_exec_updated_protoprimer_package
    )

    mock_state_proto_kernel_code_file_abs_path_finalized.return_value = (
        "path/to/whatever"
    )

    # when:

    ret_val = env_ctx.bootstrap_state(
        EnvState.state_py_exec_updated_protoprimer_package_reached.name
    )

    # then:

    assert ret_val == PythonExecutable.py_exec_updated_protoprimer_package
