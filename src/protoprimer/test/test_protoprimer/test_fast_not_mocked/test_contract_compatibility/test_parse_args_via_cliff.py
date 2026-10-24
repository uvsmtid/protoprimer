"""
See: FT_78_72_23_04.backward_compatibility.md

Ensuring the stable CLI with `cliff`.

The spec below is frozen (literals only, nothing is taken from `protoprimer`: a rename must be detected).
The actual CLI is exercised via the public `parse_args` only: for every `argv` row, the spec parsers
work out the expected values, and `parse_args` must give the same ones.
The comparison goes from the spec to the actual args only: new args/options never fail it.

See also `TODO_01_84_56_96.cover_CLI_compatibility.md`.
"""

import argparse

import pytest
from cliff.app import App
from cliff.command import Command
from cliff.commandmanager import CommandManager

from local_test.cli_spec_helper import find_spec_mismatches
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import parse_args


class Boot(Command):
    """
    Bootstrap whatever is missing in the environment.
    """

    def take_action(self, parsed_args):
        pass


class Reset(Command):
    """
    Bootstrap from scratch.
    """

    def take_action(self, parsed_args):
        pass


class Eval(Command):
    """
    Evaluate effective config.
    """

    def take_action(self, parsed_args):
        pass


class Shell(Command):
    """
    Start shell with activated `venv`.
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "-c",
            "--command",
            dest="shell_command",
            metavar="shell_command",
        )
        return parser

    def take_action(self, parsed_args):
        pass


class Start(Command):
    """
    Start `main_func` with activated `venv`.
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "main_func",
            metavar="main_func",
        )
        return parser

    def take_action(self, parsed_args):
        pass


class WrapBase(Command):
    """
    Generate an `entry_script` boilerplate.
    """

    main_func_required = False

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "-s",
            "--entry_script_path",
            dest="entry_script_path",
            metavar="entry_script_path",
            required=True,
        )
        parser.add_argument(
            "-m",
            "--main_func",
            dest="main_func",
            metavar="main_func",
            default="",
            required=self.main_func_required,
        )
        return parser

    def take_action(self, parsed_args):
        pass


class WrapBootEnv(WrapBase):
    main_func_required = False


class WrapStartApp(WrapBase):
    main_func_required = True


# `check` is not in the spec: it is not implemented and may change (TODO_73_71_31_84.exec_operation_check_or_info.md).


class SpecApp(App):
    """
    The stable CLI specification.
    """

    def __init__(self):
        cmd_manager = CommandManager("test_parse_args_via_cliff")
        cmd_manager.add_command(
            "boot",
            Boot,
        )
        cmd_manager.add_command(
            "reset",
            Reset,
        )
        cmd_manager.add_command(
            "eval",
            Eval,
        )
        cmd_manager.add_command(
            "shell",
            Shell,
        )
        cmd_manager.add_command(
            "start",
            Start,
        )
        cmd_manager.add_command(
            "wrap boot_env",
            WrapBootEnv,
        )
        cmd_manager.add_command(
            "wrap start_app",
            WrapStartApp,
        )
        super().__init__(
            description="Spec App",
            version="0.1.0",
            command_manager=cmd_manager,
        )

    def build_option_parser(self, description, version, argparse_kwargs=None):
        argparse_kwargs = argparse_kwargs or {}
        argparse_kwargs.setdefault("conflict_handler", "resolve")
        parser = super().build_option_parser(description, version, argparse_kwargs)
        # Global options (accepted before or after an exec operation):
        parser.add_argument(
            "-q",
            "--quiet",
            action="count",
            dest="stderr_log_level_quiet",
            default=0,
        )
        parser.add_argument(
            "-v",
            "--verbose",
            action="count",
            dest="stderr_log_level_verbose",
            default=0,
        )
        parser.add_argument(
            "-e",
            "--env",
            dest="selected_env_dir",
            metavar="selected_env_dir",
        )
        return parser


# The names `cliff` adds on its own (not part of the spec) are excluded from the comparison:
spec_global_dests = [
    "stderr_log_level_quiet",
    "stderr_log_level_verbose",
    "selected_env_dir",
]

exec_operations = ["boot", "reset", "eval", "shell", "start", "wrap"]


