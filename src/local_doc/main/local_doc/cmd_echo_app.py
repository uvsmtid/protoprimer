# FT_11_27_29_83.exec_operation.md: see also `cmd_start_app_example.py`
from __future__ import annotations

import argparse


def custom_echo_app_main():
    """
    Print back the parsed positional args.

    TODO: TODO_19_13_09_01.propagate_start_sub_command_cli_args.md

    FT_05_08_64_67.start_app.md
    """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("args", nargs="*")
    parsed_args = arg_parser.parse_args()
    print(parsed_args.args)


if __name__ == "__main__":
    custom_echo_app_main()
