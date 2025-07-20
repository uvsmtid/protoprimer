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

__version__ = "0.0.3"

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
            TargetState.target_run_mode_executed
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
        # TODO: Decide to print choices or not (they look too excessive). Maybe print those in `TargetState` only?
        # choices=[env_state.name for env_state in EnvState],
        # Keep default `None` to indicate there was no user override (and select the actual default conditionally):
        default=None,
        # TODO: Compute universal sink:
        help=f"Select target {EnvState.__name__}.",
    )
    arg_parser.add_argument(
        ArgConst.arg_proto_kernel_abs_file_path,
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
        ArgConst.arg_client_ref_dir_path,
        type=str,
        default=None,
        help="Path to client ref dir (relative to current directory or absolute).",
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
        ArgConst.arg_target_env_dir_rel_path,
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
    proto_kernel_abs_file_path: str | None,
):
    logger.info(
        f"switching from current `python` interpreter [{curr_python_path}][{curr_py_exec.name}] to [{next_python_path}][{next_py_exec.name}] with `{ArgConst.name_proto_kernel_abs_file_path}`[{proto_kernel_abs_file_path}]"
    )
    exec_argv: list[str] = [
        next_python_path,
        *sys.argv,
        ArgConst.arg_py_exec,
        next_py_exec.name,
    ]

    # Once `ArgConst.arg_proto_kernel_abs_file_path` is specified, it is never changed (no need to override):
    if (proto_kernel_abs_file_path is not None) and (
        ArgConst.arg_proto_kernel_abs_file_path not in exec_argv
    ):
        exec_argv.extend(
            [
                ArgConst.arg_proto_kernel_abs_file_path,
                proto_kernel_abs_file_path,
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


def get_path_to_base_python():
    path_to_next_python = os.path.join(
        sys.base_prefix,
        ConfConstGeneral.file_rel_path_venv_python,
    )
    return path_to_next_python


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


def install_editable_project(
    project_abs_path_list: list[str],
):
    """
    Install each of the `project_abs_path_list` (assuming they contain `pyproject.toml`).

    It is equivalent of:
    ```sh
    path/to/python -m pip --editable path/to/project/a --editable path/to/project/b --editable path/to/project/c ...
    ```

    FT_46_37_27_11.editable_install.md
    """

    editable_project_abs_path_list = []
    for project_abs_path in project_abs_path_list:
        editable_project_abs_path_list.append("--editable")
        editable_project_abs_path_list.append(project_abs_path)

    sub_proc_args = [
        get_path_to_curr_python(),
        "-m",
        "pip",
        "install",
        *editable_project_abs_path_list,
    ]

    logger.info(f"installing projects: {' '.join(sub_proc_args)}")

    subprocess.check_call(sub_proc_args)


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

    phase_neo = enum.auto()


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

    # `python` executable has not been categorized yet:
    py_exec_unknown = -1

    # To start `proto_kernel` by any `python`:
    py_exec_arbitrary = 1

    # To run `python` of specific version (to create `venv`):
    py_exec_required = 2

    # To use `venv` (to install packages):
    py_exec_venv = 3

    # After making the latest `protoprimer` effective:
    py_exec_updated_protoprimer_package = 4

    # After making the updated `proto_kernel` effective:
    py_exec_updated_proto_kernel_code = 5

    # TODO: make "proto" clone of client extension effective:
    py_exec_updated_client_package = 6

    def __str__(self):
        return f"{self.name}[{self.value}]"


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
class Bootstrapper_state_stderr_log_level_var(AbstractCachingStateBootstrapper[int]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[],
            env_state=EnvState.state_stderr_log_level_var.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        state_stderr_log_level_var: int = getattr(
            logging,
            os.getenv(
                EnvVarConst.name_PROTOPRIMER_DEFAULT_LOG_LEVEL,
                EnvVarConst.default_PROTOPRIMER_DEFAULT_LOG_LEVEL,
            ),
        )
        return state_stderr_log_level_var


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
                EnvState.state_stderr_log_level_var.name,
            ],
            env_state=EnvState.state_default_stderr_logger_configured.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        # Make all warnings be captured by the logging subsystem:
        logging.captureWarnings(True)

        state_stderr_log_level_var: int = self.bootstrap_parent_state(
            EnvState.state_stderr_log_level_var.name
        )
        assert state_stderr_log_level_var >= 0

        # Log everything (the filters are supposed to be set on output handlers instead):
        logger.setLevel(logging.NOTSET)

        stderr_handler: logging.Handler = logging.StreamHandler(sys.stderr)

        stderr_formatter = CustomFormatter()

        stderr_handler.setLevel(logging.NOTSET)
        stderr_handler.setFormatter(stderr_formatter)

        logger.addHandler(stderr_handler)

        stderr_handler.setLevel(state_stderr_log_level_var)

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
            logger.info(
                f"selecting `default_target`[{self.env_ctx.default_target}] as no `{ArgConst.arg_state_name}` specified"
            )
            state_target_state_name_finalized = self.env_ctx.default_target

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
class Bootstrapper_state_py_exec_arg(
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
            env_state=EnvState.state_py_exec_arg.name,
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
class Bootstrapper_state_proto_kernel_code_file_abs_path_finalized(
    AbstractCachingStateBootstrapper[str]
):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_py_exec_arg.name,
                EnvState.state_args_parsed.name,
            ],
            env_state=EnvState.state_proto_kernel_code_file_abs_path_finalized.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:

        state_py_exec_arg: PythonExecutable = self.bootstrap_parent_state(
            EnvState.state_py_exec_arg.name
        )

        state_proto_kernel_code_file_abs_path_finalized: str
        if state_py_exec_arg.value == PythonExecutable.py_exec_unknown.value:
            state_proto_kernel_code_file_abs_path_finalized = __file__
            if is_venv():
                # UC_90_98_17_93.run_under_venv.md
                # Switch out of the current `venv` (it might be arbitrary one):
                path_to_curr_python = get_path_to_curr_python()
                path_to_next_python = get_path_to_base_python()
                switch_python(
                    curr_py_exec=state_py_exec_arg,
                    curr_python_path=path_to_curr_python,
                    next_py_exec=PythonExecutable.py_exec_arbitrary,
                    next_python_path=path_to_next_python,
                    proto_kernel_abs_file_path=None,
                )
        elif state_py_exec_arg.value >= PythonExecutable.py_exec_venv.value:
            state_args_parsed: argparse.Namespace = self.bootstrap_parent_state(
                EnvState.state_args_parsed.name
            )
            arg_proto_kernel_abs_file_path = getattr(
                state_args_parsed,
                ArgConst.name_proto_kernel_abs_file_path,
            )
            if arg_proto_kernel_abs_file_path is None:
                raise AssertionError(
                    f"`{ArgConst.arg_proto_kernel_abs_file_path}` is not specified at `{EnvState.state_py_exec_arg.name}` [{state_py_exec_arg}]"
                )
            # rely on the path given in args:
            state_proto_kernel_code_file_abs_path_finalized = (
                arg_proto_kernel_abs_file_path
            )
        else:
            assert not is_venv()
            state_proto_kernel_code_file_abs_path_finalized = __file__

        return state_proto_kernel_code_file_abs_path_finalized


# noinspection PyPep8Naming
class Bootstrapper_state_proto_kernel_code_dir_abs_path_finalized(
    AbstractCachingStateBootstrapper[str]
):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_proto_kernel_code_file_abs_path_finalized.name,
            ],
            env_state=EnvState.state_proto_kernel_code_dir_abs_path_finalized.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:

        state_proto_kernel_code_file_abs_path_finalized = self.bootstrap_parent_state(
            EnvState.state_proto_kernel_code_file_abs_path_finalized.name
        )
        state_proto_kernel_code_dir_abs_path_finalized = os.path.dirname(
            state_proto_kernel_code_file_abs_path_finalized
        )

        return state_proto_kernel_code_dir_abs_path_finalized


# noinspection PyPep8Naming
class Bootstrapper_state_proto_kernel_conf_abs_file_path_finalized(
    AbstractCachingStateBootstrapper[str]
):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_proto_kernel_code_dir_abs_path_finalized.name,
            ],
            env_state=EnvState.state_proto_kernel_conf_abs_file_path_finalized.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        state_proto_kernel_code_dir_abs_path_finalized = self.bootstrap_parent_state(
            EnvState.state_proto_kernel_code_dir_abs_path_finalized.name
        )
        return os.path.join(
            state_proto_kernel_code_dir_abs_path_finalized,
            ConfConstInput.default_file_basename_conf_proto,
        )


