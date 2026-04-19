"""
See: FT_78_72_23_04.backward_compatibility.md

This test was originally focused on testing just `argparse` configuration.
See `test_via_cliff.py` which was created specifically to ensure backward compatibility.
"""

import io
from contextlib import redirect_stdout

import pytest

from protoprimer import primer_kernel as try_main
from protoprimer.primer_kernel import (
    parse_args,
    ParsedArg,
    ExecMode,
    SyntaxArg,
)


def test_parse_args_defaults():
    # when:
    args = parse_args([])

    # then:
    assert getattr(args, ParsedArg.name_exec_mode.value) == ExecMode.mode_boot.value
    assert getattr(args, ParsedArg.name_final_state.value) is None
    assert getattr(args, SyntaxArg.dest_quiet) == 0
    assert getattr(args, SyntaxArg.dest_verbose) == 0


def test_parse_args_reset():
    # when:
    args = parse_args([ExecMode.mode_reboot.value])

    # then:
    assert getattr(args, ParsedArg.name_exec_mode.value) == ExecMode.mode_reboot.value


def test_parse_args_command():
    cmd = "ls -l"

    # when:
    args = parse_args([ExecMode.mode_boot.value, SyntaxArg.arg_command, cmd])

    # then:
    assert getattr(args, ParsedArg.name_command.value) == cmd

    # when: short arg
    args_c = parse_args([ExecMode.mode_boot.value, SyntaxArg.arg_c, cmd])

    # then: short arg
    assert getattr(args_c, ParsedArg.name_command.value) == cmd


def test_parse_args_env():
    env_dir = "/path/to/env"

    # when: long arg
    args = parse_args([ExecMode.mode_boot.value, SyntaxArg.arg_env, env_dir])

    # then: long arg
    assert getattr(args, ParsedArg.name_selected_env_dir.value) == env_dir

    # when: short arg
    args_e = parse_args([ExecMode.mode_boot.value, SyntaxArg.arg_e, env_dir])

    # then: short arg
    assert getattr(args_e, ParsedArg.name_selected_env_dir.value) == env_dir


def test_parse_args_exec_mode():
    # when: boot mode
    args_prime = parse_args([ExecMode.mode_boot.value])

    # then: boot mode
    assert getattr(args_prime, ParsedArg.name_exec_mode.value) == ExecMode.mode_boot.value

    # when: eval mode
    args_config = parse_args([ExecMode.mode_eval.value])

    # then: eval mode
    assert getattr(args_config, ParsedArg.name_exec_mode.value) == ExecMode.mode_eval.value


def test_parse_args_log_level():
    # when: quiet long arg
    args_quiet = parse_args([SyntaxArg.arg_quiet])

    # then: quiet long arg
    assert getattr(args_quiet, SyntaxArg.dest_quiet) == 1

    # when: quiet short arg
    args_q = parse_args([SyntaxArg.arg_q])

    # then: quiet short arg
    assert getattr(args_q, SyntaxArg.dest_quiet) == 1

    # when: verbose once
    args_verbose_1 = parse_args([SyntaxArg.arg_verbose])

    # then: verbose once
    assert getattr(args_verbose_1, SyntaxArg.dest_verbose) == 1

    # when: verbose once short
    args_v_1 = parse_args([SyntaxArg.arg_v])

    # then: verbose once short
    assert getattr(args_v_1, SyntaxArg.dest_verbose) == 1

    # when: verbose three times
    args_verbose_3 = parse_args(["-vvv"])

    # then: verbose three times
    assert getattr(args_verbose_3, SyntaxArg.dest_verbose) == 3


def test_parse_args_final_state():
    # given:
    state = "some_state"

    # when:
    args = parse_args([ExecMode.mode_boot.value, SyntaxArg.arg_final_state, state])

    # then:
    assert getattr(args, ParsedArg.name_final_state.value) == state


