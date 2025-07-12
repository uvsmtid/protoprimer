#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Alexey Pakseykin
# See: https://github.com/uvsmtid/protoprimer
"""

NOTE: The script must be run with Python 3.
      Ensure that `python3` is in `PATH` for shebang to work.
      Alternatively, run under specific `python` interpreter.

To initialize the env with specific Python version:
    /path/to/pythonX ./path/to/protoprimer/entry/script.py
For example:
    /opt/bin/python ./prime

"""
from __future__ import annotations

import argparse
import atexit
import datetime
import enum
import json
import logging
import os
import pathlib
import subprocess
import sys
import tempfile
import venv

# Implements this (using the single script directly without a separate `_version.py` file):
# https://stackoverflow.com/a/7071358/441652
__version__ = "0.0.2"

from typing import (
    Any,
    Generic,
    TypeVar,
)

logger: logging.Logger = logging.getLogger()

StateValueType = TypeVar("StateValueType")


def main(configure_env_context=None):

    try:
        ensure_min_python_version()

        if configure_env_context is None:
            env_ctx = EnvContext()
        else:
            env_ctx = configure_env_context()

        state_run_mode_executed: bool = env_ctx.bootstrap_state(
            EnvState.state_run_mode_executed.name
        )
        assert state_run_mode_executed
        atexit.register(lambda: env_ctx.report_success_status(True))
    except SystemExit as sys_exit:
        if sys_exit.code == 0:
            atexit.register(lambda: env_ctx.report_success_status(True))
        else:
            atexit.register(lambda: env_ctx.report_success_status(False))
    except:
        atexit.register(lambda: env_ctx.report_success_status(False))
        raise


def ensure_min_python_version():
    """
    Ensure the running Python interpreter is >= (major, minor, patch).
    """

    # FT_84_11_73_28: supported python versions:
    version_tuple: tuple[int, int, int] = (3, 8, 0)

    if sys.version_info < version_tuple:
        raise AssertionError(
            f"The version of Python used [{sys.version_info}] is below the min required [{version_tuple}]"
        )


def init_arg_parser():

    arg_parser = argparse.ArgumentParser(
        description="Bootstraps the environment in current directory as `client_dir` `@/`.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    suppress_internal_args: bool = True

    arg_parser.add_argument(
        ArgConst.arg_context_phase,
        type=str,
        choices=[context_phase.name for context_phase in PrimerPhase],
        default=PrimerPhase.phase_proto.name,
        help=(
            argparse.SUPPRESS
            if suppress_internal_args
            else f"Select `{PrimerPhase.__name__}`."
        ),
    )
    arg_parser.add_argument(
        ArgConst.arg_s,
        ArgConst.arg_silent,
        action="store_true",
        dest=ArgConst.dest_silent,
        # In the case of exceptions, stack traces are still printed:
        help="Do not log (set only non-zero exit code on error).",
    )
    arg_parser.add_argument(
        ArgConst.arg_q,
        ArgConst.arg_quiet,
        action="store_true",
        dest=ArgConst.dest_quiet,
        help="Log errors messages only.",
    )
    arg_parser.add_argument(
        ArgConst.arg_v,
        ArgConst.arg_verbose,
        action="count",
        dest=ArgConst.dest_verbose,
        default=0,
        help="Increase log verbosity level.",
    )
    arg_parser.add_argument(
        ArgConst.arg_run_mode,
        type=str,
        choices=[run_mode.name for run_mode in RunMode],
        default=RunMode.bootstrap_env.name,
        help=f"Select {RunMode.__name__}.",
    )
    arg_parser.add_argument(
        ArgConst.arg_state_name,
        type=str,
        # TODO: Decide to print choices or not (they look too excessive):
        # choices=[env_state.name for env_state in EnvState],
        default=TargetState.target_full_proto_bootstrap,
        # TODO: Compute universal sink:
        help=f"Select target {EnvState.__name__}.",
    )
    arg_parser.add_argument(
        ArgConst.arg_proto_kernel_abs_path,
        type=str,
        default=None,
        help=(
            argparse.SUPPRESS
            if suppress_internal_args
            else f"Used internally: path to proto_kernel identified before {PythonExecutable.py_exec_venv.name}."
        ),
    )
    # TODO: use it with special `--init_repo` flag (otherwise, do not allow):
    arg_parser.add_argument(
        ArgConst.arg_client_dir_path,
        type=str,
        default=None,
        help="Path to client root dir (relative to current directory or absolute).",
    )
    arg_parser.add_argument(
        ArgConst.arg_py_exec,
        type=str,
        # TODO: Decide to print choices or not (they look too excessive):
        # choices=[py_exec.name for py_exec in PythonExecutable],
        default=PythonExecutable.py_exec_unknown.name,
        help=(
            argparse.SUPPRESS
            if suppress_internal_args
            else f"Used internally: override {PythonExecutable.__name__}."
        ),
    )
    # TODO: use it with special `--init_repo` flag (otherwise, do not allow):
    arg_parser.add_argument(
        ArgConst.arg_conf_env_path,
        type=str,
        default=None,
        # TODO: Rephrase (it should be more generic):
        help="Path to one of the dirs (normally under `@/dst/`) to be used as target for `@/conf/` symlink.",
    )
    return arg_parser


def switch_python(
    curr_py_exec: PythonExecutable,
    curr_python_path: str,
    next_py_exec: PythonExecutable,
    next_python_path: str,
    proto_kernel_abs_path: str,
):
    logger.info(
        f"switching from current `python` interpreter [{curr_python_path}][{curr_py_exec.name}] to [{next_python_path}][{next_py_exec.name}] with `{ArgConst.name_proto_kernel_abs_path}`[{proto_kernel_abs_path}]"
    )
    exec_argv: list[str] = [
        next_python_path,
        *sys.argv,
        ArgConst.arg_py_exec,
        next_py_exec.name,
    ]

    # Once `ArgConst.arg_proto_kernel_abs_path` is specified, it is never changed (no need to override):
    if ArgConst.arg_proto_kernel_abs_path not in exec_argv:
        exec_argv.extend(
            [
                ArgConst.arg_proto_kernel_abs_path,
                proto_kernel_abs_path,
            ]
        )

    os.execv(
        next_python_path,
        exec_argv,
    )


def create_temp_file():
    # TODO: avoid generating new temp file (use configured location):
    temp_file = tempfile.NamedTemporaryFile(mode="w+t", encoding="utf-8")
    return temp_file


def is_sub_path(
    abs_sub_path,
    abs_base_base,
):
    try:
        pathlib.PurePath(abs_sub_path).relative_to(pathlib.PurePath(abs_base_base))
        return True
    except ValueError:
        return False


def get_path_to_curr_python():
    return sys.executable


def get_script_command_line():
    return " ".join(sys.argv)


def read_json_file(
    file_path: str,
) -> dict:
    with open(file_path, "r", encoding="utf-8") as file_obj:
        return json.load(file_obj)


def write_json_file(
    file_path: str,
    file_data: dict,
) -> None:
    with open(file_path, "w", encoding="utf-8") as file_obj:
        json.dump(file_data, file_obj, indent=4)


def read_text_file(
    file_path: str,
) -> str:
    with open(file_path, "r", encoding="utf-8") as file_obj:
        return file_obj.read()


def write_text_file(
    file_path: str,
    file_data: str,
) -> None:
    with open(file_path, "w", encoding="utf-8") as file_obj:
        file_obj.write(file_data)


def insert_every_n_lines(
    input_text: str,
    insert_text: str,
    every_n: int,
) -> str:
    """
    Insert `insert_text` into `input_text` after `every_n` lines.

    Original use case: add boilerplate text indicating generated content throughout entire file.
    """
    input_lines: list[str] = input_text.splitlines()
    output_text = []

    for line_n, text_line in enumerate(input_lines, 1):
        output_text.append(text_line)
        if line_n % every_n == 0:
            output_text.append(insert_text)

    return (
        "\n".join(output_text)
        +
        # Add new line to ensure line of the `output_text` is not modified:
        "\n"
        +
        # This fixes the issue of fighting `pre-commit` plugins
        # when the previous new line is a trailing one
        # (which is normally removed by pre-commit):
        "###"
        + "\n"
    )


def install_package(
    package_name: str,
):
    subprocess.check_call(
        [
            get_path_to_curr_python(),
            "-m",
            "pip",
            "install",
            package_name,
        ]
    )


def install_editable_package(
    package_path: str,
    extras_list: [str],
):
    """
    Install `package_path` (assuming it is `dirname` for `setup.py`) with `extras_list`.

    When `extras_list` is `["test", "dev"]`, the actual command run is:

    ```sh
    path/to/python -m pip --editable path/to/package[test,dev]
    ```
    """

    if extras_list:
        extras_spec = ",".join(extras_list)
        package_spec = f"{package_path}[{extras_spec}]"
    else:
        package_spec = package_path

    subprocess.check_call(
        [
            get_path_to_curr_python(),
            "-m",
            "pip",
            "install",
            "--editable",
            package_spec,
        ]
    )


class ConfBundle(enum.Enum):
    """
    See: FT_89_41_35_82.conf_bundle.md
    """

    conf_proto = enum.auto()

    conf_client = enum.auto()

    conf_env = enum.auto()


class PrimerPhase(enum.Enum):
    """
    See: FT_14_52_73_23.primer_phase.md
    """

    phase_proto = enum.auto()

    phase_venv = enum.auto()


class RunMode(enum.Enum):
    """
    Various modes the script can be run in.

    See: FT_11_27_29_83.run_mode.md
    """

    print_dag = enum.auto()

    bootstrap_env = enum.auto()

    # TODO: implement:
    check_env = enum.auto()


# TODO: This is not really a visitor anymore:
class AbstractBootstrapperVisitor:
    """
    Visitor pattern to work with bootstrappers.
    """

    def visit_bootstrapper(
        self,
        state_bootstrapper: AbstractStateBootstrapper,
    ) -> None:
        raise NotImplementedError()


class DefaultBootstrapperVisitor(AbstractBootstrapperVisitor):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__()
        self.env_ctx: EnvContext = env_ctx

    def visit_bootstrapper(
        self,
        state_bootstrapper: AbstractStateBootstrapper,
    ) -> None:
        """
        This is a trivial implementation (no DAG traversal).

        This is because all dependencies will be conditionally bootstrapped by the implementation of that bootstrapper.
        """
        state_bootstrapper.bootstrap_state()


class SinkPrinterVisitor(AbstractBootstrapperVisitor):
    """
    This class prints reduced DAG of `EnvState`-s.

    Full DAG for a target may involve the same dependency/parent multiple times.
    Printing each dependency multiple times (with all its transient dependencies) looks excessive.
    Instead, this class prints each dependency/parent only if any of its siblings has not been printed yet.
    Therefore, there is some duplication, but the result is both more concise and less confusing.
    """

    rendered_no_parents: str = "[none]"

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__()
        self.env_ctx: EnvContext = env_ctx
        self.already_printed: set[str] = set()

    def visit_bootstrapper(
        self,
        state_bootstrapper: AbstractStateBootstrapper,
    ) -> None:
        self.print_bootstrapper_parents(
            state_bootstrapper,
            force_print=False,
            level=0,
        )

    def print_bootstrapper_parents(
        self,
        state_bootstrapper,
        force_print: bool,
        level: int,
    ) -> None:
        if (
            state_bootstrapper.get_env_state() in self.already_printed
            and not force_print
        ):
            return
        else:
            self.already_printed.add(state_bootstrapper.get_env_state())

        # Indented name:
        print(
            f"{' ' * level * 4}{state_bootstrapper.get_env_state()}",
            end="",
        )
        # Dependencies (parents):
        rendered_parent_states: str
        if len(state_bootstrapper.get_state_parents()) > 0:
            rendered_parent_states = " ".join(state_bootstrapper.get_state_parents())
        else:
            rendered_parent_states = self.rendered_no_parents
        print(
            f": {rendered_parent_states}",
            end="",
        )
        # new line:
        print()

        # Check ahead if any of the dependencies (parents) are not printed:
        any_parent_to_print: bool = False
        for state_parent in state_bootstrapper.get_state_parents():
            if state_parent not in self.already_printed:
                any_parent_to_print = True
                break

        # Recurse:
        if any_parent_to_print:
            for state_parent in state_bootstrapper.get_state_parents():
                self.print_bootstrapper_parents(
                    self.env_ctx.state_bootstrappers[state_parent],
                    # Even if this state was already printed, since we are printing siblings, print them all:
                    force_print=any_parent_to_print,
                    level=level + 1,
                )


class PythonExecutable(enum.IntEnum):
    """
    Python executables started during the bootstrap process - each replaces the executable program (via `os.execv`).

    See: FT_72_45_12_06.python_executable.md
    """

    # TODO: rename to `unpredictable`
    # `python` executable has not been categorized yet:
    py_exec_unknown = -1

    # To start `proto_kernel` by any `python`:
    py_exec_arbitrary = 1

    # To run `python` of specific version (to create `venv`):
    py_exec_required = 2

    # To use `venv` (to install packages):
    py_exec_venv = 3

    # To make the latest packages effective:
    py_exec_updated_protoprimer_package = 4

    # To make updated `proto_kernel` effective:
    py_exec_updated_proto_kernel_code = 5

    # TODO: make "proto" clone of client extension effective:
    py_exec_updated_client_package = 6


class AbstractStateBootstrapper(Generic[StateValueType]):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_parents: list[str],
        env_state: str,
    ):
        self.env_ctx: EnvContext = env_ctx
        self.env_state: str = env_state

        # TODO: Actually bootstrap the additional states
        #       (beyond what is bootstrapped by code):
        # The states which will be bootstrapped:
        # `state_parents` >= `state_parents`
        self.state_parents: list[str] = state_parents

        # Embed `EnvState` name into the class name:
        assert self.env_state in self.__class__.__name__

        assert type(env_state) is str

        for state_parent in state_parents:
            assert type(state_parent) is str

        state_parent: str
        for state_parent in self.state_parents:
            self.env_ctx.add_dependency_edge(
                state_parent,
                env_state,
            )

    def accept_visitor(
        self,
        bootstrapper_visitor: AbstractBootstrapperVisitor,
    ) -> None:
        bootstrapper_visitor.visit_bootstrapper(self)

    def get_env_state(
        self,
    ) -> str:
        return self.env_state

    def set_state_parents(
        self,
        state_parents: list[str],
    ):
        self.state_parents = state_parents

    def get_state_parents(
        self,
    ) -> list[str]:
        return self.state_parents

    def bootstrap_parent_state(
        self,
        parent_state: str,
    ) -> StateValueType:
        if parent_state not in self.state_parents:
            raise AssertionError(
                f"parent_state[{parent_state}] is not parent of [{self.env_state}]"
            )
        return self.env_ctx.bootstrap_state(parent_state)

    def bootstrap_state(
        self,
    ) -> StateValueType:
        self._ensure_pre_condition()
        return self._bootstrap_state()

    def _ensure_pre_condition(
        self,
    ) -> None:
        pass

    def _bootstrap_state(
        self,
    ) -> StateValueType:
        raise NotImplementedError()