# noinspection PyPep8Naming
class Bootstrapper_state_client_ref_dir_path_arg(AbstractCachingStateBootstrapper[str]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_args_parsed.name,
                EnvState.state_proto_kernel_conf_abs_file_path_finalized.name,
            ],
            env_state=EnvState.state_client_ref_dir_path_arg.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:

        state_args_parsed: argparse.Namespace = self.bootstrap_parent_state(
            EnvState.state_args_parsed.name
        )

        state_client_ref_dir_path_arg = getattr(
            state_args_parsed,
            ArgConst.name_client_ref_dir_path,
        )

        state_proto_kernel_conf_abs_file_path_finalized = self.bootstrap_parent_state(
            EnvState.state_proto_kernel_conf_abs_file_path_finalized.name
        )

        if not os.path.exists(state_proto_kernel_conf_abs_file_path_finalized):
            if state_client_ref_dir_path_arg is None:
                raise AssertionError(
                    f"Unable to bootstrap [{EnvState.state_client_ref_dir_path_arg.name}]: file [{state_proto_kernel_conf_abs_file_path_finalized}] does not exists and [{ArgConst.arg_client_ref_dir_path}] is not specified."
                )
        return state_client_ref_dir_path_arg


# noinspection PyPep8Naming
class Bootstrapper_state_proto_kernel_conf_file_data(
    AbstractCachingStateBootstrapper[dict]
):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_proto_kernel_conf_abs_file_path_finalized.name,
                EnvState.state_proto_kernel_code_dir_abs_path_finalized.name,
                EnvState.state_client_ref_dir_path_arg.name,
            ],
            env_state=EnvState.state_proto_kernel_conf_file_data.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        state_proto_kernel_conf_abs_file_path_finalized = self.bootstrap_parent_state(
            EnvState.state_proto_kernel_conf_abs_file_path_finalized.name
        )

        file_data: dict
        if os.path.exists(state_proto_kernel_conf_abs_file_path_finalized):
            file_data = read_json_file(state_proto_kernel_conf_abs_file_path_finalized)
        else:
            state_proto_kernel_code_dir_abs_path_finalized = (
                self.bootstrap_parent_state(
                    EnvState.state_proto_kernel_code_dir_abs_path_finalized.name
                )
            )
            state_client_ref_dir_path_arg = self.bootstrap_parent_state(
                EnvState.state_client_ref_dir_path_arg.name
            )
            assert state_client_ref_dir_path_arg is not None

            # Generate file data when missing (first time):
            file_data = {
                # Compute value of the relative path:
                ConfConstPrimer.field_dir_rel_path_root_client: os.path.relpath(
                    state_client_ref_dir_path_arg,
                    state_proto_kernel_code_dir_abs_path_finalized,
                ),
                ConfConstPrimer.field_file_rel_path_conf_client: ConfConstPrimer.default_file_rel_path_conf_client,
            }
            write_json_file(state_proto_kernel_conf_abs_file_path_finalized, file_data)
        return file_data


