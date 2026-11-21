import os
import subprocess
import sys
from unittest.mock import (
    MagicMock,
    patch,
)

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    EnvVar,
    _ConfConstGeneral,
    _StateStride,
    _switch_python,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        _switch_python.__name__,
    )


@patch.dict(f"{os.__name__}.environ", {}, clear=True)
@patch.object(sys, "argv", ["/path/to/script.py", "--some-arg"])
@patch.object(_ConfConstGeneral, "is_os_windows", False)
@patch(f"{os.__name__}.execve")
def test_switch_python(
    mock_execve: MagicMock,
):
    # given:
    curr_py_exec = _StateStride.stride_py_arbitrary
    curr_python_path = "/usr/bin/python"
    next_py_exec = _StateStride.stride_py_required
    next_python_path = "/usr/bin/python3.9"
    start_id = "test_start_id"
    proto_kernel_abs_file_path = "/path/to/proto_kernel.py"

    # when:
    _switch_python(
        curr_python_path,
        next_py_exec,
        next_python_path,
        start_id,
        proto_kernel_abs_file_path,
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
            EnvVar.var_PROTOPRIMER_PY_EXEC.value: _StateStride.stride_py_required.name,
            EnvVar.var_PROTOPRIMER_START_ID.value: start_id,
            EnvVar.var_PROTOPRIMER_PROTO_KERNEL.value: proto_kernel_abs_file_path,
        },
    )


@patch.dict(
    f"{os.__name__}.environ",
    {EnvVar.var_PROTOPRIMER_TRACE_EXECUTION.value: "true"},
    clear=True,
)
@patch.object(sys, "argv", ["/path/to/script.py", "--some-arg"])
@patch.object(_ConfConstGeneral, "is_os_windows", False)
@patch(f"{os.__name__}.execve")
def test_switch_python_trace_execution(
    mock_execve: MagicMock,
):
    # given:
    curr_python_path = "/usr/bin/python"
    next_py_exec = _StateStride.stride_py_required
    next_python_path = "/usr/bin/python3.9"
    start_id = "test_start_id"
    proto_kernel_abs_file_path = "/path/to/proto_kernel.py"

    # when:
    _switch_python(
        curr_python_path,
        next_py_exec,
        next_python_path,
        start_id,
        proto_kernel_abs_file_path,
    )

    # then:
    expected_argv = [
        next_python_path,
        "-I",
        "-m",
        "trace",
        "--trace",
        "/path/to/script.py",
        "--some-arg",
    ]
    mock_execve.assert_called_once_with(
        path=next_python_path,
        argv=expected_argv,
        env={
            EnvVar.var_PROTOPRIMER_TRACE_EXECUTION.value: "true",
            EnvVar.var_PROTOPRIMER_PY_EXEC.value: _StateStride.stride_py_required.name,
            EnvVar.var_PROTOPRIMER_START_ID.value: start_id,
            EnvVar.var_PROTOPRIMER_PROTO_KERNEL.value: proto_kernel_abs_file_path,
        },
    )


@patch.dict(f"{os.__name__}.environ", {}, clear=True)
@patch.object(sys, "argv", ["/path/to/script.py", "--some-arg"])
@patch.object(_ConfConstGeneral, "is_os_windows", False)
@patch(f"{os.__name__}.execve")
def test_switch_python_no_proto_kernel(
    mock_execve: MagicMock,
):
    # given:
    curr_py_exec = _StateStride.stride_py_arbitrary
    curr_python_path = "/usr/bin/python"
    next_py_exec = _StateStride.stride_py_required
    next_python_path = "/usr/bin/python3.9"
    start_id = "test_start_id"
    proto_kernel_abs_file_path = None

    # when:
    _switch_python(
        curr_python_path,
        next_py_exec,
        next_python_path,
        start_id,
        proto_kernel_abs_file_path,
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
            EnvVar.var_PROTOPRIMER_PY_EXEC.value: _StateStride.stride_py_required.name,
            EnvVar.var_PROTOPRIMER_START_ID.value: start_id,
        },
    )


@patch.dict(f"{os.__name__}.environ", {}, clear=True)
@patch.object(sys, "argv", ["/path/to/script.py", "--some-arg"])
@patch.object(_ConfConstGeneral, "is_os_windows", True)
@patch(f"{subprocess.__name__}.run")
@patch(f"{os.__name__}.execve")
def test_switch_python_on_windows(
    mock_execve: MagicMock,
    mock_run: MagicMock,
):
    # given:
    # Windows has no real `exec()`: the next `python` is run as a child process (and its exit code is returned):
    mock_run.return_value = MagicMock(returncode=7)
    next_python_path = "C:\\python\\python.exe"
    start_id = "test_start_id"
    proto_kernel_abs_file_path = "C:\\path\\to\\proto_kernel.py"

    # when:
    with pytest.raises(SystemExit) as exc_info:
        _switch_python(
            "C:\\python\\curr_python.exe",
            _StateStride.stride_py_required,
            next_python_path,
            start_id,
            proto_kernel_abs_file_path,
        )

    # then:
    assert exc_info.value.code == 7
    mock_execve.assert_not_called()
    mock_run.assert_called_once_with(
        [
            next_python_path,
            "-I",
            "/path/to/script.py",
            "--some-arg",
        ],
        env={
            EnvVar.var_PROTOPRIMER_PY_EXEC.value: _StateStride.stride_py_required.name,
            EnvVar.var_PROTOPRIMER_START_ID.value: start_id,
            EnvVar.var_PROTOPRIMER_PROTO_KERNEL.value: proto_kernel_abs_file_path,
        },
    )