class AbstractCachingStateBootstrapper(AbstractStateBootstrapper[StateValueType]):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_parents: list[str],
        env_state: str,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=state_parents,
            env_state=env_state,
        )
        self.is_bootstrapped: bool = False
        self.cached_value: StateValueType | None = None

    def _bootstrap_state(
        self,
    ) -> StateValueType:
        if not self.is_bootstrapped:
            # See: FT_30_24_95_65.state_idempotency.md
            self.cached_value = self._bootstrap_once()
            logger.debug(
                f"state [{self.env_state}] evaluated value [{self.cached_value}]"
            )
            self.is_bootstrapped = True

        return self.cached_value

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        raise NotImplementedError()


# noinspection PyPep8Naming
class Bootstrapper_state_default_stderr_log_level_specified(
    AbstractCachingStateBootstrapper[int]
):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[],
            env_state=EnvState.state_default_stderr_log_level_specified.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        state_default_stderr_log_level_specified: int = getattr(
            logging,
            os.getenv(
                EnvVarConst.name_PROTOPRIMER_DEFAULT_LOG_LEVEL,
                EnvVarConst.default_PROTOPRIMER_DEFAULT_LOG_LEVEL,
            ),
        )
        return state_default_stderr_log_level_specified


# TODO: Rename to `state_default_stderr_log_handler_configured`
# noinspection PyPep8Naming
class Bootstrapper_state_default_stderr_logger_configured(
    AbstractCachingStateBootstrapper[logging.Handler]
):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_default_stderr_log_level_specified.name,
            ],
            env_state=EnvState.state_default_stderr_logger_configured.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        # Make all warnings be captured by the logging subsystem:
        logging.captureWarnings(True)

        state_default_stderr_log_level_specified: int = self.bootstrap_parent_state(
            EnvState.state_default_stderr_log_level_specified.name
        )
        assert state_default_stderr_log_level_specified >= 0

        # Log everything (the filters are supposed to be set on output handlers instead):
        logger.setLevel(logging.NOTSET)

        stderr_handler: logging.Handler = logging.StreamHandler(sys.stderr)

        stderr_formatter = CustomFormatter()

        stderr_handler.setLevel(logging.NOTSET)
        stderr_handler.setFormatter(stderr_formatter)

        logger.addHandler(stderr_handler)

        stderr_handler.setLevel(state_default_stderr_log_level_specified)

        return stderr_handler


