from __future__ import annotations

import argparse
import os
import sys

from metaprimer.script_lib import (
    configure_script,
)
from protoprimer.primer_kernel import (
    _get_shell_driver,
    EnvState,
    ParsedArg,
    SyntaxArg,
)


def custom_main():

    parsed_args = _init_arg_parser().parse_args()

    derived_data: dict = configure_script(script_basename=os.path.basename(sys.argv[0]))

    venv_dir_abs_path: str = derived_data[EnvState.state_local_venv_dir_abs_path_inited.name]
    cache_dir_abs_path: str = derived_data[EnvState.state_local_cache_dir_abs_path_inited.name]

    command_line: str | None = getattr(parsed_args, ParsedArg.name_command.value, None)

    shell_driver = _get_shell_driver(cache_dir_abs_path)
    shell_driver.run_shell(
        True,
        command_line,
        venv_dir_abs_path,
    )


def _init_arg_parser() -> argparse.ArgumentParser:

    arg_parser = argparse.ArgumentParser(
        description="Start shell with activated `venv`.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    arg_parser.add_argument(
        SyntaxArg.arg_c,
        SyntaxArg.arg_command,
        dest=ParsedArg.name_command.value,
        metavar=ParsedArg.name_command.value,
        type=str,
        default=None,
        help="Shell command to execute (non-interactive).",
    )

    return arg_parser


if __name__ == "__main__":
    custom_main()
