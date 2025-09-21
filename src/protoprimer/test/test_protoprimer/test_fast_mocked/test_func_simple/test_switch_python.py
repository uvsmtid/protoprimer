import sys
from unittest.mock import (
    MagicMock,
    patch,
)

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    switch_python,
    PythonExecutable,
    WizardStage,
    SyntaxArg,
    ParsedArg,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        switch_python.__name__,
    )


@patch("os.execv")
def test_switch_python(
    mock_execv: MagicMock,
):
    # given:
    curr_py_exec = PythonExecutable.py_exec_arbitrary
    curr_python_path = "/usr/bin/python"
    next_py_exec = PythonExecutable.py_exec_required
    next_python_path = "/usr/bin/python3.9"
    start_id = "test_start_id"
    proto_code_abs_file_path = "/path/to/proto_kernel.py"
    wizard_stage = WizardStage.wizard_started

    # when:
    with patch.object(sys, "argv", ["/path/to/script.py", "--some-arg"]):
        switch_python(
            curr_py_exec,
            curr_python_path,
            next_py_exec,
            next_python_path,
            start_id,
            proto_code_abs_file_path,
            wizard_stage,
        )

    # then:
    expected_argv = [
        next_python_path,
        "/path/to/script.py",
        "--some-arg",
        SyntaxArg.arg_py_exec,
        next_py_exec.name,
        SyntaxArg.arg_start_id,
        start_id,
        SyntaxArg.arg_proto_code_abs_file_path,
        proto_code_abs_file_path,
    ]
    mock_execv.assert_called_once_with(next_python_path, expected_argv)


@patch("os.execv")
def test_switch_python_with_wizard_finished(
    mock_execv: MagicMock,
):
    # given:
    curr_py_exec = PythonExecutable.py_exec_arbitrary
    curr_python_path = "/usr/bin/python"
    next_py_exec = PythonExecutable.py_exec_required
    next_python_path = "/usr/bin/python3.9"
    start_id = "test_start_id"
    proto_code_abs_file_path = "/path/to/proto_kernel.py"
    wizard_stage = WizardStage.wizard_finished

    # when:
    with patch.object(sys, "argv", ["/path/to/script.py", "--some-arg"]):
        switch_python(
            curr_py_exec,
            curr_python_path,
            next_py_exec,
            next_python_path,
            start_id,
            proto_code_abs_file_path,
            wizard_stage,
        )

    # then:
    expected_argv = [
        next_python_path,
        "/path/to/script.py",
        "--some-arg",
        SyntaxArg.arg_py_exec,
        next_py_exec.name,
        SyntaxArg.arg_start_id,
        start_id,
        SyntaxArg.arg_proto_code_abs_file_path,
        proto_code_abs_file_path,
        SyntaxArg.arg_wizard_stage,
        wizard_stage.value,
    ]
    mock_execv.assert_called_once_with(next_python_path, expected_argv)


@patch("os.execv")
def test_switch_python_no_proto_code(
    mock_execv: MagicMock,
):
    # given:
    curr_py_exec = PythonExecutable.py_exec_arbitrary
    curr_python_path = "/usr/bin/python"
    next_py_exec = PythonExecutable.py_exec_required
    next_python_path = "/usr/bin/python3.9"
    start_id = "test_start_id"
    proto_code_abs_file_path = None
    wizard_stage = WizardStage.wizard_started

    # when:
    with patch.object(sys, "argv", ["/path/to/script.py", "--some-arg"]):
        switch_python(
            curr_py_exec,
            curr_python_path,
            next_py_exec,
            next_python_path,
            start_id,
            proto_code_abs_file_path,
            wizard_stage,
        )

    # then:
    expected_argv = [
        next_python_path,
        "/path/to/script.py",
        "--some-arg",
        SyntaxArg.arg_py_exec,
        next_py_exec.name,
        SyntaxArg.arg_start_id,
        start_id,
    ]
    mock_execv.assert_called_once_with(next_python_path, expected_argv)
