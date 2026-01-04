import io
from contextlib import redirect_stdout

import pytest

from protoprimer import primer_kernel as try_main
from protoprimer.primer_kernel import (
    CommandAction,
    parse_args,
    ParsedArg,
    RunMode,
    SyntaxArg,
)


def test_parse_args_defaults():
    # when:
    args = parse_args([])

    # then:
    assert getattr(args, ParsedArg.name_run_mode.value) == RunMode.mode_prime.value
    assert getattr(args, ParsedArg.name_final_state.value) is None
    assert getattr(args, SyntaxArg.dest_silent) is False
    assert getattr(args, SyntaxArg.dest_quiet) is False
    assert getattr(args, SyntaxArg.dest_verbose) == 0


def test_parse_args_upgrade():
    # when:
    args = parse_args([RunMode.mode_upgrade.value])

    # then:
    assert getattr(args, ParsedArg.name_run_mode.value) == RunMode.mode_upgrade.value


def test_parse_args_command():
    cmd = "ls -l"

    # when:
    args = parse_args([RunMode.mode_prime.value, SyntaxArg.arg_command, cmd])

    # then:
    assert getattr(args, ParsedArg.name_command.value) == cmd

    # when: short arg
    args_c = parse_args([RunMode.mode_prime.value, SyntaxArg.arg_c, cmd])

    # then: short arg
    assert getattr(args_c, ParsedArg.name_command.value) == cmd


def test_parse_args_env():
    env_dir = "/path/to/env"

    # when: long arg
    args = parse_args([RunMode.mode_prime.value, SyntaxArg.arg_env, env_dir])

    # then: long arg
    assert getattr(args, ParsedArg.name_selected_env_dir.value) == env_dir

    # when: short arg
    args_e = parse_args([RunMode.mode_prime.value, SyntaxArg.arg_e, env_dir])

    # then: short arg
    assert getattr(args_e, ParsedArg.name_selected_env_dir.value) == env_dir


def test_parse_args_run_mode():
    # when: prime mode
    args_prime = parse_args([RunMode.mode_prime.value])

    # then: prime mode
    assert (
        getattr(args_prime, ParsedArg.name_run_mode.value) == RunMode.mode_prime.value
    )

    # when: config mode
    args_config = parse_args([RunMode.mode_config.value])

    # then: config mode
    assert (
        getattr(args_config, ParsedArg.name_run_mode.value) == RunMode.mode_config.value
    )

    # when: check mode
    args_check = parse_args([RunMode.mode_check.value])

    # then: check mode
    assert (
        getattr(args_check, ParsedArg.name_run_mode.value) == RunMode.mode_check.value
    )


def test_parse_args_log_level():
    # when: silent long arg
    args_silent = parse_args([SyntaxArg.arg_silent])

    # then: silent long arg
    assert getattr(args_silent, SyntaxArg.dest_silent) is True

    # when: silent short arg
    args_s = parse_args([SyntaxArg.arg_s])

    # then: silent short arg
    assert getattr(args_s, SyntaxArg.dest_silent) is True

    # when: quiet long arg
    args_quiet = parse_args([SyntaxArg.arg_quiet])

    # then: quiet long arg
    assert getattr(args_quiet, SyntaxArg.dest_quiet) is True

    # when: quiet short arg
    args_q = parse_args([SyntaxArg.arg_q])

    # then: quiet short arg
    assert getattr(args_q, SyntaxArg.dest_quiet) is True

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
    args = parse_args([RunMode.mode_prime.value, SyntaxArg.arg_final_state, state])

    # then:
    assert getattr(args, ParsedArg.name_final_state.value) == state