# noinspection PyPep8Naming
class Bootstrapper_state_client_ref_dir_abs_path_global(
    AbstractCachingStateBootstrapper[str]
):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_proto_kernel_conf_file_data.name,
                EnvState.state_proto_kernel_code_dir_abs_path_finalized.name,
            ],
            env_state=EnvState.state_client_ref_dir_abs_path_global.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        state_proto_kernel_conf_file_data = self.bootstrap_parent_state(
            EnvState.state_proto_kernel_conf_file_data.name
        )

        field_client_dir_rel_path = state_proto_kernel_conf_file_data[
            ConfConstPrimer.field_dir_rel_path_root_client
        ]

        state_proto_kernel_code_dir_abs_path_finalized = self.bootstrap_parent_state(
            EnvState.state_proto_kernel_code_dir_abs_path_finalized.name
        )

        state_client_ref_dir_abs_path_global = os.path.join(
            state_proto_kernel_code_dir_abs_path_finalized,
            field_client_dir_rel_path,
        )

        return os.path.normpath(state_client_ref_dir_abs_path_global)


# noinspection PyPep8Naming
class Bootstrapper_state_target_env_dir_rel_path_finalized(
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
                EnvState.state_client_conf_file_data.name,
            ],
            env_state=EnvState.state_target_env_dir_rel_path_finalized.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        state_target_env_dir_rel_path_finalized = getattr(
            self.bootstrap_parent_state(EnvState.state_args_parsed.name),
            ArgConst.name_target_env_dir_rel_path,
        )
        if state_target_env_dir_rel_path_finalized is None:
            state_client_conf_file_data: dict = self.bootstrap_parent_state(
                EnvState.state_client_conf_file_data.name
            )
            state_target_env_dir_rel_path_finalized = state_client_conf_file_data.get(
                ConfConstClient.field_dir_rel_path_conf_env_default_target,
            )
        return state_target_env_dir_rel_path_finalized


# noinspection PyPep8Naming
class Bootstrapper_state_client_conf_file_abs_path_global(
    AbstractCachingStateBootstrapper[str]
):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_client_ref_dir_abs_path_global.name,
                EnvState.state_proto_kernel_conf_file_data.name,
            ],
            env_state=EnvState.state_client_conf_file_abs_path_global.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        state_client_ref_dir_abs_path_global = self.bootstrap_parent_state(
            EnvState.state_client_ref_dir_abs_path_global.name
        )

        state_proto_kernel_conf_file_data = self.bootstrap_parent_state(
            EnvState.state_proto_kernel_conf_file_data.name
        )

        field_client_config_rel_path = state_proto_kernel_conf_file_data[
            ConfConstPrimer.field_file_rel_path_conf_client
        ]

        return os.path.join(
            state_client_ref_dir_abs_path_global,
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
                EnvState.state_client_conf_file_abs_path_global.name,
            ],
            env_state=EnvState.state_client_conf_file_data.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:

        state_client_conf_file_abs_path_global = self.bootstrap_parent_state(
            EnvState.state_client_conf_file_abs_path_global.name
        )
        if os.path.exists(state_client_conf_file_abs_path_global):
            return read_json_file(state_client_conf_file_abs_path_global)
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
                os.path.dirname(state_client_conf_file_abs_path_global),
                exist_ok=True,
            )
            write_json_file(state_client_conf_file_abs_path_global, file_data)
            return file_data


# noinspection PyPep8Naming
class Bootstrapper_state_env_conf_dir_abs_path_local(
    AbstractCachingStateBootstrapper[str]
):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_client_ref_dir_abs_path_global.name,
                EnvState.state_client_conf_file_data.name,
            ],
            env_state=EnvState.state_env_conf_dir_abs_path_local.name,
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
        state_env_conf_dir_abs_path_local = os.path.join(
            self.bootstrap_parent_state(
                EnvState.state_client_ref_dir_abs_path_global.name
            ),
            env_conf_dir_rel_path,
        )

        return state_env_conf_dir_abs_path_local