# noinspection PyPep8Naming
class Bootstrapper_state_args_parsed(
    AbstractCachingStateBootstrapper[argparse.Namespace]
):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[],
            env_state=EnvState.state_args_parsed.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        state_args_parsed: argparse.Namespace = init_arg_parser().parse_args()
        return state_args_parsed


# noinspection PyPep8Naming
class Bootstrapper_state_stderr_log_level_finalized(
    AbstractCachingStateBootstrapper[int]
):
    """
    There is a narrow window between the default log level is set and this state is evaluated.
    To control default log level, see `EnvVarConst.name_PROTOPRIMER_DEFAULT_LOG_LEVEL`.
    """

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_default_stderr_logger_configured.name,
                EnvState.state_args_parsed.name,
            ],
            env_state=EnvState.state_stderr_log_level_finalized.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:

        state_default_stderr_logger_configured: logging.Handler = (
            self.bootstrap_parent_state(
                EnvState.state_default_stderr_logger_configured.name
            )
        )

        parsed_args = self.bootstrap_parent_state(EnvState.state_args_parsed.name)
        stderr_log_level_silent = getattr(
            parsed_args,
            ArgConst.dest_silent,
        )
        stderr_log_level_quiet = getattr(
            parsed_args,
            ArgConst.dest_quiet,
        )
        stderr_log_level_verbose = getattr(
            parsed_args,
            ArgConst.dest_verbose,
        )
        if stderr_log_level_silent:
            # disable logs = no output:
            state_default_stderr_logger_configured.setLevel(logging.CRITICAL + 1)
        elif stderr_log_level_quiet:
            state_default_stderr_logger_configured.setLevel(logging.ERROR)
        elif stderr_log_level_verbose:
            if stderr_log_level_verbose >= 2:
                state_default_stderr_logger_configured.setLevel(logging.NOTSET)
            elif stderr_log_level_verbose == 1:
                state_default_stderr_logger_configured.setLevel(logging.DEBUG)

        return state_default_stderr_logger_configured.level


# noinspection PyPep8Naming
class Bootstrapper_state_run_mode_finalized(AbstractCachingStateBootstrapper[RunMode]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_args_parsed.name,
            ],
            env_state=EnvState.state_run_mode_finalized.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        state_args_parsed: argparse.Namespace = self.bootstrap_parent_state(
            EnvState.state_args_parsed.name
        )
        state_run_mode_finalized: RunMode = RunMode[
            getattr(
                state_args_parsed,
                ArgConst.name_run_mode,
            )
        ]
        return state_run_mode_finalized


# noinspection PyPep8Naming
class Bootstrapper_state_target_state_name_finalized(
    AbstractCachingStateBootstrapper[str]
):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_args_parsed.name,
            ],
            env_state=EnvState.state_target_state_name_finalized.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        state_args_parsed = self.bootstrap_parent_state(EnvState.state_args_parsed.name)
        state_target_state_name_finalized = getattr(
            state_args_parsed,
            ArgConst.name_state_name,
        )

        if state_target_state_name_finalized is None:
            state_target_state_name_finalized = self.env_ctx.universal_sink

        return state_target_state_name_finalized


# noinspection PyPep8Naming
class Bootstrapper_state_run_mode_executed(AbstractCachingStateBootstrapper[bool]):
    """
    This is a special bootstrapper - it traverses ALL bootstrappers.

    BUT: It does not depend on ALL bootstrappers - instead, it uses a visitor as run mode strategy implementation.
    """

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_stderr_log_level_finalized.name,
                EnvState.state_target_state_name_finalized.name,
                EnvState.state_run_mode_finalized.name,
            ],
            env_state=EnvState.state_run_mode_executed.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:

        state_stderr_log_level_finalized = self.bootstrap_parent_state(
            EnvState.state_stderr_log_level_finalized.name
        )
        assert state_stderr_log_level_finalized >= 0

        state_target_state_name_finalized: str = self.bootstrap_parent_state(
            EnvState.state_target_state_name_finalized.name
        )

        state_run_mode_finalized: RunMode = self.bootstrap_parent_state(
            EnvState.state_run_mode_finalized.name
        )

        state_bootstrapper: AbstractBootstrapperVisitor = (
            self.env_ctx.state_bootstrappers[state_target_state_name_finalized]
        )

        selected_visitor: AbstractBootstrapperVisitor
        if state_run_mode_finalized is None:
            raise ValueError(f"run mode is not defined")
        elif state_run_mode_finalized == RunMode.print_dag:
            selected_visitor = SinkPrinterVisitor(self.env_ctx)
        elif state_run_mode_finalized == RunMode.bootstrap_env:
            selected_visitor = DefaultBootstrapperVisitor(self.env_ctx)
        else:
            raise ValueError(f"cannot handle run mode [{state_run_mode_finalized}]")

        selected_visitor.visit_bootstrapper(state_bootstrapper)

        return True


# noinspection PyPep8Naming
class Bootstrapper_state_py_exec_specified(
    AbstractCachingStateBootstrapper[PythonExecutable]
):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_args_parsed.name,
            ],
            env_state=EnvState.state_py_exec_specified.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        return PythonExecutable[
            getattr(
                self.bootstrap_parent_state(EnvState.state_args_parsed.name),
                ArgConst.name_py_exec,
            )
        ]


# noinspection PyPep8Naming
class Bootstrapper_state_proto_kernel_abs_path(AbstractCachingStateBootstrapper[str]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_py_exec_specified.name,
                EnvState.state_args_parsed.name,
            ],
            env_state=EnvState.state_proto_kernel_abs_path.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:

        state_py_exec_specified: PythonExecutable = self.bootstrap_parent_state(
            EnvState.state_py_exec_specified.name
        )

        state_proto_kernel_abs_path: str
        if state_py_exec_specified.value >= PythonExecutable.py_exec_venv.value:
            state_args_parsed: argparse.Namespace = self.bootstrap_parent_state(
                EnvState.state_args_parsed.name
            )
            arg_proto_kernel_abs_path = getattr(
                state_args_parsed,
                ArgConst.name_proto_kernel_abs_path,
            )
            if arg_proto_kernel_abs_path is None:
                raise AssertionError(
                    f"`{ArgConst.arg_proto_kernel_abs_path}` is not specified at `{EnvState.state_py_exec_specified.name}` [{state_py_exec_specified}]"
                )
            state_proto_kernel_abs_path = arg_proto_kernel_abs_path
        else:
            assert not is_venv()
            state_proto_kernel_abs_path = __file__

        return state_proto_kernel_abs_path


# noinspection PyPep8Naming
class Bootstrapper_state_proto_kernel_dir_path(AbstractCachingStateBootstrapper[str]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_proto_kernel_abs_path.name,
            ],
            env_state=EnvState.state_proto_kernel_dir_path.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:

        state_proto_kernel_abs_path = self.bootstrap_parent_state(
            EnvState.state_proto_kernel_abs_path.name
        )
        state_proto_kernel_dir_path = os.path.dirname(state_proto_kernel_abs_path)

        return state_proto_kernel_dir_path


# noinspection PyPep8Naming
class Bootstrapper_state_proto_kernel_config_file_path(
    AbstractCachingStateBootstrapper[str]
):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_proto_kernel_dir_path.name,
            ],
            env_state=EnvState.state_proto_kernel_config_file_path.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        state_proto_kernel_dir_path = self.bootstrap_parent_state(
            EnvState.state_proto_kernel_dir_path.name
        )
        return os.path.join(
            state_proto_kernel_dir_path,
            ConfConstInput.default_file_basename_conf_proto,
        )


# noinspection PyPep8Naming
class Bootstrapper_state_client_dir_path_specified(
    AbstractCachingStateBootstrapper[str]
):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_args_parsed.name,
                EnvState.state_proto_kernel_config_file_path.name,
            ],
            env_state=EnvState.state_client_dir_path_specified.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:

        state_args_parsed: argparse.Namespace = self.bootstrap_parent_state(
            EnvState.state_args_parsed.name
        )

        state_client_dir_path_specified = getattr(
            state_args_parsed,
            ArgConst.name_client_dir_path,
        )

        state_proto_kernel_config_file_path = self.bootstrap_parent_state(
            EnvState.state_proto_kernel_config_file_path.name
        )

        if not os.path.exists(state_proto_kernel_config_file_path):
            if state_client_dir_path_specified is None:
                raise AssertionError(
                    f"Unable to bootstrap [{EnvState.state_client_dir_path_specified.name}]: file [{state_proto_kernel_config_file_path}] does not exists and [{ArgConst.arg_client_dir_path}] is not specified."
                )
        return state_client_dir_path_specified