@pytest.mark.parametrize(
    "test_argv,expected_dict",
    [
        (
            [],
            {
                ParsedArg.name_run_mode.value: RunMode.mode_prime.value,
                ParsedArg.name_selected_env_dir.value: None,
                SyntaxArg.dest_silent: False,
                SyntaxArg.dest_quiet: False,
                SyntaxArg.dest_verbose: 0,
                ParsedArg.name_final_state.value: None,
                ParsedArg.name_command.value: None,
            },
        ),
        (
            ["prime"],
            {
                ParsedArg.name_run_mode.value: RunMode.mode_prime.value,
                ParsedArg.name_selected_env_dir.value: None,
                ParsedArg.name_final_state.value: None,
                SyntaxArg.dest_silent: False,
                SyntaxArg.dest_quiet: False,
                SyntaxArg.dest_verbose: 0,
                ParsedArg.name_command.value: None,
            },
        ),
        (
            ["prime", "--final_state", "some_state"],
            {
                ParsedArg.name_run_mode.value: RunMode.mode_prime.value,
                ParsedArg.name_selected_env_dir.value: None,
                ParsedArg.name_final_state.value: "some_state",
                SyntaxArg.dest_silent: False,
                SyntaxArg.dest_quiet: False,
                SyntaxArg.dest_verbose: 0,
                ParsedArg.name_command.value: None,
            },
        ),
        (
            ["upgrade"],
            {
                ParsedArg.name_run_mode.value: "upgrade",
                SyntaxArg.dest_silent: False,
                SyntaxArg.dest_quiet: False,
                SyntaxArg.dest_verbose: 0,
            },
        ),
        (
            ["config"],
            {
                ParsedArg.name_run_mode.value: "config",
                SyntaxArg.dest_silent: False,
                SyntaxArg.dest_quiet: False,
                SyntaxArg.dest_verbose: 0,
            },
        ),
        (
            ["check"],
            {
                ParsedArg.name_run_mode.value: "check",
                SyntaxArg.dest_silent: False,
                SyntaxArg.dest_quiet: False,
                SyntaxArg.dest_verbose: 0,
            },
        ),
        (
            ["-q", "prime"],
            {
                ParsedArg.name_run_mode.value: RunMode.mode_prime.value,
                ParsedArg.name_selected_env_dir.value: None,
                ParsedArg.name_final_state.value: None,
                SyntaxArg.dest_silent: False,
                SyntaxArg.dest_quiet: True,
                SyntaxArg.dest_verbose: 0,
                ParsedArg.name_command.value: None,
            },
        ),
        (
            ["prime", "-v"],
            {
                ParsedArg.name_run_mode.value: RunMode.mode_prime.value,
                ParsedArg.name_selected_env_dir.value: None,
                ParsedArg.name_final_state.value: None,
                SyntaxArg.dest_silent: False,
                SyntaxArg.dest_quiet: False,
                SyntaxArg.dest_verbose: 1,
                ParsedArg.name_command.value: None,
            },
        ),
        (
            ["prime", "-s"],
            {
                ParsedArg.name_run_mode.value: RunMode.mode_prime.value,
                ParsedArg.name_selected_env_dir.value: None,
                ParsedArg.name_final_state.value: None,
                SyntaxArg.dest_silent: True,
                SyntaxArg.dest_quiet: False,
                SyntaxArg.dest_verbose: 0,
                ParsedArg.name_command.value: None,
            },
        ),
        (
            ["prime", "-q"],
            {
                ParsedArg.name_run_mode.value: RunMode.mode_prime.value,
                ParsedArg.name_selected_env_dir.value: None,
                ParsedArg.name_final_state.value: None,
                SyntaxArg.dest_silent: False,
                SyntaxArg.dest_quiet: True,
                SyntaxArg.dest_verbose: 0,
                ParsedArg.name_command.value: None,
            },
        ),
        (
            ["-vvv", "prime"],
            {
                ParsedArg.name_run_mode.value: RunMode.mode_prime.value,
                ParsedArg.name_selected_env_dir.value: None,
                ParsedArg.name_final_state.value: None,
                SyntaxArg.dest_silent: False,
                SyntaxArg.dest_quiet: False,
                SyntaxArg.dest_verbose: 3,
                ParsedArg.name_command.value: None,
            },
        ),
        (
            ["prime", "--env", "some/path"],
            {
                ParsedArg.name_run_mode.value: RunMode.mode_prime.value,
                ParsedArg.name_selected_env_dir.value: "some/path",
                ParsedArg.name_final_state.value: None,
                SyntaxArg.dest_silent: False,
                SyntaxArg.dest_quiet: False,
                SyntaxArg.dest_verbose: 0,
                ParsedArg.name_command.value: None,
            },
        ),
        (
            ["--env", "some/path"],
            {
                ParsedArg.name_run_mode.value: RunMode.mode_prime.value,
                ParsedArg.name_selected_env_dir.value: "some/path",
                ParsedArg.name_final_state.value: None,
                SyntaxArg.dest_silent: False,
                SyntaxArg.dest_quiet: False,
                SyntaxArg.dest_verbose: 0,
                ParsedArg.name_command.value: None,
            },
        ),
        (
            ["--env", "default_env"],
            {
                ParsedArg.name_run_mode.value: RunMode.mode_prime.value,
                ParsedArg.name_selected_env_dir.value: "default_env",
                ParsedArg.name_final_state.value: None,
                SyntaxArg.dest_silent: False,
                SyntaxArg.dest_quiet: False,
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
        ["upgrade", "--final_state", "some_state"],
        ["config", "--final_state", "some_state"],
        ["check", "--final_state", "some_state"],
    ],
)
def test_argparse_invalid_final_state(test_argv):
    with pytest.raises(SystemExit):
        try_main.parse_args(test_argv)


@pytest.mark.parametrize(
    "test_argv",
    [
        ["upgrade", "--env", "some/path"],
        ["config", "--env", "some/path"],
        ["check", "--env", "some/path"],
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
        normalize_space("prime Prime the environment to make it ready to use.")
        in normalized_output
    )
    assert (
        normalize_space(
            "upgrade Re-create `venv`, re-install dependencies, and re-pin versions."
        )
        in normalized_output
    )
    assert normalize_space("config Print effective config.") in normalized_output
    assert (
        normalize_space("check Check the environment configuration.")
        in normalized_output
    )


def test_subcommand_help_formatting():
    string_io = io.StringIO()
    with redirect_stdout(string_io):
        with pytest.raises(SystemExit):
            try_main.parse_args(["-h"])
    output = string_io.getvalue()
    assert "Run modes:\n" in output
