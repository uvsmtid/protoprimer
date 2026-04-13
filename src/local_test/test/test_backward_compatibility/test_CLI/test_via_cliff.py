"""
See: FT_78_72_23_04.backward_compatibility.md

Ensuring the stable CLI with `cliff`.

See also `test_parse_args.py` to test for various `argparse` configurations.
"""

import argparse
import pytest
from cliff.command import Command
from cliff.app import App
from cliff.commandmanager import CommandManager
from protoprimer import primer_kernel


class Boot(Command):
    """
    Bootstrap the environment to make it ready to use.
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        # We use the exact destination names as used in protoprimer for comparison:
        parser.add_argument(
            "-e",
            "--env",
            dest="selected_env_dir",
            metavar="selected_env_dir",
        )
        parser.add_argument(
            "-c",
            "--command",
            dest="run_command",
            metavar="run_command",
        )
        parser.add_argument(
            "--final_state",
            dest="final_state",
            metavar="final_state",
        )
        return parser

    def take_action(self, parsed_args):
        pass


class Reset(Command):
    """
    Re-create `venv`, re-install dependencies, and re-pin versions.
    """

    def take_action(self, parsed_args):
        pass


class Eval(Command):
    """
    Print effective config.
    """

    def take_action(self, parsed_args):
        pass


class Check(Command):
    """
    Check the environment configuration.
    """

    def take_action(self, parsed_args):
        pass


class SpecApp(App):
    """
    The stable CLI specification.
    """

    def __init__(self):
        cmd_manager = CommandManager("test_via_cliff")
        cmd_manager.add_command("boot", Boot)
        cmd_manager.add_command("reset", Reset)
        cmd_manager.add_command("eval", Eval)
        cmd_manager.add_command("check", Check)
        super().__init__(
            description="Spec App",
            version="0.1.0",
            command_manager=cmd_manager,
        )

    def build_option_parser(self, description, version, argparse_kwargs=None):
        argparse_kwargs = argparse_kwargs or {}
        argparse_kwargs.setdefault("conflict_handler", "resolve")
        parser = super().build_option_parser(description, version, argparse_kwargs)
        # Global options:
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
        return parser


def extract_parser_data(parser: argparse.ArgumentParser):
    """
    Extract a canonical structure from an argparse parser for comparison.
    """
    parser_data = {}
    for parser_action in parser._actions:
        if isinstance(parser_action, (argparse._HelpAction, argparse._SubParsersAction)):
            continue
        # We use sorted option strings as key to identify the option:
        option_key = tuple(sorted(parser_action.option_strings))
        parser_data[option_key] = {
            "dest": parser_action.dest,
            "metavar": parser_action.metavar,
            "default": parser_action.default,
            "type": str(parser_action.type),
            "choices": parser_action.choices,
        }
    return parser_data


def test_cli_structure_compatibility():
    """
    Compare the actual protoprimer parser structure with the SpecApp (cliff-based) structure.
    """

    # given:

    parent_parser = primer_kernel._create_parent_argparser()
    actual_parser = primer_kernel._create_child_argparser(
        parent_argparsers=[parent_parser],
    )
    spec_app = SpecApp()
    expected_main_parser = spec_app.build_option_parser("Spec", "0.1.0")
    actual_main_data = extract_parser_data(actual_parser)
    expected_main_data = extract_parser_data(expected_main_parser)
    expected_opts_to_check = [
        ("--quiet", "-q"),
        ("--verbose", "-v"),
    ]
    subparsers_action = next(a for a in actual_parser._actions if isinstance(a, argparse._SubParsersAction))

    # when:

    # (comparison performed in then)

    # then:
    # The main options must match the spec exactly (bidirectional):

    for opt_key in expected_opts_to_check:
        assert opt_key in actual_main_data
        assert actual_main_data[opt_key]["dest"] == expected_main_data[opt_key]["dest"]

    for opt_key in actual_main_data:
        assert opt_key in expected_main_data

    # then:
    # Subcommand options must match the spec exactly (bidirectional):

    for subcommand in ["boot", "reset", "eval"]:
        actual_subparser = subparsers_action.choices[subcommand]
        actual_sub_data = extract_parser_data(actual_subparser)

        cmd_factory, cmd_name, search_args = spec_app.command_manager.find_command([subcommand])
        cmd_instance = cmd_factory(spec_app, None, cmd_name=subcommand)
        expected_subparser = cmd_instance.get_parser("test")
        expected_sub_data = extract_parser_data(expected_subparser)

        # In cliff, subcommands might inherit global options, but in protoprimer they are shared via parents.
        # We only check the specific options for each subcommand.
        for opt_key, expected_spec in expected_sub_data.items():
            if opt_key in expected_main_data:
                continue
            assert opt_key in actual_sub_data
            assert actual_sub_data[opt_key]["dest"] == expected_spec["dest"]

        for opt_key in actual_sub_data:
            if opt_key in expected_main_data:
                continue
            assert opt_key in expected_sub_data


@pytest.mark.parametrize(
    "argv, expected_dest, expected_val",
    [
        (["-q", "boot"], "stderr_log_level_quiet", 1),
        (["boot", "-q"], "stderr_log_level_quiet", 1),
        (["-v", "-v", "reset"], "stderr_log_level_verbose", 2),
        (["boot", "-e", "my_env"], "selected_env_dir", "my_env"),
        (["boot", "--env", "my_env"], "selected_env_dir", "my_env"),
        (["boot", "-c", "my_cmd"], "run_command", "my_cmd"),
        (["boot", "--command", "my_cmd"], "run_command", "my_cmd"),
    ],
)
def test_parse_args_behavior(argv, expected_dest, expected_val):
    """
    Verify that parse_args handles inputs correctly (including two-phase parsing).
    """

    # given:

    # (argv and expected values come from parametrizing)

    # when:

    parsed_args = primer_kernel.parse_args(argv)

    # then:

    assert getattr(parsed_args, expected_dest) == expected_val


def test_default_subcommand():
    """
    Verify that `boot` is the default subcommand when none is provided.
    """

    # given:

    # (no subcommand in argv)

    # when:

    parsed_args = primer_kernel.parse_args(["-q"])

    # then:

    assert parsed_args.exec_mode == "boot"
    assert parsed_args.stderr_log_level_quiet == 1