# noinspection PyPep8Naming
class Bootstrapper_state_script_config_file_data(
    AbstractCachingStateBootstrapper[dict]
):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_proto_kernel_config_file_path.name,
                EnvState.state_proto_kernel_dir_path.name,
                EnvState.state_client_dir_path_specified.name,
            ],
            env_state=EnvState.state_script_config_file_data.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        state_proto_kernel_config_file_path = self.bootstrap_parent_state(
            EnvState.state_proto_kernel_config_file_path.name
        )

        file_data: dict
        if os.path.exists(state_proto_kernel_config_file_path):
            file_data = read_json_file(state_proto_kernel_config_file_path)
        else:
            state_proto_kernel_dir_path = self.bootstrap_parent_state(
                EnvState.state_proto_kernel_dir_path.name
            )
            state_client_dir_path_specified = self.bootstrap_parent_state(
                EnvState.state_client_dir_path_specified.name
            )
            assert state_client_dir_path_specified is not None

            # Generate file data when missing (first time):
            file_data = {
                # Compute value of the relative path:
                ConfConstPrimer.field_dir_rel_path_root_client: os.path.relpath(
                    state_client_dir_path_specified,
                    state_proto_kernel_dir_path,
                ),
                ConfConstPrimer.field_file_rel_path_conf_client: ConfConstPrimer.default_file_rel_path_conf_client,
            }
            write_json_file(state_proto_kernel_config_file_path, file_data)
        return file_data


# noinspection PyPep8Naming
class Bootstrapper_state_client_dir_path_configured(
    AbstractCachingStateBootstrapper[str]
):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_script_config_file_data.name,
                EnvState.state_proto_kernel_dir_path.name,
            ],
            env_state=EnvState.state_client_dir_path_configured.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        state_script_config_file_data = self.bootstrap_parent_state(
            EnvState.state_script_config_file_data.name
        )

        field_client_dir_rel_path = state_script_config_file_data[
            ConfConstPrimer.field_dir_rel_path_root_client
        ]

        state_proto_kernel_dir_path = self.bootstrap_parent_state(
            EnvState.state_proto_kernel_dir_path.name
        )

        state_client_dir_path_configured = os.path.join(
            state_proto_kernel_dir_path,
            field_client_dir_rel_path,
        )

        return os.path.normpath(state_client_dir_path_configured)


# noinspection PyPep8Naming
class Bootstrapper_state_target_dst_dir_path(AbstractCachingStateBootstrapper[str]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_args_parsed.name,
                EnvState.state_client_conf_file_data.name,
            ],
            env_state=EnvState.state_target_dst_dir_path.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        dir_rel_path_conf_env_target = getattr(
            self.bootstrap_parent_state(EnvState.state_args_parsed.name),
            ArgConst.name_conf_env_path,
        )
        if dir_rel_path_conf_env_target is None:
            state_client_conf_file_data = self.bootstrap_parent_state(
                EnvState.state_client_conf_file_data.name
            )
            dir_rel_path_conf_env_target = state_client_conf_file_data.get(
                ConfConstClient.field_dir_rel_path_conf_env_default_target,
            )
        return dir_rel_path_conf_env_target


# noinspection PyPep8Naming
class Bootstrapper_state_client_conf_file_path(AbstractCachingStateBootstrapper[str]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_client_dir_path_configured.name,
                EnvState.state_script_config_file_data.name,
            ],
            env_state=EnvState.state_client_conf_file_path.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        state_client_dir_path_configured = self.bootstrap_parent_state(
            EnvState.state_client_dir_path_configured.name
        )

        state_script_config_file_data = self.bootstrap_parent_state(
            EnvState.state_script_config_file_data.name
        )

        field_client_config_rel_path = state_script_config_file_data[
            ConfConstPrimer.field_file_rel_path_conf_client
        ]

        return os.path.join(
            state_client_dir_path_configured,
            field_client_config_rel_path,
        )


# noinspection PyPep8Naming
class Bootstrapper_state_client_conf_file_data(AbstractCachingStateBootstrapper[dict]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_client_conf_file_path.name,
            ],
            env_state=EnvState.state_client_conf_file_data.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:

        state_client_conf_file_path = self.bootstrap_parent_state(
            EnvState.state_client_conf_file_path.name
        )
        if os.path.exists(state_client_conf_file_path):
            return read_json_file(state_client_conf_file_path)
        else:
            # Generate file data when missing (first time):
            file_data = {
                # TODO: Decide how to support (or avoid) evaluation of value if it does not exist.
                #       Maybe support few actions: check_if_exists and bootstrap_if_does_not_exists?
                #       Using default when value is missing in data does not work here.
                ConfConstClient.field_dir_rel_path_conf_env_link_name: ConfConstClient.default_dir_rel_path_conf_env_link_name,
                # TODO: This should not be part of the file - defaults should be configured, not generated (or generated by extensible code):
                # ConfConstClient.field_dir_rel_path_conf_env_default_target: ConfConstClient.default_dir_rel_path_conf_env_target,
            }
            os.makedirs(
                os.path.dirname(state_client_conf_file_path),
                exist_ok=True,
            )
            write_json_file(state_client_conf_file_path, file_data)
            return file_data


# noinspection PyPep8Naming
class Bootstrapper_state_env_conf_dir_path(AbstractCachingStateBootstrapper[str]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_client_dir_path_configured.name,
                EnvState.state_client_conf_file_data.name,
            ],
            env_state=EnvState.state_env_conf_dir_path.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        file_data = self.bootstrap_parent_state(
            EnvState.state_client_conf_file_data.name
        )

        env_conf_dir_rel_path = file_data.get(
            ConfConstClient.field_dir_rel_path_conf_env_link_name,
            # TODO: Decide how to support (or avoid) evaluation of value if it does not exist.
            #       Maybe support few actions: check_if_exists and bootstrap_if_does_not_exists?
            #       Using default when value is missing in data does not work here.
            ConfConstClient.default_dir_rel_path_conf_env_link_name,
        )

        assert not os.path.isabs(env_conf_dir_rel_path)

        # Convert to absolute:
        state_env_conf_dir_path = os.path.join(
            self.bootstrap_parent_state(EnvState.state_client_dir_path_configured.name),
            env_conf_dir_rel_path,
        )

        return state_env_conf_dir_path


# noinspection PyPep8Naming
class Bootstrapper_state_target_dst_dir_path_verified(
    AbstractCachingStateBootstrapper[bool]
):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_target_dst_dir_path.name,
            ],
            env_state=EnvState.state_target_dst_dir_path_verified.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        """
        Raises exception if the target path of the `@/conf/` symlink is not allowed.

        NOTE:
        At the moment, only target paths under `client_dir` (under `@/`) are allowed.
        This is not a strict requirement and can be relaxed in the future.
        """

        state_target_dst_dir_path = self.bootstrap_parent_state(
            EnvState.state_target_dst_dir_path.name
        )
        if os.path.isabs(state_target_dst_dir_path):
            raise AssertionError(
                f"Target for `@/conf/` symlink [{state_target_dst_dir_path}] must not be absolute path."
            )
        elif ".." in pathlib.Path(state_target_dst_dir_path).parts:
            raise AssertionError(
                f"Target for `@/conf/` symlink [{state_target_dst_dir_path}] must not contain `..` path segments."
            )
        elif not os.path.isdir(state_target_dst_dir_path):
            raise AssertionError(
                f"Target for `@/conf/` symlink [{state_target_dst_dir_path}] must lead to a directory."
            )

        return True


# noinspection PyPep8Naming
class Bootstrapper_state_env_conf_dir_path_verified(
    AbstractCachingStateBootstrapper[bool]
):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_target_dst_dir_path.name,
                EnvState.state_target_dst_dir_path_verified.name,
                EnvState.state_env_conf_dir_path.name,
            ],
            env_state=EnvState.state_env_conf_dir_path_verified.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        state_env_conf_dir_path = self.bootstrap_parent_state(
            EnvState.state_env_conf_dir_path.name
        )
        state_target_dst_dir_path = self.bootstrap_parent_state(
            EnvState.state_target_dst_dir_path.name
        )
        if os.path.exists(state_env_conf_dir_path):
            if os.path.islink(state_env_conf_dir_path):
                if os.path.isdir(state_env_conf_dir_path):
                    if state_target_dst_dir_path is None:
                        pass
                    else:
                        conf_dir_path = os.readlink(state_env_conf_dir_path)
                        if os.path.normpath(
                            state_target_dst_dir_path
                        ) == os.path.normpath(conf_dir_path):
                            pass
                        else:
                            raise AssertionError(
                                f"The `@/conf/` target [{conf_dir_path}] is not the same as the provided target [{state_target_dst_dir_path}]."
                            )
                else:
                    raise AssertionError(
                        f"The `@/conf/` [{state_env_conf_dir_path}] target is not a directory.",
                    )
            else:
                raise AssertionError(
                    f"The `@/conf/` [{state_env_conf_dir_path}] is not a symlink.",
                )
        else:
            if state_target_dst_dir_path is None:
                raise AssertionError(
                    f"The `@/conf/` dir does not exists and `{ArgConst.name_conf_env_path}` is not provided - see `--help`.",
                )
            else:
                state_target_dst_dir_path_verified = self.bootstrap_parent_state(
                    EnvState.state_target_dst_dir_path_verified.name
                )
                assert state_target_dst_dir_path_verified

                os.symlink(
                    os.path.normpath(state_target_dst_dir_path),
                    state_env_conf_dir_path,
                )

        return True


