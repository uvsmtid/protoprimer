"""
See: FT_78_72_23_04.backward_compatibility.md

This test was originally focused on testing just `argparse` configuration.
See `test_parse_args_via_cliff.py` (in `test_contract_compatibility`) which was created specifically to ensure backward compatibility
(it also holds the `--` and required `main_func` cases).
"""

import io
from contextlib import redirect_stdout

import pytest

from protoprimer import primer_kernel as try_main
from protoprimer.primer_kernel import (
    _parse_args,
    _ParsedArg,
    _ExecOperation,
    _SyntaxArg,
)


def test_parse_args_defaults():
    # when:
    args = _parse_args([])

    # then:
    assert getattr(args, _ParsedArg.name_exec_operation.value) == _ExecOperation.op_boot.value
    assert getattr(args, _SyntaxArg.dest_quiet) == 0
    assert getattr(args, _SyntaxArg.dest_verbose) == 0


def test_parse_args_reset():
    # when:
    args = _parse_args([_ExecOperation.op_reset.value])

    # then:
    assert getattr(args, _ParsedArg.name_exec_operation.value) == _ExecOperation.op_reset.value


def test_parse_args_command():
    cmd = "ls -l"

    # when:
    args = _parse_args([_ExecOperation.op_shell.value, _SyntaxArg.arg_command, cmd])

    # then:
    assert getattr(args, _ParsedArg.name_shell_command.value) == cmd

    # when: short arg
    args_c = _parse_args([_ExecOperation.op_shell.value, _SyntaxArg.arg_c, cmd])

    # then: short arg
    assert getattr(args_c, _ParsedArg.name_shell_command.value) == cmd


def test_parse_args_start():
    main_func = "my_module:my_func"

    # when:
    args = _parse_args([_ExecOperation.op_start.value, main_func])

    # then:
    assert getattr(args, _ParsedArg.name_exec_operation.value) == _ExecOperation.op_start.value
    assert getattr(args, _ParsedArg.name_main_func.value) == main_func


def test_parse_args_env():
    env_dir = "/path/to/env"

    # when: long arg
    args = _parse_args([_ExecOperation.op_boot.value, _SyntaxArg.arg_env, env_dir])

    # then: long arg
    assert getattr(args, _ParsedArg.name_selected_env_dir.value) == env_dir

    # when: short arg
    args_e = _parse_args([_ExecOperation.op_boot.value, _SyntaxArg.arg_e, env_dir])

    # then: short arg
    assert getattr(args_e, _ParsedArg.name_selected_env_dir.value) == env_dir


def test_parse_args_exec_operation():
    # when: boot command
    args_prime = _parse_args([_ExecOperation.op_boot.value])

    # then: boot command
    assert getattr(args_prime, _ParsedArg.name_exec_operation.value) == _ExecOperation.op_boot.value

    # when: eval command
    args_config = _parse_args([_ExecOperation.op_eval.value])

    # then: eval command
    assert getattr(args_config, _ParsedArg.name_exec_operation.value) == _ExecOperation.op_eval.value


def test_parse_args_log_level():
    # when: quiet long arg
    args_quiet = _parse_args([_SyntaxArg.arg_quiet])

    # then: quiet long arg
    assert getattr(args_quiet, _SyntaxArg.dest_quiet) == 1

    # when: quiet short arg
    args_q = _parse_args([_SyntaxArg.arg_q])

    # then: quiet short arg
    assert getattr(args_q, _SyntaxArg.dest_quiet) == 1

    # when: verbose once
    args_verbose_1 = _parse_args([_SyntaxArg.arg_verbose])

    # then: verbose once
    assert getattr(args_verbose_1, _SyntaxArg.dest_verbose) == 1

    # when: verbose once short
    args_v_1 = _parse_args([_SyntaxArg.arg_v])

    # then: verbose once short
    assert getattr(args_v_1, _SyntaxArg.dest_verbose) == 1

    # when: verbose three times
    args_verbose_3 = _parse_args(["-vvv"])

    # then: verbose three times
    assert getattr(args_verbose_3, _SyntaxArg.dest_verbose) == 3