# noinspection PyPep8Naming
class Bootstrapper_state_target_env_dir_rel_path_verified(
    AbstractCachingStateBootstrapper[bool]
):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_target_env_dir_rel_path_finalized.name,
            ],
            env_state=EnvState.state_target_env_dir_rel_path_verified.name,
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

        state_target_env_dir_rel_path_finalized = self.bootstrap_parent_state(
            EnvState.state_target_env_dir_rel_path_finalized.name
        )
        if os.path.isabs(state_target_env_dir_rel_path_finalized):
            raise AssertionError(
                f"Target for `@/conf/` symlink [{state_target_env_dir_rel_path_finalized}] must not be absolute path."
            )
        elif ".." in pathlib.Path(state_target_env_dir_rel_path_finalized).parts:
            raise AssertionError(
                f"Target for `@/conf/` symlink [{state_target_env_dir_rel_path_finalized}] must not contain `..` path segments."
            )
        elif not os.path.isdir(state_target_env_dir_rel_path_finalized):
            raise AssertionError(
                f"Target for `@/conf/` symlink [{state_target_env_dir_rel_path_finalized}] must lead to a directory."
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
                EnvState.state_target_env_dir_rel_path_finalized.name,
                EnvState.state_target_env_dir_rel_path_verified.name,
                EnvState.state_env_conf_dir_abs_path_local.name,
            ],
            env_state=EnvState.state_env_conf_dir_path_verified.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        state_env_conf_dir_abs_path_local = self.bootstrap_parent_state(
            EnvState.state_env_conf_dir_abs_path_local.name
        )
        state_target_env_dir_rel_path_finalized = self.bootstrap_parent_state(
            EnvState.state_target_env_dir_rel_path_finalized.name
        )
        if os.path.exists(state_env_conf_dir_abs_path_local):
            if os.path.islink(state_env_conf_dir_abs_path_local):
                if os.path.isdir(state_env_conf_dir_abs_path_local):
                    if state_target_env_dir_rel_path_finalized is None:
                        pass
                    else:
                        conf_dir_path = os.readlink(state_env_conf_dir_abs_path_local)
                        if os.path.normpath(
                            state_target_env_dir_rel_path_finalized
                        ) == os.path.normpath(conf_dir_path):
                            pass
                        else:
                            raise AssertionError(
                                f"The `@/conf/` target [{conf_dir_path}] is not the same as the provided target [{state_target_env_dir_rel_path_finalized}]."
                            )
                else:
                    raise AssertionError(
                        f"The `@/conf/` [{state_env_conf_dir_abs_path_local}] target is not a directory.",
                    )
            else:
                raise AssertionError(
                    f"The `@/conf/` [{state_env_conf_dir_abs_path_local}] is not a symlink.",
                )
        else:
            if state_target_env_dir_rel_path_finalized is None:
                raise AssertionError(
                    f"The `@/conf/` dir does not exists and `{ArgConst.name_target_env_dir_rel_path}` is not provided - see `--help`.",
                )
            else:
                state_target_env_dir_rel_path_verified = self.bootstrap_parent_state(
                    EnvState.state_target_env_dir_rel_path_verified.name
                )
                assert state_target_env_dir_rel_path_verified

                os.symlink(
                    os.path.normpath(state_target_env_dir_rel_path_finalized),
                    state_env_conf_dir_abs_path_local,
                )

        return True


# noinspection PyPep8Naming
class Bootstrapper_state_env_conf_file_path_local(
    AbstractCachingStateBootstrapper[str]
):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_client_ref_dir_abs_path_global.name,
                EnvState.state_env_conf_dir_abs_path_local.name,
                EnvState.state_env_conf_dir_path_verified.name,
            ],
            env_state=EnvState.state_env_conf_file_path_local.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        state_env_conf_dir_path_verified = self.bootstrap_parent_state(
            EnvState.state_env_conf_dir_path_verified.name
        )
        assert state_env_conf_dir_path_verified

        state_client_ref_dir_abs_path_global = self.bootstrap_parent_state(
            EnvState.state_client_ref_dir_abs_path_global.name
        )
        state_env_conf_file_path_local = os.path.join(
            state_client_ref_dir_abs_path_global,
            ConfConstClient.default_dir_rel_path_conf_env_link_name,
            # TODO: Do not use default values directly - resolve it differently at the prev|next step based on the need:
            ConfConstClient.default_file_basename_conf_env,
        )
        state_env_conf_dir_abs_path_local = self.bootstrap_parent_state(
            EnvState.state_env_conf_dir_abs_path_local.name
        )
        # TODO: Ensure the path is under with proper error message:
        assert is_sub_path(
            state_env_conf_file_path_local,
            state_env_conf_dir_abs_path_local,
        )
        return state_env_conf_file_path_local


# noinspection PyPep8Naming
class Bootstrapper_state_env_conf_file_data(AbstractCachingStateBootstrapper[dict]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_env_conf_file_path_local.name,
            ],
            env_state=EnvState.state_env_conf_file_data.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        state_env_conf_file_path_local = self.bootstrap_parent_state(
            EnvState.state_env_conf_file_path_local.name
        )
        file_data: dict
        if os.path.exists(state_env_conf_file_path_local):
            file_data = read_json_file(state_env_conf_file_path_local)
        else:
            file_data = {
                # TODO: Do not use default values directly - resolve it differently at the prev|next step based on the need:
                ConfConstEnv.field_file_abs_path_python: ConfConstEnv.default_file_abs_path_python,
                # TODO: Do not use default values directly - resolve it differently at the prev|next step based on the need:
                ConfConstEnv.field_dir_rel_path_venv: ConfConstEnv.default_dir_rel_path_venv,
            }
            # TODO: This creates a directory with `ConfConstClient.default_dir_rel_path_conf_env_link_name` instead of symlink.
            #       But this happens only if dependency
            #       `state_env_conf_file_path_local` -> `state_env_conf_dir_path_verified`
            #       was not executed (which is not possible outside of tests).
            write_json_file(state_env_conf_file_path_local, file_data)
        return file_data


# noinspection PyPep8Naming
class Bootstrapper_state_local_python_file_abs_path_finalized(
    AbstractCachingStateBootstrapper[str]
):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_env_conf_file_data.name,
                EnvState.state_client_ref_dir_abs_path_global.name,
            ],
            env_state=EnvState.state_local_python_file_abs_path_finalized.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        state_env_conf_file_data: dict = self.bootstrap_parent_state(
            EnvState.state_env_conf_file_data.name
        )

        state_local_python_file_abs_path_finalized = state_env_conf_file_data.get(
            ConfConstEnv.field_file_abs_path_python,
            # TODO: Do not use default values directly - resolve it differently at the prev|next step based on the need:
            ConfConstEnv.default_file_abs_path_python,
        )

        if not os.path.isabs(state_local_python_file_abs_path_finalized):
            # TODO: Really? Do we really want to allow specifying `python` using rel path?
            #       Regardless, even if rel path, the `field_file_abs_path_python` should remove `abs` from the name then.
            state_local_python_file_abs_path_finalized = os.path.join(
                self.bootstrap_parent_state(
                    EnvState.state_client_ref_dir_abs_path_global.name
                ),
                state_local_python_file_abs_path_finalized,
            )

        return state_local_python_file_abs_path_finalized