# noinspection PyPep8Naming
class Bootstrapper_state_env_conf_file_path(AbstractCachingStateBootstrapper[str]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_client_dir_path_configured.name,
                EnvState.state_env_conf_dir_path.name,
                EnvState.state_env_conf_dir_path_verified.name,
            ],
            env_state=EnvState.state_env_conf_file_path.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        state_env_conf_dir_path_verified = self.bootstrap_parent_state(
            EnvState.state_env_conf_dir_path_verified.name
        )
        assert state_env_conf_dir_path_verified

        state_client_dir_path_configured = self.bootstrap_parent_state(
            EnvState.state_client_dir_path_configured.name
        )
        state_env_conf_file_path = os.path.join(
            state_client_dir_path_configured,
            ConfConstClient.default_dir_rel_path_conf_env_link_name,
            # TODO: Do not use default values directly - resolve it differently at the prev|next step based on the need:
            ConfConstClient.default_file_basename_conf_env,
        )
        state_env_conf_dir_path = self.bootstrap_parent_state(
            EnvState.state_env_conf_dir_path.name
        )
        # TODO: Ensure the path is under with proper error message:
        assert is_sub_path(
            state_env_conf_file_path,
            state_env_conf_dir_path,
        )
        return state_env_conf_file_path


# noinspection PyPep8Naming
class Bootstrapper_state_env_conf_file_data(AbstractCachingStateBootstrapper[dict]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_env_conf_file_path.name,
            ],
            env_state=EnvState.state_env_conf_file_data.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        state_env_conf_file_path = self.bootstrap_parent_state(
            EnvState.state_env_conf_file_path.name
        )
        file_data: dict
        if os.path.exists(state_env_conf_file_path):
            file_data = read_json_file(state_env_conf_file_path)
        else:
            file_data = {
                # TODO: Do not use default values directly - resolve it differently at the prev|next step based on the need:
                ConfConstEnv.field_file_abs_path_python: ConfConstEnv.default_file_abs_path_python,
                # TODO: Do not use default values directly - resolve it differently at the prev|next step based on the need:
                ConfConstEnv.field_dir_rel_path_venv: ConfConstEnv.default_dir_rel_path_venv,
            }
            # TODO: This creates a directory with `ConfConstClient.default_dir_rel_path_conf_env_link_name` instead of symlink.
            #       But this happens only if dependency
            #       `state_env_conf_file_path` -> `state_env_conf_dir_path_verified`
            #       was not executed (which is not possible outside of tests).
            write_json_file(state_env_conf_file_path, file_data)
        return file_data


# noinspection PyPep8Naming
class Bootstrapper_state_env_path_to_python(AbstractCachingStateBootstrapper[str]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_env_conf_file_data.name,
            ],
            env_state=EnvState.state_env_path_to_python.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        file_data = self.bootstrap_parent_state(EnvState.state_env_conf_file_data.name)

        state_env_path_to_python = file_data.get(
            ConfConstEnv.field_file_abs_path_python,
            # TODO: Do not use default values directly - resolve it differently at the prev|next step based on the need:
            ConfConstEnv.default_file_abs_path_python,
        )

        if not os.path.isabs(state_env_path_to_python):
            state_env_path_to_python = os.path.join(
                self.bootstrap_parent_state(
                    EnvState.state_client_dir_path_configured.name
                ),
                state_env_path_to_python,
            )

        return state_env_path_to_python


# noinspection PyPep8Naming
class Bootstrapper_state_env_path_to_venv(AbstractCachingStateBootstrapper[str]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_env_conf_file_data.name,
                EnvState.state_client_dir_path_configured.name,
            ],
            env_state=EnvState.state_env_path_to_venv.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        file_data = self.bootstrap_parent_state(EnvState.state_env_conf_file_data.name)

        state_env_path_to_venv = file_data.get(
            ConfConstEnv.field_dir_rel_path_venv,
            # TODO: Do not use default values directly - resolve it differently at the prev|next step based on the need:
            ConfConstEnv.default_dir_rel_path_venv,
        )

        if not os.path.isabs(state_env_path_to_venv):
            state_env_path_to_venv = os.path.join(
                self.bootstrap_parent_state(
                    EnvState.state_client_dir_path_configured.name
                ),
                state_env_path_to_venv,
            )

        return state_env_path_to_venv


# noinspection PyPep8Naming
class Bootstrapper_state_py_exec_selected(
    AbstractCachingStateBootstrapper[PythonExecutable]
):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_py_exec_specified.name,
                EnvState.state_env_path_to_python.name,
                EnvState.state_env_path_to_venv.name,
                EnvState.state_env_conf_file_path.name,
                EnvState.state_proto_kernel_abs_path.name,
            ],
            env_state=EnvState.state_py_exec_selected.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        """
        Recursively runs this script inside the `python` interpreter required by the user.

        The `python` interpreter required by the user is saved into `field_file_abs_path_python`.
        Otherwise, it matches the interpreter the bootstrap script is executed with at the moment.
        """

        state_py_exec_selected: PythonExecutable

        state_py_exec_specified: PythonExecutable = self.bootstrap_parent_state(
            EnvState.state_py_exec_specified.name
        )

        state_proto_kernel_abs_path: str = self.bootstrap_parent_state(
            EnvState.state_proto_kernel_abs_path.name
        )

        state_env_path_to_python = self.bootstrap_parent_state(
            EnvState.state_env_path_to_python.name
        )
        state_env_path_to_venv = self.bootstrap_parent_state(
            EnvState.state_env_path_to_venv.name
        )

        # TODO: Make it separate validation state
        #       (not a dependency of this because, technically, we do not know where `EnvState.state_env_path_to_python` and `EnvState.state_env_path_to_venv` came from):
        if is_sub_path(state_env_path_to_python, state_env_path_to_venv):
            state_env_conf_file_path = self.bootstrap_parent_state(
                EnvState.state_env_conf_file_path.name
            )
            raise AssertionError(
                f"The [{state_env_path_to_python}] is a sub-path of the [{state_env_path_to_venv}]. "
                f"This is not allowed because `path_to_python` is used to init `venv` and cannot rely on `venv` existance. "
                f"Specify different `{EnvState.state_env_path_to_python.name}` (e.g. `/usr/bin/python3`). "
                # TODO: compute path for `proto_kernel.py`
                f"Alternatively, remove [{state_env_conf_file_path}] and re-run `@/cmd/proto_kernel.py` "
                f"to re-create it automatically. "
            )

        venv_path_to_python = os.path.join(
            state_env_path_to_venv,
            ConfConstGeneral.file_rel_path_venv_python,
        )
        path_to_curr_python = get_path_to_curr_python()
        if is_sub_path(path_to_curr_python, state_env_path_to_venv):
            if path_to_curr_python != venv_path_to_python:
                assert state_py_exec_specified == PythonExecutable.py_exec_unknown
                state_py_exec_selected = PythonExecutable.py_exec_arbitrary
                # Ensure `python` is from the correct `venv` path
                switch_python(
                    curr_py_exec=state_py_exec_specified,
                    curr_python_path=path_to_curr_python,
                    next_py_exec=PythonExecutable.py_exec_required,
                    next_python_path=state_env_path_to_python,
                    proto_kernel_abs_path=state_proto_kernel_abs_path,
                )
            else:
                # If already under `venv` with the expected path, nothing to do.
                assert (
                    state_py_exec_specified == PythonExecutable.py_exec_unknown
                    or state_py_exec_specified >= PythonExecutable.py_exec_venv
                )
                # Successfully reached end goal:
                if state_py_exec_specified == PythonExecutable.py_exec_unknown:
                    state_py_exec_selected = PythonExecutable.py_exec_venv
                else:
                    state_py_exec_selected = state_py_exec_specified
        else:
            if path_to_curr_python != state_env_path_to_python:
                assert state_py_exec_specified == PythonExecutable.py_exec_unknown
                state_py_exec_selected = PythonExecutable.py_exec_arbitrary
                switch_python(
                    curr_py_exec=state_py_exec_specified,
                    curr_python_path=path_to_curr_python,
                    next_py_exec=PythonExecutable.py_exec_required,
                    next_python_path=state_env_path_to_python,
                    proto_kernel_abs_path=state_proto_kernel_abs_path,
                )
            else:
                assert (
                    state_py_exec_specified == PythonExecutable.py_exec_unknown
                    or state_py_exec_specified == PythonExecutable.py_exec_required
                )
                state_py_exec_selected = PythonExecutable.py_exec_required
                if not os.path.exists(state_env_path_to_venv):
                    logger.info(f"creating `venv` [{state_env_path_to_venv}]")
                    venv.create(
                        state_env_path_to_venv,
                        with_pip=True,
                    )
                else:
                    logger.info(f"reusing existing `venv` [{state_env_path_to_venv}]")
                switch_python(
                    curr_py_exec=state_py_exec_specified,
                    curr_python_path=state_env_path_to_python,
                    next_py_exec=PythonExecutable.py_exec_venv,
                    next_python_path=venv_path_to_python,
                    proto_kernel_abs_path=state_proto_kernel_abs_path,
                )

        return state_py_exec_selected