def parse_via_spec(expected_argv) -> dict:
    """
    Work out the expected values for `expected_argv` using the `cliff` spec only.
    """

    spec_app = SpecApp()
    global_parser = spec_app.build_option_parser("Spec", "0.1.0")
    global_args, remaining_argv = global_parser.parse_known_args(expected_argv)
    expected_spec_values = {spec_dest: getattr(global_args, spec_dest) for spec_dest in spec_global_dests}

    # `boot` is the default exec operation:
    if remaining_argv and remaining_argv[0] in exec_operations:
        exec_operation = remaining_argv[0]
        remaining_argv = remaining_argv[1:]
    else:
        exec_operation = "boot"
    expected_spec_values["exec_operation"] = exec_operation

    command_tokens = [exec_operation]
    if exec_operation == "wrap":
        command_tokens.append(remaining_argv[0])
        expected_spec_values["entry_func"] = remaining_argv[0]
        remaining_argv = remaining_argv[1:]

    cmd_factory, cmd_name, _ = spec_app.command_manager.find_command(command_tokens)
    cmd_instance = cmd_factory(spec_app, None, cmd_name=cmd_name)
    command_args = cmd_instance.get_parser("test").parse_args(remaining_argv)
    expected_spec_values.update(vars(command_args))

    return expected_spec_values


def test_relationship():
    assert_test_module_name_embeds_str(parse_args.__name__)


@pytest.mark.parametrize(
    "given_argv",
    [
        [],
        ["boot"],
        ["reset"],
        ["eval"],
        ["-q", "boot"],
        ["boot", "-q"],
        ["--quiet", "boot"],
        ["-v", "-v", "reset"],
        ["-vvv", "boot"],
        ["boot", "--verbose"],
        ["boot", "-e", "my_env"],
        ["boot", "--env", "my_env"],
        ["-e", "my_env", "eval"],
        ["eval", "-e", "my_env"],
        ["--env", "my_env"],
        ["shell"],
        ["shell", "-c", "ls -l"],
        ["shell", "--command", "ls -l"],
        ["-q", "shell", "-c", "ls"],
        ["start", "my_module:my_func"],
        ["-v", "start", "my_module:my_func"],
        ["start", "my_module:my_func", "-e", "my_env"],
        ["wrap", "boot_env", "-s", "/path/to/script"],
        ["wrap", "boot_env", "--entry_script_path", "/path/to/script", "-m", "my_module:my_func"],
        ["wrap", "start_app", "-s", "/path/to/script", "-m", "my_module:my_func"],
        ["wrap", "start_app", "--entry_script_path", "/path/to/script", "--main_func", "my_module:my_func"],
        ["-q", "wrap", "start_app", "-s", "/path/to/script", "-m", "my_module:my_func"],
    ],
)
def test_parse_args_matches_spec(given_argv):
    """
    Every value the spec expects for `given_argv` (defaults, short and long forms, positions, ...)
    must be given by `parse_args` too.
    """

    # given:

    expected_spec_values = parse_via_spec(given_argv)

    # when:

    actual_args = parse_args(given_argv)

    # then:

    assert find_spec_mismatches(expected_spec_values, actual_args) == []


@pytest.mark.parametrize(
    "given_argv",
    [
        ["start"],
        ["wrap"],
        ["wrap", "boot_env"],
        ["wrap", "start_app", "-s", "/path/to/script"],
        ["wrap", "unknown_entry_func", "-s", "/path/to/script"],
        ["--invalid-arg"],
    ],
)
def test_parse_args_rejects_incomplete_or_invalid_argv(given_argv):
    with pytest.raises(SystemExit):
        parse_args(given_argv)


@pytest.mark.parametrize(
    "given_argv, expected_target_args, expected_verbose",
    [
        (["start", "my_module:my_func"], [], 0),
        (["start", "my_module:my_func", "--", "-v", "--foo", "bar"], ["-v", "--foo", "bar"], 0),
        (["-v", "start", "my_module:my_func", "--", "-v"], ["-v"], 1),
    ],
)
def test_parse_args_target_args_after_double_dash(given_argv, expected_target_args, expected_verbose):
    """
    Behavior which `cliff` cannot describe: args after `--` are passed verbatim to `main_func`.
    """

    # when:

    actual_args = parse_args(given_argv)

    # then:

    assert actual_args.exec_operation == "start"
    assert actual_args.main_func == "my_module:my_func"
    assert actual_args.target_args == expected_target_args
    assert actual_args.stderr_log_level_verbose == expected_verbose


@pytest.mark.parametrize(
    "given_argv",
    [
        # `--` before an exec operation:
        ["--", "start", "my_module:my_func"],
        # `--` is only supported with `start`:
        ["boot", "--", "foo"],
        ["shell", "--", "foo"],
    ],
)
def test_parse_args_double_dash_is_rejected(given_argv):
    with pytest.raises(ValueError):
        parse_args(given_argv)


def test_parse_args_default_exec_operation_is_boot():
    assert parse_args(["-q"]).exec_operation == "boot"