# noinspection PyPep8Naming
class Bootstrapper_state_local_venv_dir_path_finalized(
    AbstractCachingStateBootstrapper[str]
):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_env_conf_file_data.name,
                EnvState.state_client_ref_dir_abs_path_global.name,
            ],
            env_state=EnvState.state_local_venv_dir_path_finalized.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        state_env_conf_file_data: dict = self.bootstrap_parent_state(
            EnvState.state_env_conf_file_data.name
        )

        state_local_venv_dir_path_finalized = state_env_conf_file_data.get(
            ConfConstEnv.field_dir_rel_path_venv,
            # TODO: Do not use default values directly - resolve it differently at the prev|next step based on the need:
            ConfConstEnv.default_dir_rel_path_venv,
        )

        if not os.path.isabs(state_local_venv_dir_path_finalized):
            state_client_ref_dir_abs_path_global = self.bootstrap_parent_state(
                EnvState.state_client_ref_dir_abs_path_global.name
            )
            state_local_venv_dir_path_finalized = os.path.join(
                state_client_ref_dir_abs_path_global,
                state_local_venv_dir_path_finalized,
            )

        return state_local_venv_dir_path_finalized


# noinspection PyPep8Naming
class Bootstrapper_state_project_path_list_finalized(
    AbstractCachingStateBootstrapper[list]
):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_env_conf_file_data.name,
            ],
            env_state=EnvState.state_project_path_list_finalized.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        state_env_conf_file_data: dict = self.bootstrap_parent_state(
            EnvState.state_env_conf_file_data.name
        )

        project_rel_path_list: list[str] = state_env_conf_file_data.get(
            ConfConstEnv.field_project_rel_path_list,
            ConfConstEnv.default_project_rel_path_list,
        )

        return project_rel_path_list


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
                EnvState.state_py_exec_arg.name,
                EnvState.state_local_python_file_abs_path_finalized.name,
                EnvState.state_local_venv_dir_path_finalized.name,
                EnvState.state_env_conf_file_path_local.name,
                EnvState.state_proto_kernel_code_file_abs_path_finalized.name,
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

        state_py_exec_arg: PythonExecutable = self.bootstrap_parent_state(
            EnvState.state_py_exec_arg.name
        )

        state_proto_kernel_code_file_abs_path_finalized: str = (
            self.bootstrap_parent_state(
                EnvState.state_proto_kernel_code_file_abs_path_finalized.name
            )
        )

        state_local_python_file_abs_path_finalized = self.bootstrap_parent_state(
            EnvState.state_local_python_file_abs_path_finalized.name
        )
        state_local_venv_dir_path_finalized = self.bootstrap_parent_state(
            EnvState.state_local_venv_dir_path_finalized.name
        )

        # TODO: Make it separate validation state
        #       (not a dependency of this because, technically, we do not know where `EnvState.state_local_python_file_abs_path_finalized` and `EnvState.state_local_venv_dir_path_finalized` came from):
        if is_sub_path(
            state_local_python_file_abs_path_finalized,
            state_local_venv_dir_path_finalized,
        ):
            state_env_conf_file_path_local = self.bootstrap_parent_state(
                EnvState.state_env_conf_file_path_local.name
            )
            raise AssertionError(
                f"The [{state_local_python_file_abs_path_finalized}] is a sub-path of the [{state_local_venv_dir_path_finalized}]. "
                f"This is not allowed because `path_to_python` is used to init `venv` and cannot rely on `venv` existance. "
                f"Specify different `{EnvState.state_local_python_file_abs_path_finalized.name}` (e.g. `/usr/bin/python3`). "
                # TODO: compute path for `proto_kernel.py`
                f"Alternatively, remove [{state_env_conf_file_path_local}] and re-run `@/cmd/proto_kernel.py` "
                f"to re-create it automatically. "
            )

        venv_path_to_python = os.path.join(
            state_local_venv_dir_path_finalized,
            ConfConstGeneral.file_rel_path_venv_python,
        )
        path_to_curr_python = get_path_to_curr_python()
        logger.debug(f"path_to_curr_python: {path_to_curr_python}")
        if is_sub_path(path_to_curr_python, state_local_venv_dir_path_finalized):
            if path_to_curr_python != venv_path_to_python:
                assert state_py_exec_arg == PythonExecutable.py_exec_unknown
                state_py_exec_selected = PythonExecutable.py_exec_arbitrary
                # Ensure `python` is from the correct `venv` path
                switch_python(
                    curr_py_exec=state_py_exec_arg,
                    curr_python_path=path_to_curr_python,
                    next_py_exec=PythonExecutable.py_exec_required,
                    next_python_path=state_local_python_file_abs_path_finalized,
                    proto_kernel_abs_file_path=state_proto_kernel_code_file_abs_path_finalized,
                )
            else:
                # If already under `venv` with the expected path, nothing to do.
                assert (
                    state_py_exec_arg == PythonExecutable.py_exec_unknown
                    or state_py_exec_arg >= PythonExecutable.py_exec_venv
                )
                # Successfully reached end goal:
                if state_py_exec_arg == PythonExecutable.py_exec_unknown:
                    state_py_exec_selected = PythonExecutable.py_exec_venv
                else:
                    state_py_exec_selected = state_py_exec_arg
        else:
            if path_to_curr_python != state_local_python_file_abs_path_finalized:
                assert state_py_exec_arg == PythonExecutable.py_exec_unknown
                state_py_exec_selected = PythonExecutable.py_exec_arbitrary
                switch_python(
                    curr_py_exec=state_py_exec_arg,
                    curr_python_path=path_to_curr_python,
                    next_py_exec=PythonExecutable.py_exec_required,
                    next_python_path=state_local_python_file_abs_path_finalized,
                    proto_kernel_abs_file_path=state_proto_kernel_code_file_abs_path_finalized,
                )
            else:
                assert state_py_exec_arg <= PythonExecutable.py_exec_required
                state_py_exec_selected = PythonExecutable.py_exec_required
                if not os.path.exists(state_local_venv_dir_path_finalized):
                    logger.info(
                        f"creating `venv` [{state_local_venv_dir_path_finalized}]"
                    )
                    venv.create(
                        state_local_venv_dir_path_finalized,
                        with_pip=True,
                    )
                else:
                    logger.info(
                        f"reusing existing `venv` [{state_local_venv_dir_path_finalized}]"
                    )
                switch_python(
                    curr_py_exec=state_py_exec_arg,
                    curr_python_path=state_local_python_file_abs_path_finalized,
                    next_py_exec=PythonExecutable.py_exec_venv,
                    next_python_path=venv_path_to_python,
                    proto_kernel_abs_file_path=state_proto_kernel_code_file_abs_path_finalized,
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
                EnvState.state_client_ref_dir_abs_path_global.name,
                EnvState.state_project_path_list_finalized.name,
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

        state_client_ref_dir_abs_path_global: str = self.bootstrap_parent_state(
            EnvState.state_client_ref_dir_abs_path_global.name
        )

        state_project_path_list_finalized: list[str] = self.bootstrap_parent_state(
            EnvState.state_project_path_list_finalized.name
        )

        if state_py_exec_selected == PythonExecutable.py_exec_venv:

            if len(state_project_path_list_finalized) == 0:
                logger.warning("project path list is empty - nothing to install")
                return True

            project_abs_path_list = []
            for project_rel_path in state_project_path_list_finalized:
                # FT_46_37_27_11.editable_install.md

                project_abs_path = os.path.join(
                    state_client_ref_dir_abs_path_global,
                    project_rel_path,
                )
                assert os.path.isfile(os.path.join(project_abs_path, "pyproject.toml"))

                project_abs_path_list.append(project_abs_path)

            install_editable_project(
                project_abs_path_list,
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
                EnvState.state_py_exec_arg.name,
                EnvState.state_proto_kernel_code_file_abs_path_finalized.name,
                EnvState.state_protoprimer_package_installed.name,
            ],
            env_state=EnvState.state_py_exec_updated_protoprimer_package_reached.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:

        state_py_exec_updated_protoprimer_package_reached: PythonExecutable

        state_py_exec_arg: PythonExecutable = self.bootstrap_parent_state(
            EnvState.state_py_exec_arg.name
        )

        state_proto_kernel_code_file_abs_path_finalized: str = (
            self.bootstrap_parent_state(
                EnvState.state_proto_kernel_code_file_abs_path_finalized.name
            )
        )

        state_protoprimer_package_installed: bool = self.bootstrap_parent_state(
            EnvState.state_protoprimer_package_installed.name
        )
        assert state_protoprimer_package_installed

        if (
            state_py_exec_arg.value
            < PythonExecutable.py_exec_updated_protoprimer_package.value
        ):
            venv_path_to_python = get_path_to_curr_python()

            state_py_exec_updated_protoprimer_package_reached = (
                PythonExecutable.py_exec_updated_protoprimer_package
            )
            # TODO: maybe add this reason to `switch_python` as an arg?
            logger.debug(
                f"restarting current `python` interpreter [{venv_path_to_python}] to make [{EnvState.state_protoprimer_package_installed.name}] effective"
            )
            switch_python(
                curr_py_exec=state_py_exec_arg,
                curr_python_path=venv_path_to_python,
                next_py_exec=PythonExecutable.py_exec_updated_protoprimer_package,
                next_python_path=venv_path_to_python,
                proto_kernel_abs_file_path=state_proto_kernel_code_file_abs_path_finalized,
            )
        else:
            # Successfully reached end goal:
            state_py_exec_updated_protoprimer_package_reached = state_py_exec_arg

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
                EnvState.state_proto_kernel_code_file_abs_path_finalized.name,
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

        state_proto_kernel_code_file_abs_path_finalized = self.bootstrap_parent_state(
            EnvState.state_proto_kernel_code_file_abs_path_finalized.name
        )
        assert os.path.isabs(state_proto_kernel_code_file_abs_path_finalized)
        assert not os.path.islink(state_proto_kernel_code_file_abs_path_finalized)
        assert os.path.isfile(state_proto_kernel_code_file_abs_path_finalized)

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
            f"writing `primer_kernel_abs_path` [{primer_kernel_abs_path}] over `state_proto_kernel_code_file_abs_path_finalized` [{state_proto_kernel_code_file_abs_path_finalized}]"
        )
        write_text_file(
            file_path=state_proto_kernel_code_file_abs_path_finalized,
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
                EnvState.state_py_exec_arg.name,
                EnvState.state_proto_kernel_updated.name,
                EnvState.state_proto_kernel_code_file_abs_path_finalized.name,
            ],
            env_state=EnvState.state_py_exec_updated_proto_kernel_code.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:

        state_py_exec_updated_proto_kernel_code: PythonExecutable

        state_py_exec_arg: PythonExecutable = self.bootstrap_parent_state(
            EnvState.state_py_exec_arg.name
        )

        state_proto_kernel_code_file_abs_path_finalized: str = (
            self.bootstrap_parent_state(
                EnvState.state_proto_kernel_code_file_abs_path_finalized.name
            )
        )

        state_proto_kernel_updated: bool = self.bootstrap_parent_state(
            EnvState.state_proto_kernel_updated.name
        )
        assert state_proto_kernel_updated

        venv_path_to_python = get_path_to_curr_python()

        if (
            state_py_exec_arg.value
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
                curr_py_exec=state_py_exec_arg,
                curr_python_path=venv_path_to_python,
                next_py_exec=PythonExecutable.py_exec_updated_proto_kernel_code,
                next_python_path=venv_path_to_python,
                proto_kernel_abs_file_path=state_proto_kernel_code_file_abs_path_finalized,
            )
        else:
            # Successfully reached end goal:
            state_py_exec_updated_proto_kernel_code = state_py_exec_arg

        return state_py_exec_updated_proto_kernel_code