@pytest.mark.parametrize(
    "test_argv,expected_dict",
    [
        (
            [],
            {
                ParsedArg.name_exec_mode.value: ExecMode.mode_boot.value,
                ParsedArg.name_selected_env_dir.value: None,
                SyntaxArg.dest_quiet: 0,
                SyntaxArg.dest_verbose: 0,
                ParsedArg.name_final_state.value: None,
                ParsedArg.name_command.value: None,
            },
        ),
        (
            ["boot"],
            {
                ParsedArg.name_exec_mode.value: ExecMode.mode_boot.value,
                ParsedArg.name_selected_env_dir.value: None,
                ParsedArg.name_final_state.value: None,
                SyntaxArg.dest_quiet: 0,
                SyntaxArg.dest_verbose: 0,
                ParsedArg.name_command.value: None,
            },
        ),
        (
            ["boot", "--final_state", "some_state"],
            {
                ParsedArg.name_exec_mode.value: ExecMode.mode_boot.value,
                ParsedArg.name_selected_env_dir.value: None,
                ParsedArg.name_final_state.value: "some_state",
                SyntaxArg.dest_quiet: 0,
                SyntaxArg.dest_verbose: 0,
                ParsedArg.name_command.value: None,
            },
        ),
        (
            ["reboot"],
            {
                ParsedArg.name_exec_mode.value: "reboot",
                SyntaxArg.dest_quiet: 0,
                SyntaxArg.dest_verbose: 0,
            },
        ),
        (
            ["eval"],
            {
                ParsedArg.name_exec_mode.value: "eval",
                SyntaxArg.dest_quiet: 0,
                SyntaxArg.dest_verbose: 0,
            },
        ),
        (
            ["-q", "boot"],
            {
                ParsedArg.name_exec_mode.value: ExecMode.mode_boot.value,
                ParsedArg.name_selected_env_dir.value: None,
                ParsedArg.name_final_state.value: None,
                SyntaxArg.dest_quiet: 1,
                SyntaxArg.dest_verbose: 0,
                ParsedArg.name_command.value: None,
            },
        ),
        (
            ["boot", "-v"],
            {
                ParsedArg.name_exec_mode.value: ExecMode.mode_boot.value,
                ParsedArg.name_selected_env_dir.value: None,
                ParsedArg.name_final_state.value: None,
                SyntaxArg.dest_quiet: 0,
                SyntaxArg.dest_verbose: 1,
                ParsedArg.name_command.value: None,
            },
        ),
        (
            ["boot", "-q"],
            {
                ParsedArg.name_exec_mode.value: ExecMode.mode_boot.value,
                ParsedArg.name_selected_env_dir.value: None,
                ParsedArg.name_final_state.value: None,
                SyntaxArg.dest_quiet: 1,
                SyntaxArg.dest_verbose: 0,
                ParsedArg.name_command.value: None,
            },
        ),
        (
            ["-vvv", "boot"],
            {
                ParsedArg.name_exec_mode.value: ExecMode.mode_boot.value,
                ParsedArg.name_selected_env_dir.value: None,
                ParsedArg.name_final_state.value: None,
                SyntaxArg.dest_quiet: 0,
                SyntaxArg.dest_verbose: 3,
                ParsedArg.name_command.value: None,
            },
        ),
        (
            ["boot", "--env", "some/path"],
            {
                ParsedArg.name_exec_mode.value: ExecMode.mode_boot.value,
                ParsedArg.name_selected_env_dir.value: "some/path",
                ParsedArg.name_final_state.value: None,
                SyntaxArg.dest_quiet: 0,
                SyntaxArg.dest_verbose: 0,
                ParsedArg.name_command.value: None,
            },
        ),
        (
            ["--env", "some/path"],
            {
                ParsedArg.name_exec_mode.value: ExecMode.mode_boot.value,
                ParsedArg.name_selected_env_dir.value: "some/path",
                ParsedArg.name_final_state.value: None,
                SyntaxArg.dest_quiet: 0,
                SyntaxArg.dest_verbose: 0,
                ParsedArg.name_command.value: None,
            },
        ),
        (
            ["--env", "default_env"],
            {
                ParsedArg.name_exec_mode.value: ExecMode.mode_boot.value,
                ParsedArg.name_selected_env_dir.value: "default_env",
                ParsedArg.name_final_state.value: None,
                SyntaxArg.dest_quiet: 0,
                SyntaxArg.dest_verbose: 0,
                ParsedArg.name_command.value: None,
            },
        ),
    ],
)
def test_argparse_subcommands_parametrized(test_argv, expected_dict):
    parsed_args = try_main.parse_args(test_argv)
    assert vars(parsed_args) == expected_dict


@pytest.mark.parametrize(
    "test_argv",
    [
        ["reboot", "--final_state", "some_state"],
        ["eval", "--final_state", "some_state"],
    ],
)
def test_argparse_invalid_final_state(test_argv):
    with pytest.raises(SystemExit):
        try_main.parse_args(test_argv)


@pytest.mark.parametrize(
    "test_argv",
    [
        ["reboot", "--env", "some/path"],
        ["eval", "--env", "some/path"],
    ],
)
def test_argparse_invalid_env(test_argv):
    with pytest.raises(SystemExit):
        try_main.parse_args(test_argv)


def test_main_help_contains_subcommand_descriptions():
    string_io = io.StringIO()
    with redirect_stdout(string_io):
        with pytest.raises(SystemExit):
            try_main.parse_args(["-h"])
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
        normalize_space("reboot Bootstrap from scratch: re-create `venv`, re-install dependencies, re-pin versions, ...")
        in normalized_output
        #
    )
    assert normalize_space("eval Evaluate effective config (print it on `stdout`).") in normalized_output


def test_subcommand_help_formatting():
    string_io = io.StringIO()
    with redirect_stdout(string_io):
        with pytest.raises(SystemExit):
            try_main.parse_args(["-h"])
    help_output = string_io.getvalue()
    assert "Exec modes:\n" in help_output