# noinspection PyPep8Naming
class Bootstrapper_state_protoprimer_package_installed(
    AbstractCachingStateBootstrapper[bool]
):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_py_exec_selected.name,
                EnvState.state_client_dir_path_configured.name,
            ],
            env_state=EnvState.state_protoprimer_package_installed.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        state_py_exec_selected: PythonExecutable = self.bootstrap_parent_state(
            EnvState.state_py_exec_selected.name
        )
        assert state_py_exec_selected >= PythonExecutable.py_exec_venv

        state_client_dir_path_configured = self.bootstrap_parent_state(
            EnvState.state_client_dir_path_configured.name
        )

        if state_py_exec_selected == PythonExecutable.py_exec_venv:
            # protoprimer:
            # TODO: this should be configurable:
            setup_py_dir = os.path.join(
                state_client_dir_path_configured,
                "src",
                "protoprimer",
            )
            assert os.path.isfile(os.path.join(setup_py_dir, "setup.py"))
            # TODO: This has to be changed for released version of `primer_kernel`:
            install_editable_package(
                setup_py_dir,
                # TODO: this should be configurable:
                [],
            )
            # local_repo:
            setup_py_dir = os.path.join(
                state_client_dir_path_configured,
                "src",
                "local_repo",
            )
            install_editable_package(
                setup_py_dir,
                # TODO: this should be configurable:
                [],
            )
            # local_test:
            setup_py_dir = os.path.join(
                state_client_dir_path_configured,
                "src",
                "local_test",
            )
            install_editable_package(
                setup_py_dir,
                # TODO: this should be configurable:
                [],
            )

        return True


# noinspection PyPep8Naming
class Bootstrapper_state_py_exec_updated_protoprimer_package_reached(
    AbstractCachingStateBootstrapper[PythonExecutable]
):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_py_exec_specified.name,
                EnvState.state_proto_kernel_abs_path.name,
                EnvState.state_protoprimer_package_installed.name,
            ],
            env_state=EnvState.state_py_exec_updated_protoprimer_package_reached.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:

        state_py_exec_updated_protoprimer_package_reached: PythonExecutable

        state_py_exec_specified: PythonExecutable = self.bootstrap_parent_state(
            EnvState.state_py_exec_specified.name
        )

        state_proto_kernel_abs_path: str = self.bootstrap_parent_state(
            EnvState.state_proto_kernel_abs_path.name
        )

        state_protoprimer_package_installed: bool = self.bootstrap_parent_state(
            EnvState.state_protoprimer_package_installed.name
        )
        assert state_protoprimer_package_installed

        venv_path_to_python = get_path_to_curr_python()

        if (
            state_py_exec_specified.value
            < PythonExecutable.py_exec_updated_protoprimer_package.value
        ):
            state_py_exec_updated_protoprimer_package_reached = (
                PythonExecutable.py_exec_updated_protoprimer_package
            )
            # TODO: maybe add this reason to `switch_python` as an arg?
            logger.debug(
                f"restarting current `python` interpreter [{venv_path_to_python}] to make [{EnvState.state_protoprimer_package_installed.name}] effective"
            )
            switch_python(
                curr_py_exec=state_py_exec_specified,
                curr_python_path=venv_path_to_python,
                next_py_exec=PythonExecutable.py_exec_updated_protoprimer_package,
                next_python_path=venv_path_to_python,
                proto_kernel_abs_path=state_proto_kernel_abs_path,
            )
        else:
            # Successfully reached end goal:
            state_py_exec_updated_protoprimer_package_reached = state_py_exec_specified

        return state_py_exec_updated_protoprimer_package_reached


# noinspection PyPep8Naming
class Bootstrapper_state_proto_kernel_updated(AbstractCachingStateBootstrapper[bool]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_py_exec_updated_protoprimer_package_reached.name,
                EnvState.state_proto_kernel_abs_path.name,
            ],
            env_state=EnvState.state_proto_kernel_updated.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        state_py_exec_updated_protoprimer_package_reached: PythonExecutable = (
            self.bootstrap_parent_state(
                EnvState.state_py_exec_updated_protoprimer_package_reached.name
            )
        )
        assert (
            state_py_exec_updated_protoprimer_package_reached
            >= PythonExecutable.py_exec_updated_protoprimer_package
        )

        # TODO: optimize: run this logic only when `PythonExecutable.py_exec_updated_protoprimer_package`

        state_proto_kernel_abs_path = self.bootstrap_parent_state(
            EnvState.state_proto_kernel_abs_path.name
        )
        assert os.path.isabs(state_proto_kernel_abs_path)
        assert not os.path.islink(state_proto_kernel_abs_path)
        assert os.path.isfile(state_proto_kernel_abs_path)

        assert is_venv()
        # TODO: This has to be changed for released names of the package:
        import protoprimer

        # Use generator from immutable (source) `primer_kernel` to avoid
        # generated code inside generated code inside generated code ...
        # in local (target) `proto_kernel`:
        generated_content = protoprimer.primer_kernel.ConfConstGeneral.func_get_proto_kernel_generated_boilerplate(
            protoprimer.primer_kernel
        )

        primer_kernel_abs_path = protoprimer.primer_kernel.__file__
        primer_kernel_text = read_text_file(primer_kernel_abs_path)
        assert primer_kernel_text.count(generated_content) < 10

        proto_kernel_text = insert_every_n_lines(
            input_text=primer_kernel_text,
            insert_text=generated_content,
            every_n=20,
        )

        logger.debug(
            f"writing `primer_kernel_abs_path` [{primer_kernel_abs_path}] over `state_proto_kernel_abs_path` [{state_proto_kernel_abs_path}]"
        )
        write_text_file(
            file_path=state_proto_kernel_abs_path,
            file_data=proto_kernel_text,
        )

        # TODO: optimize: return true if content changed:

        return True


# noinspection PyPep8Naming
class Bootstrapper_state_py_exec_updated_proto_kernel_code(
    AbstractCachingStateBootstrapper[PythonExecutable]
):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_py_exec_specified.name,
                EnvState.state_proto_kernel_updated.name,
                EnvState.state_proto_kernel_abs_path.name,
            ],
            env_state=EnvState.state_py_exec_updated_proto_kernel_code.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:

        state_py_exec_updated_proto_kernel_code: PythonExecutable

        state_py_exec_specified: PythonExecutable = self.bootstrap_parent_state(
            EnvState.state_py_exec_specified.name
        )

        state_proto_kernel_abs_path: str = self.bootstrap_parent_state(
            EnvState.state_proto_kernel_abs_path.name
        )

        state_proto_kernel_updated: bool = self.bootstrap_parent_state(
            EnvState.state_proto_kernel_updated.name
        )
        assert state_proto_kernel_updated

        venv_path_to_python = get_path_to_curr_python()

        if (
            state_py_exec_specified.value
            < PythonExecutable.py_exec_updated_proto_kernel_code.value
        ):
            state_py_exec_updated_proto_kernel_code = (
                PythonExecutable.py_exec_updated_proto_kernel_code
            )
            # TODO: maybe add this reason to `switch_python` as an arg?
            logger.debug(
                f"restarting current `python` interpreter [{venv_path_to_python}] to make [{EnvState.state_proto_kernel_updated.name}] effective"
            )
            switch_python(
                curr_py_exec=state_py_exec_specified,
                curr_python_path=venv_path_to_python,
                next_py_exec=PythonExecutable.py_exec_updated_proto_kernel_code,
                next_python_path=venv_path_to_python,
                proto_kernel_abs_path=state_proto_kernel_abs_path,
            )
        else:
            # Successfully reached end goal:
            state_py_exec_updated_proto_kernel_code = state_py_exec_specified

        return state_py_exec_updated_proto_kernel_code