class EnvState(enum.Enum):
    """
    Environment states to be reached during the bootstrap process.

    NOTE: Only `str` names of the enum items are supposed to be used (any value is ignored).
    The value of `AbstractCachingStateBootstrapper` assigned is the default implementation for the state,
    and the only reason it is assigned is purely for the quick navigation across the source code in the IDE.

    FT_68_54_41_96.state_dependency.md
    """

    def __init__(
        self,
        # Default implementation (for reference):
        default_impl,
    ):
        self.default_impl = default_impl

    state_stderr_log_level_var = Bootstrapper_state_stderr_log_level_var

    state_default_stderr_logger_configured = (
        Bootstrapper_state_default_stderr_logger_configured
    )

    state_args_parsed = Bootstrapper_state_args_parsed

    state_stderr_log_level_finalized = Bootstrapper_state_stderr_log_level_finalized

    state_run_mode_finalized = Bootstrapper_state_run_mode_finalized

    state_target_state_name_finalized = Bootstrapper_state_target_state_name_finalized

    # Special case: triggers everything:
    state_run_mode_executed = Bootstrapper_state_run_mode_executed

    state_py_exec_arg = Bootstrapper_state_py_exec_arg

    state_proto_kernel_code_file_abs_path_finalized = (
        Bootstrapper_state_proto_kernel_code_file_abs_path_finalized
    )

    # TODO: rename to `proto_kernel_abs_dir_path`:
    state_proto_kernel_code_dir_abs_path_finalized = (
        Bootstrapper_state_proto_kernel_code_dir_abs_path_finalized
    )

    state_proto_kernel_conf_abs_file_path_finalized = (
        Bootstrapper_state_proto_kernel_conf_abs_file_path_finalized
    )

    state_client_ref_dir_path_arg = Bootstrapper_state_client_ref_dir_path_arg

    state_proto_kernel_conf_file_data = Bootstrapper_state_proto_kernel_conf_file_data

    # TODO: Rename to `ref_dir_path_configured`:
    state_client_ref_dir_abs_path_global = (
        Bootstrapper_state_client_ref_dir_abs_path_global
    )

    # TODO:
    # state_cli_log_level

    state_client_conf_file_abs_path_global = (
        Bootstrapper_state_client_conf_file_abs_path_global
    )

    state_client_conf_file_data = Bootstrapper_state_client_conf_file_data

    # TODO:
    # state_client_log_level

    # TODO:
    # state_client_path_to_python

    # TODO:
    # state_client_path_to_venv

    state_env_conf_dir_abs_path_local = Bootstrapper_state_env_conf_dir_abs_path_local

    # TODO: rename in relation to `ArgConst.arg_target_env_dir_rel_path`
    state_target_env_dir_rel_path_finalized = (
        Bootstrapper_state_target_env_dir_rel_path_finalized
    )

    state_target_env_dir_rel_path_verified = (
        Bootstrapper_state_target_env_dir_rel_path_verified
    )

    state_env_conf_dir_path_verified = Bootstrapper_state_env_conf_dir_path_verified

    state_env_conf_file_path_local = Bootstrapper_state_env_conf_file_path_local

    state_env_conf_file_data = Bootstrapper_state_env_conf_file_data

    # TODO:
    # state_env_log_level

    state_local_python_file_abs_path_finalized = (
        Bootstrapper_state_local_python_file_abs_path_finalized
    )

    state_local_venv_dir_path_finalized = (
        Bootstrapper_state_local_venv_dir_path_finalized
    )

    state_project_path_list_finalized = Bootstrapper_state_project_path_list_finalized

    # TODO: rename to `py_exec_venv_reached`:
    state_py_exec_selected = Bootstrapper_state_py_exec_selected

    # TODO: rename to "client" (or "ref"?): `client_project_list_installed`:
    state_protoprimer_package_installed = (
        Bootstrapper_state_protoprimer_package_installed
    )

    # TODO: rename - "reached" sounds weird (and makes no sense):
    state_py_exec_updated_protoprimer_package_reached = (
        Bootstrapper_state_py_exec_updated_protoprimer_package_reached
    )

    # TODO: rename according to the final name:
    state_proto_kernel_updated = Bootstrapper_state_proto_kernel_updated

    state_py_exec_updated_proto_kernel_code = (
        Bootstrapper_state_py_exec_updated_proto_kernel_code
    )


