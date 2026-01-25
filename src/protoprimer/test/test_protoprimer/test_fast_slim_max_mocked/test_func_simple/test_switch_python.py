import os
import sys
from unittest.mock import (
    MagicMock,
    patch,
)

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    EnvVar,
    PythonExecutable,
    switch_python,
    SyntaxArg,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        switch_python.__name__,
    )


@patch.dict(f"{os.__name__}.environ", {}, clear=True)
@patch.object(sys, "argv", ["/path/to/script.py", "--some-arg"])
@patch(f"{os.__name__}.execve")
def test_switch_python(
    mock_execve: MagicMock,
):
    # given:
    curr_py_exec = PythonExecutable.py_exec_arbitrary
    curr_python_path = "/usr/bin/python"
    next_py_exec = PythonExecutable.py_exec_required
    next_python_path = "/usr/bin/python3.9"
    start_id = "test_start_id"
    proto_code_abs_file_path = "/path/to/proto_kernel.py"

    # when:
    switch_python(
        curr_python_path,
        next_py_exec,
        next_python_path,
        start_id,
        proto_code_abs_file_path,
    )

    # then:
    expected_argv = [
        next_python_path,
        "-I",
        "/path/to/script.py",
        "--some-arg",
    ]
    mock_execve.assert_called_once_with(
        path=next_python_path,
        argv=expected_argv,
        env={
            EnvVar.var_PROTOPRIMER_PY_EXEC.value: PythonExecutable.py_exec_required.name,
            EnvVar.var_PROTOPRIMER_START_ID.value: start_id,
            EnvVar.var_PROTOPRIMER_PROTO_CODE.value: proto_code_abs_file_path,
        },
    )


@patch.dict(f"{os.__name__}.environ", {}, clear=True)
@patch.object(sys, "argv", ["/path/to/script.py", "--some-arg"])
@patch(f"{os.__name__}.execve")
def test_switch_python_no_proto_code(
    mock_execve: MagicMock,
):
    # given:
    curr_py_exec = PythonExecutable.py_exec_arbitrary
    curr_python_path = "/usr/bin/python"
    next_py_exec = PythonExecutable.py_exec_required
    next_python_path = "/usr/bin/python3.9"
    start_id = "test_start_id"
    proto_code_abs_file_path = None

    # when:
    switch_python(
        curr_python_path,
        next_py_exec,
        next_python_path,
        start_id,
        proto_code_abs_file_path,
    )

    # then:
    expected_argv = [
        next_python_path,
        "-I",
        "/path/to/script.py",
        "--some-arg",
    ]
    mock_execve.assert_called_once_with(
        path=next_python_path,
        argv=expected_argv,
        env={
            EnvVar.var_PROTOPRIMER_PY_EXEC.value: PythonExecutable.py_exec_required.name,
            EnvVar.var_PROTOPRIMER_START_ID.value: start_id,
        },
    )