# TODO: Move this `state_activated_venv_shell_started` to some `protoprimer.*` module with extra states ("neo", not "proto") because it beyond `venv`.
# noinspection PyPep8Naming
class Bootstrapper_state_activated_venv_shell_started(
    AbstractCachingStateBootstrapper[bool]
):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_py_exec_updated_proto_kernel_code.name,
                EnvState.state_env_path_to_venv.name,
            ],
            env_state=EnvState.state_activated_venv_shell_started.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:

        state_py_exec_updated_proto_kernel_code = self.bootstrap_parent_state(
            EnvState.state_py_exec_updated_proto_kernel_code.name
        )

        # TODO: this should be the last executable here:
        assert (
            state_py_exec_updated_proto_kernel_code
            >= PythonExecutable.py_exec_updated_protoprimer_package
        )

        state_env_path_to_venv = self.bootstrap_parent_state(
            EnvState.state_env_path_to_venv.name
        )

        venv_path_to_activate = os.path.join(
            state_env_path_to_venv,
            ConfConstGeneral.file_rel_path_venv_activate,
        )

        temp_file = create_temp_file()
        temp_file.write(f"source ~/.bashrc && source {venv_path_to_activate}")
        temp_file.flush()
        file_path = temp_file.name
        logger.info(f"file_path: {file_path}")
        os.execv(
            # TODO: get path automatically:
            "/usr/bin/bash",
            [
                "bash",
                "--init-file",
                file_path,
            ],
        )

        # noinspection PyUnreachableCode
        return True


class EnvState(enum.Enum):
    """
    Configuration states to be bootstrapped during the bootstrap process.

    NOTE: Only `str` names of the enum items are supposed to be used (any value is ignored).

    See: FT_68_54_41_96.state_dependency.md
    """

    def __init__(
        self,
        # Default implementation (for reference):
        default_impl,
    ):
        self.default_impl = default_impl

    state_default_stderr_log_level_specified = (
        Bootstrapper_state_default_stderr_log_level_specified,
    )

    state_default_stderr_logger_configured = (
        Bootstrapper_state_default_stderr_logger_configured,
    )

    state_args_parsed = (Bootstrapper_state_args_parsed,)

    state_stderr_log_level_finalized = (Bootstrapper_state_stderr_log_level_finalized,)

    state_run_mode_finalized = (Bootstrapper_state_run_mode_finalized,)

    state_target_state_name_finalized = (
        Bootstrapper_state_target_state_name_finalized,
    )

    # Special case: triggers everything:
    state_run_mode_executed = (Bootstrapper_state_run_mode_executed,)

    state_py_exec_specified = (Bootstrapper_state_py_exec_specified,)

    state_proto_kernel_abs_path = (Bootstrapper_state_proto_kernel_abs_path,)

    # TODO: rename to `proto_kernel_abs_dir_path`:
    state_proto_kernel_dir_path = (Bootstrapper_state_proto_kernel_dir_path,)

    state_proto_kernel_config_file_path = (
        Bootstrapper_state_proto_kernel_config_file_path,
    )

    state_client_dir_path_specified = (Bootstrapper_state_client_dir_path_specified,)

    # TODO: Rename to avoid `script`:
    state_script_config_file_data = (Bootstrapper_state_script_config_file_data,)

    state_client_dir_path_configured = (Bootstrapper_state_client_dir_path_configured,)

    # TODO:
    # state_cli_log_level

    state_client_conf_file_path = (Bootstrapper_state_client_conf_file_path,)

    state_client_conf_file_data = (Bootstrapper_state_client_conf_file_data,)

    # TODO:
    # state_client_log_level

    # TODO:
    # state_client_path_to_python

    # TODO:
    # state_client_path_to_venv

    state_env_conf_dir_path = (Bootstrapper_state_env_conf_dir_path,)

    # TODO: rename in relation to `ArgConst.arg_conf_env_path`
    state_target_dst_dir_path = (Bootstrapper_state_target_dst_dir_path,)

    state_target_dst_dir_path_verified = (
        Bootstrapper_state_target_dst_dir_path_verified,
    )

    state_env_conf_dir_path_verified = (Bootstrapper_state_env_conf_dir_path_verified,)

    state_env_conf_file_path = (Bootstrapper_state_env_conf_file_path,)

    state_env_conf_file_data = (Bootstrapper_state_env_conf_file_data,)

    # TODO:
    # state_env_log_level

    state_env_path_to_python = (Bootstrapper_state_env_path_to_python,)

    state_env_path_to_venv = (Bootstrapper_state_env_path_to_venv,)

    # TODO: rename to `py_exec_venv_reached`:
    state_py_exec_selected = (Bootstrapper_state_py_exec_selected,)

    # TODO: rename according to the final name:
    state_protoprimer_package_installed = (
        Bootstrapper_state_protoprimer_package_installed,
    )

    # TODO: rename - "reached" sounds weird (and makes no sense):
    state_py_exec_updated_protoprimer_package_reached = (
        Bootstrapper_state_py_exec_updated_protoprimer_package_reached,
    )

    # TODO: rename according to the final name:
    state_proto_kernel_updated = (Bootstrapper_state_proto_kernel_updated,)

    state_py_exec_updated_proto_kernel_code = (
        Bootstrapper_state_py_exec_updated_proto_kernel_code,
    )

    state_activated_venv_shell_started = (
        Bootstrapper_state_activated_venv_shell_started,
    )


class TargetState:
    """
    Special `EnvState`-s.
    """

    target_full_proto_bootstrap: str = (
        EnvState.state_py_exec_updated_proto_kernel_code.name
    )

    target_stderr_log_handler: str = (
        EnvState.state_default_stderr_logger_configured.name
    )

    target_activated_venv_shell: str = EnvState.state_activated_venv_shell_started.name


class EnvVarConst:
    """
    See FT_08_92_69_92.env_var.md
    """

    name_PROTOPRIMER_DEFAULT_LOG_LEVEL: str = "PROTOPRIMER_DEFAULT_LOG_LEVEL"

    default_PROTOPRIMER_DEFAULT_LOG_LEVEL: str = "INFO"


class ArgConst:

    name_proto_kernel_abs_path = "proto_kernel_abs_path"
    name_conf_env_path = "conf_env_path"
    name_client_dir_path = "client_dir_path"
    name_py_exec = "py_exec"
    name_context_phase = "context_phase"
    name_run_mode = "run_mode"
    name_state_name = "state_name"

    name_s = "s"
    name_silent = "silent"

    name_q = "q"
    name_quiet = "quiet"

    name_v = "v"
    name_verbose = "verbose"

    # TODO: Add file_log_level:
    prefix_stderr_log_level = "stderr_log_level"

    arg_proto_kernel_abs_path = f"--{name_proto_kernel_abs_path}"
    arg_conf_env_path = f"--{name_conf_env_path}"
    arg_client_dir_path = f"--{name_client_dir_path}"
    arg_py_exec = f"--{name_py_exec}"
    arg_context_phase = f"--{name_context_phase}"
    arg_run_mode = f"--{name_run_mode}"
    arg_state_name = f"--{name_state_name}"

    arg_s = f"-{name_s}"
    arg_silent = f"--{name_silent}"
    value_silent = f"--{name_silent}"
    dest_silent = f"log_level_{name_silent}"

    arg_q = f"-{name_q}"
    arg_quiet = f"--{name_quiet}"
    dest_quiet = f"log_level_{name_quiet}"

    arg_v = f"-{name_v}"
    arg_verbose = f"--{name_verbose}"
    dest_verbose = f"log_level_{name_verbose}"


class ConfConstGeneral:

    default_primer_kernel_module = "primer_kernel"
    default_proto_kernel_module = "proto_kernel"
    default_proto_kernel_basename = f"{default_proto_kernel_module}.py"

    # TODO: use lambdas to generate based on input (instead of None):
    # This is a value declared for completeness,
    # but unused (evaluated dynamically via the bootstrap process):
    input_based = None

    file_rel_path_venv_python = os.path.join(
        "bin",
        "python",
    )

    file_rel_path_venv_activate = os.path.join(
        "bin",
        "activate",
    )

    # TODO: rename according to the final name:
    func_get_proto_kernel_generated_boilerplate = lambda module_obj: (
        f"""
################################################################################
# Generated content:
# This is a copy of `{module_obj.__name__}` (proto) updated automatically.
# It is supposed to be versioned (to be available in the dst repo on clone),
# but it should not be linted (as its content/style is owned by the src repo).
################################################################################
"""
    )


class ConfConstInput:
    """
    Constants input config phase.
    """

    file_abs_path_script = ConfConstGeneral.input_based
    dir_abs_path_current = ConfConstGeneral.input_based

    default_file_basename_conf_proto = f"{ConfBundle.conf_proto.name}.{ConfConstGeneral.default_primer_kernel_module}.json"


class ConfConstPrimer:
    """
    Constants primer config phase.
    """

    field_dir_rel_path_root_client = "dir_rel_path_root_client"

    field_file_rel_path_conf_client = "file_rel_path_conf_client"

    default_file_rel_path_conf_client = os.path.join(
        "conf_client",
        f"conf_client.{ConfConstGeneral.default_primer_kernel_module}.json",
    )


