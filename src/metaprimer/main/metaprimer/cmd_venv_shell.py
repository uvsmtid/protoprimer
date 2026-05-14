from __future__ import annotations

import argparse
import logging
import os

from protoprimer.primer_kernel import (
    _get_shell_driver,
    ConfLeap,
    EnvState,
    get_config,
    ParsedArg,
    reconfigure_file_log_handler,
    reconfigure_stderr_log_handler,
    SyntaxArg,
)

logger = logging.getLogger()


def custom_main():

    log_handler = reconfigure_stderr_log_handler(logging.WARNING)
    reconfigure_file_log_handler(logging.INFO)

    parsed_args = _init_arg_parser().parse_args()

    proto_kernel_abs_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(str(__file__)))))),
        "cmd/proto_code/proto_kernel.py",
    )

    derived_data: dict = get_config(proto_kernel_abs_path, ConfLeap.leap_derived)

    venv_dir_abs_path: str = derived_data[EnvState.state_local_venv_dir_abs_path_inited.name]
    cache_dir_abs_path: str = derived_data[EnvState.state_local_cache_dir_abs_path_inited.name]

    command_line: str | None = getattr(parsed_args, ParsedArg.name_command.value, None)

    shell_driver = _get_shell_driver(cache_dir_abs_path)
    shell_driver.run_shell(
        True,
        command_line,
        log_handler,
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