@pytest.mark.parametrize(
    "test_argv,expected_dict",
    [
        (
            [],
            {
                _ParsedArg.name_exec_operation.value: _ExecOperation.op_boot.value,
                _ParsedArg.name_selected_env_dir.value: None,
                _SyntaxArg.dest_quiet: 0,
                _SyntaxArg.dest_verbose: 0,
                _ParsedArg.name_target_args.value: [],
            },
        ),
        (
            ["boot"],
            {
                _ParsedArg.name_exec_operation.value: _ExecOperation.op_boot.value,
                _ParsedArg.name_selected_env_dir.value: None,
                _SyntaxArg.dest_quiet: 0,
                _SyntaxArg.dest_verbose: 0,
                _ParsedArg.name_target_args.value: [],
            },
        ),
        (
            ["reset"],
            {
                _ParsedArg.name_exec_operation.value: "reset",
                _ParsedArg.name_selected_env_dir.value: None,
                _SyntaxArg.dest_quiet: 0,
                _SyntaxArg.dest_verbose: 0,
                _ParsedArg.name_target_args.value: [],
            },
        ),
        (
            ["eval"],
            {
                _ParsedArg.name_exec_operation.value: "eval",
                _ParsedArg.name_selected_env_dir.value: None,
                _SyntaxArg.dest_quiet: 0,
                _SyntaxArg.dest_verbose: 0,
                _ParsedArg.name_target_args.value: [],
            },
        ),
        (
            ["-q", "boot"],
            {
                _ParsedArg.name_exec_operation.value: _ExecOperation.op_boot.value,
                _ParsedArg.name_selected_env_dir.value: None,
                _SyntaxArg.dest_quiet: 1,
                _SyntaxArg.dest_verbose: 0,
                _ParsedArg.name_target_args.value: [],
            },
        ),
        (
            ["boot", "-v"],
            {
                _ParsedArg.name_exec_operation.value: _ExecOperation.op_boot.value,
                _ParsedArg.name_selected_env_dir.value: None,
                _SyntaxArg.dest_quiet: 0,
                _SyntaxArg.dest_verbose: 1,
                _ParsedArg.name_target_args.value: [],
            },
        ),
        (
            ["boot", "-q"],
            {
                _ParsedArg.name_exec_operation.value: _ExecOperation.op_boot.value,
                _ParsedArg.name_selected_env_dir.value: None,
                _SyntaxArg.dest_quiet: 1,
                _SyntaxArg.dest_verbose: 0,
                _ParsedArg.name_target_args.value: [],
            },
        ),
        (
            ["-vvv", "boot"],
            {
                _ParsedArg.name_exec_operation.value: _ExecOperation.op_boot.value,
                _ParsedArg.name_selected_env_dir.value: None,
                _SyntaxArg.dest_quiet: 0,
                _SyntaxArg.dest_verbose: 3,
                _ParsedArg.name_target_args.value: [],
            },
        ),
        (
            ["boot", "--env", "some/path"],
            {
                _ParsedArg.name_exec_operation.value: _ExecOperation.op_boot.value,
                _ParsedArg.name_selected_env_dir.value: "some/path",
                _SyntaxArg.dest_quiet: 0,
                _SyntaxArg.dest_verbose: 0,
                _ParsedArg.name_target_args.value: [],
            },
        ),
        (
            ["--env", "some/path"],
            {
                _ParsedArg.name_exec_operation.value: _ExecOperation.op_boot.value,
                _ParsedArg.name_selected_env_dir.value: "some/path",
                _SyntaxArg.dest_quiet: 0,
                _SyntaxArg.dest_verbose: 0,
                _ParsedArg.name_target_args.value: [],
            },
        ),
        (
            ["--env", "default_env"],
            {
                _ParsedArg.name_exec_operation.value: _ExecOperation.op_boot.value,
                _ParsedArg.name_selected_env_dir.value: "default_env",
                _SyntaxArg.dest_quiet: 0,
                _SyntaxArg.dest_verbose: 0,
                _ParsedArg.name_target_args.value: [],
            },
        ),
    ],
)
def test_argparse_execoperations_parametrized(test_argv, expected_dict):
    parsed_args = try_main._parse_args(test_argv)
    assert vars(parsed_args) == expected_dict


@pytest.mark.parametrize(
    "test_argv,expected_env",
    [
        (["reset", "--env", "some/path"], "some/path"),
        (["eval", "--env", "some/path"], "some/path"),
        (["-e", "some/path", "eval"], "some/path"),
    ],
)
def test_argparse_env_common_arg(test_argv, expected_env):
    parsed_args = try_main._parse_args(test_argv)
    assert getattr(parsed_args, _ParsedArg.name_selected_env_dir.value) == expected_env


def test_main_help_contains_execoperation_descriptions():
    string_io = io.StringIO()
    with redirect_stdout(string_io):
        with pytest.raises(SystemExit):
            try_main._parse_args(["-h"])
    output = string_io.getvalue()

    def normalize_space(s):
        return " ".join(s.split())

    normalized_output = normalize_space(output)

    assert (
        normalize_space("boot Bootstrap whatever is missing in the environment.")
        in normalized_output
        #
    )
    assert (
        normalize_space("reset Bootstrap from scratch: re-create `venv`, re-install dependencies, re-pin versions, ...")
        in normalized_output
        #
    )
    assert normalize_space("eval Evaluate effective config (print it on `stdout`).") in normalized_output


def test_execoperation_help_formatting():
    string_io = io.StringIO()
    with redirect_stdout(string_io):
        with pytest.raises(SystemExit):
            try_main._parse_args(["-h"])
    help_output = string_io.getvalue()
    assert "Exec operations:\n" in help_output