class ConfConstClient:
    """
    Constants client config phase.
    """

    field_dir_rel_path_conf_env_link_name = "dir_rel_path_conf_env_link_name"

    field_dir_rel_path_conf_env_default_target = "dir_rel_path_conf_env_default_target"

    default_dir_rel_path_conf_env_link_name = os.path.join(
        "conf_env",
    )

    default_file_basename_conf_env = (
        f"conf_env.{ConfConstGeneral.default_primer_kernel_module}.json"
    )

    # TODO: Delete this - the default can only be provided by client (config or code):
    # default_dir_rel_path_conf_env_target = os.path.join(
    #     "dst_conf_env",
    #     "default_env",
    # )


class ConfConstEnv:
    """
    Constants env config phase.
    """

    field_file_abs_path_python = "file_abs_path_python"
    field_dir_rel_path_venv = "dir_rel_path_venv"

    default_file_abs_path_python = "/usr/bin/python"
    default_dir_rel_path_venv = "venv"


class EnvContext:

    def __init__(
        self,
    ):

        self.state_bootstrappers: dict[str, AbstractStateBootstrapper] = {}
        self.dependency_edges: list[tuple[str, str]] = []

        self.register_bootstrapper(
            Bootstrapper_state_default_stderr_log_level_specified(self)
        )
        self.register_bootstrapper(
            Bootstrapper_state_default_stderr_logger_configured(self)
        )
        self.register_bootstrapper(Bootstrapper_state_args_parsed(self))
        self.register_bootstrapper(Bootstrapper_state_stderr_log_level_finalized(self))
        self.register_bootstrapper(Bootstrapper_state_run_mode_finalized(self))
        self.register_bootstrapper(Bootstrapper_state_target_state_name_finalized(self))
        self.register_bootstrapper(Bootstrapper_state_run_mode_executed(self))
        self.register_bootstrapper(Bootstrapper_state_py_exec_specified(self))
        self.register_bootstrapper(Bootstrapper_state_proto_kernel_abs_path(self))
        self.register_bootstrapper(Bootstrapper_state_proto_kernel_dir_path(self))
        self.register_bootstrapper(
            Bootstrapper_state_proto_kernel_config_file_path(self)
        )
        self.register_bootstrapper(Bootstrapper_state_client_dir_path_specified(self))
        self.register_bootstrapper(Bootstrapper_state_script_config_file_data(self))
        self.register_bootstrapper(Bootstrapper_state_client_dir_path_configured(self))
        self.register_bootstrapper(Bootstrapper_state_target_dst_dir_path(self))
        self.register_bootstrapper(Bootstrapper_state_client_conf_file_path(self))
        self.register_bootstrapper(Bootstrapper_state_client_conf_file_data(self))
        self.register_bootstrapper(Bootstrapper_state_env_conf_dir_path(self))
        self.register_bootstrapper(
            Bootstrapper_state_target_dst_dir_path_verified(self)
        )
        self.register_bootstrapper(Bootstrapper_state_env_conf_dir_path_verified(self))
        self.register_bootstrapper(Bootstrapper_state_env_conf_file_path(self))
        self.register_bootstrapper(Bootstrapper_state_env_conf_file_data(self))
        self.register_bootstrapper(Bootstrapper_state_env_path_to_python(self))
        self.register_bootstrapper(Bootstrapper_state_env_path_to_venv(self))
        self.register_bootstrapper(Bootstrapper_state_py_exec_selected(self))
        self.register_bootstrapper(
            Bootstrapper_state_protoprimer_package_installed(self)
        )
        self.register_bootstrapper(
            Bootstrapper_state_py_exec_updated_protoprimer_package_reached(self)
        )
        self.register_bootstrapper(Bootstrapper_state_proto_kernel_updated(self))
        self.register_bootstrapper(
            Bootstrapper_state_py_exec_updated_proto_kernel_code(self)
        )
        self.register_bootstrapper(
            Bootstrapper_state_activated_venv_shell_started(self)
        )

        self.populate_dependencies()

        # TODO: Do not set it on Context - use bootstrap-able values:
        # TODO: Find "Universal Sink":
        self.universal_sink: str = TargetState.target_full_proto_bootstrap

    def register_bootstrapper(
        self,
        state_bootstrapper: AbstractStateBootstrapper,
    ):
        env_state: str = state_bootstrapper.get_env_state()
        if env_state in self.state_bootstrappers:
            raise AssertionError(
                f"[{AbstractStateBootstrapper.__name__}] for [{env_state}] is already registered."
            )
        else:
            self.state_bootstrappers[env_state] = state_bootstrapper

    def add_dependency_edge(
        self,
        parent_state: str,
        child_state: str,
    ):
        self.dependency_edges.append((parent_state, child_state))

    def populate_dependencies(
        self,
    ):
        # Populate a temporary collection of all children per parent:
        child_parents: dict[str, list[str]] = {}
        dependency_edge: tuple[str, str]
        for dependency_edge in self.dependency_edges:
            parent_dependency: str = dependency_edge[0]
            child_dependency: str = dependency_edge[1]
            child_parents.setdefault(child_dependency, []).append(parent_dependency)

        # Set children per parent:
        for child_id in child_parents.keys():
            state_bootstrapper: AbstractStateBootstrapper = self.state_bootstrappers[
                child_id
            ]
            state_parents: list[str] = child_parents[child_id]
            state_bootstrapper.set_state_parents(state_parents)

    def bootstrap_state(
        self,
        env_state: str,
    ) -> Any:
        try:
            state_bootstrapper = self.state_bootstrappers[env_state]
        except KeyError:
            logger.error(f"`env_state` [{env_state}] is not registered.")
            raise
        return state_bootstrapper.bootstrap_state()

    def report_success_status(
        self,
        is_successful: bool,
    ):
        """
        Print a color-coded status message to stderr.
        """

        color_success = "\033[42m\033[30m"
        color_failure = "\033[41m\033[97m"
        color_reset = "\033[0m"

        target_stderr_log_handler: logging.Handler = self.bootstrap_state(
            TargetState.target_stderr_log_handler
        )

        is_reportable: bool
        if is_successful:
            color_status = color_success
            status_name = "SUCCESS"
            is_reportable = target_stderr_log_handler.level <= logging.INFO
        else:
            color_status = color_failure
            status_name = "FAILURE"
            is_reportable = target_stderr_log_handler.level <= logging.CRITICAL

        if is_reportable:
            print(
                f"{color_status}{status_name}{color_reset}: {get_path_to_curr_python()} {get_script_command_line()}",
                file=sys.stderr,
                flush=True,
            )


class CustomFormatter(logging.Formatter):
    """
    Custom formatter with color and proper timestamp.
    """

    def __init__(
        self,
    ):
        # noinspection SpellCheckingInspection
        super().__init__(
            fmt="%(asctime)s %(process)d %(levelname)s %(filename)s:%(lineno)d %(message)s",
        )

    # noinspection SpellCheckingInspection
    def formatTime(
        self,
        log_record,
        datefmt=None,
    ):
        # Format date without millis:
        formatted_timestamp = datetime.datetime.fromtimestamp(
            log_record.created
        ).strftime("%Y-%m-%d %H:%M:%S")

        # Append millis with dot `.` as a separator:
        return f"{formatted_timestamp}.{int(log_record.msecs):03d}"

    # ANSI escape codes for colors:
    color_reset = "\033[0m"
    color_set = {
        # cyan:
        "DEBUG": "\033[36m",
        # green:
        "INFO": "\033[32m",
        # yellow:
        "WARNING": "\033[33m",
        # red:
        "ERROR": "\033[31m",
        # bold red:
        "CRITICAL": "\033[1;31m",
    }

    def format(self, log_record):
        log_color = self.color_set.get(log_record.levelname, self.color_reset)
        log_msg = super().format(log_record)
        return f"{log_color}{log_msg}{self.color_reset}"


def is_venv() -> bool:
    return sys.prefix != sys.base_prefix


def delegate_to_venv(
    client_dir_path: str,
) -> bool:
    """
    This is a helper function to delegate script execution to a `python` from `venv`.

    It is supposed to be used in FT_75_87_82_46 entry scripts.
    The entry script must know how to compute the path to `client_dir_path`
    (e.g., it must know its path within client dir structure).

    The function fails if `venv` is not created - user must trigger bootstrap manually.

    :return: `False` if already inside `venv`, otherwise start itself inside `venv`.
    """

    if not is_venv():

        venv_python = os.path.join(
            client_dir_path,
            # TODO: This might be passed as arg to the func (that being a default):
            ConfConstEnv.default_dir_rel_path_venv,
            # TODO: This might be passed as arg to the func (that being a default):
            ConfConstGeneral.file_rel_path_venv_python,
        )

        if not os.path.exists(venv_python):
            raise AssertionError(
                f"`{venv_python}` does not exist - has `venv` been bootstrapped?"
            )

        # Throws or never returns:
        os.execv(
            venv_python,
            [
                venv_python,
                *sys.argv,
            ],
        )
    else:
        # Not delegated:
        return False


if __name__ == "__main__":
    main()