class TargetState:
    """
    Special `EnvState`-s.
    """

    target_full_proto_bootstrap: str = (
        EnvState.state_py_exec_updated_proto_kernel_code.name
    )

    target_run_mode_executed: str = EnvState.state_run_mode_executed.name

    target_stderr_log_handler: str = (
        EnvState.state_default_stderr_logger_configured.name
    )


class EnvVarConst:
    """
    See FT_08_92_69_92.env_var.md
    """

    name_PATH: str = "PATH"

    name_PROTOPRIMER_DEFAULT_LOG_LEVEL: str = "PROTOPRIMER_DEFAULT_LOG_LEVEL"

    default_PROTOPRIMER_DEFAULT_LOG_LEVEL: str = "INFO"


class ArgConst:

    name_proto_kernel_abs_file_path = "proto_kernel_abs_file_path"
    name_target_env_dir_rel_path = "target_env_dir_rel_path"
    name_client_ref_dir_path = "client_ref_dir_path"
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

    arg_proto_kernel_abs_file_path = f"--{name_proto_kernel_abs_file_path}"
    arg_target_env_dir_rel_path = f"--{name_target_env_dir_rel_path}"
    arg_client_ref_dir_path = f"--{name_client_ref_dir_path}"
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

    file_rel_path_venv_bin = os.path.join(
        "bin",
    )

    file_rel_path_venv_python = os.path.join(
        file_rel_path_venv_bin,
        "python",
    )

    file_rel_path_venv_activate = os.path.join(
        file_rel_path_venv_bin,
        "activate",
    )

    # TODO: rename according to the final name:
    func_get_proto_kernel_generated_boilerplate = lambda module_obj: (
        f"""
################################################################################
# Generated content:
# This is a (proto) copy of `{module_obj.__name__}` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
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

    field_project_rel_path_list = "project_rel_path_list"

    # TODO: This may not work everywhere:
    default_file_abs_path_python = "/usr/bin/python"

    default_dir_rel_path_venv = "venv"

    default_project_rel_path_list = []


class EnvContext:

    def __init__(
        self,
    ):

        self.state_bootstrappers: dict[str, AbstractStateBootstrapper] = {}
        self.dependency_edges: list[tuple[str, str]] = []

        self.register_bootstrapper(Bootstrapper_state_stderr_log_level_var(self))
        self.register_bootstrapper(
            Bootstrapper_state_default_stderr_logger_configured(self)
        )
        self.register_bootstrapper(Bootstrapper_state_args_parsed(self))
        self.register_bootstrapper(Bootstrapper_state_stderr_log_level_finalized(self))
        self.register_bootstrapper(Bootstrapper_state_run_mode_finalized(self))
        self.register_bootstrapper(Bootstrapper_state_target_state_name_finalized(self))
        self.register_bootstrapper(Bootstrapper_state_run_mode_executed(self))
        self.register_bootstrapper(Bootstrapper_state_py_exec_arg(self))
        self.register_bootstrapper(
            Bootstrapper_state_proto_kernel_code_file_abs_path_finalized(self)
        )
        self.register_bootstrapper(
            Bootstrapper_state_proto_kernel_code_dir_abs_path_finalized(self)
        )
        self.register_bootstrapper(
            Bootstrapper_state_proto_kernel_conf_abs_file_path_finalized(self)
        )
        self.register_bootstrapper(Bootstrapper_state_client_ref_dir_path_arg(self))
        self.register_bootstrapper(Bootstrapper_state_proto_kernel_conf_file_data(self))
        self.register_bootstrapper(
            Bootstrapper_state_client_ref_dir_abs_path_global(self)
        )
        self.register_bootstrapper(
            Bootstrapper_state_target_env_dir_rel_path_finalized(self)
        )
        self.register_bootstrapper(
            Bootstrapper_state_client_conf_file_abs_path_global(self)
        )
        self.register_bootstrapper(Bootstrapper_state_client_conf_file_data(self))
        self.register_bootstrapper(Bootstrapper_state_env_conf_dir_abs_path_local(self))
        self.register_bootstrapper(
            Bootstrapper_state_target_env_dir_rel_path_verified(self)
        )
        self.register_bootstrapper(Bootstrapper_state_env_conf_dir_path_verified(self))
        self.register_bootstrapper(Bootstrapper_state_env_conf_file_path_local(self))
        self.register_bootstrapper(Bootstrapper_state_env_conf_file_data(self))
        self.register_bootstrapper(
            Bootstrapper_state_local_python_file_abs_path_finalized(self)
        )
        self.register_bootstrapper(
            Bootstrapper_state_local_venv_dir_path_finalized(self)
        )
        self.register_bootstrapper(Bootstrapper_state_project_path_list_finalized(self))
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

        self.populate_dependencies()

        # TODO: Do not set it on Context - use bootstrap-able values:
        # TODO: Find "Universal Sink":
        self.default_target: str = TargetState.target_full_proto_bootstrap

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
    client_ref_dir_path: str,
) -> bool:
    """
    This is a helper function to delegate script execution to a `python` from `venv`.

    It is supposed to be used in FT_75_87_82_46 entry scripts.
    The entry script must know how to compute the path to `client_ref_dir_path`
    (e.g., it must know its path within client dir structure).

    The function fails if `venv` is not created - user must trigger bootstrap manually.

    :return: `False` if already inside `venv`, otherwise start itself inside `venv`.
    """

    if not is_venv():

        venv_bin = os.path.join(
            client_ref_dir_path,
            # TODO: This might be passed as arg to the func (that being a default):
            ConfConstEnv.default_dir_rel_path_venv,
            ConfConstGeneral.file_rel_path_venv_bin,
        )
        venv_python = os.path.join(
            client_ref_dir_path,
            # TODO: This might be passed as arg to the func (that being a default):
            ConfConstEnv.default_dir_rel_path_venv,
            ConfConstGeneral.file_rel_path_venv_python,
        )

        if not os.path.exists(venv_python):
            raise AssertionError(
                f"`{venv_python}` does not exist - has `venv` been bootstrapped?"
            )

        # Equivalent of `./venv/bin/activate` to configure `PATH` env var:
        os.environ[EnvVarConst.name_PATH] = (
            venv_bin + os.pathsep + os.environ.get(EnvVarConst.name_PATH, "")
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
