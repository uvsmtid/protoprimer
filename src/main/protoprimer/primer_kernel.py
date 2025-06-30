#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Alexey Pakseykin
# See: https://github.com/uvsmtid/protoprimer
"""

NOTE: The script must be run with Python 3.
      Ensure that `python3` is in `PATH` for shebang to work.
      Alternatively, run under specific `python` interpreter.

See more:
*   FS_28_84_41_40: flexible bootstrap

Typical usage:
    ./exe/bootstrap_env.py

To initialize the env with specific Python version:
    /path/to/pythonX ./exe/bootstrap_env.py

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
__version__ = "0.0.1"

from typing import (
    Any,
    Generic,
    TypeVar,
)

logger = logging.getLogger()

StateValueType = TypeVar("StateValueType")


def main(configure_env_context=None):

    ensure_min_python_version()

    if configure_env_context is None:
        env_ctx = EnvContext()
    else:
        env_ctx = configure_env_context()

    try:
        # TODO: make it one of the bootstrap steps?
        env_ctx.configure_logger()

        env_ctx.run_stages()
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

    # FS_84_11_73_28: supported python versions:
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

    arg_parser.add_argument(
        # TODO: put in ArgConst:
        "--context_phase",
        type=str,
        choices=[context_phase.name for context_phase in ContextPhase],
        default=ContextPhase.proto_primer.name,
        help=f"Select `{ContextPhase.__name__}`.",
    )
    arg_parser.add_argument(
        "-s",
        # TODO: put in ArgConst:
        "--silent",
        action="store_true",
        dest="log_level_silent",
        # In the case of exceptions, stack traces are still printed:
        help="Do not log, use non-zero exit code on error.",
    )
    arg_parser.add_argument(
        "-q",
        # TODO: put in ArgConst:
        "--quiet",
        action="store_true",
        dest="log_level_quiet",
        help="Log errors messages only.",
    )
    arg_parser.add_argument(
        "-v",
        # TODO: put in ArgConst:
        "--verbose",
        action="count",
        dest="log_level_verbose",
        default=0,
        help="Log debug messages.",
    )
    arg_parser.add_argument(
        # TODO: put in ArgConst:
        "--run_mode",
        type=str,
        choices=[run_mode.name for run_mode in RunMode],
        default=RunMode.bootstrap_env.name,
        help="Select run mode.",
    )
    arg_parser.add_argument(
        # TODO: put in ArgConst:
        "--state_name",
        type=str,
        default=None,
        # TODO: Compute universal sink:
        help="Select state name to start with (default = universal sink).",
    )
    # TODO: use it with special `--init_repo` flag (otherwise, do not allow):
    arg_parser.add_argument(
        ArgConst.arg_client_dir_path,
        nargs="?",
        default=None,
        help="Path to client root dir (relative to current directory or absolute).",
    )
    arg_parser.add_argument(
        ArgConst.arg_py_exec,
        type=str,
        choices=[py_exec.name for py_exec in PythonExecutable],
        default=PythonExecutable.py_exec_unknown.name,
        help="Used internally: category of `python` executable detected by recursive invocation.",
    )
    # TODO: use it with special `--init_repo` flag (otherwise, do not allow):
    # TODO: use positional arg for that:
    arg_parser.add_argument(
        # TODO: put in ArgConst:
        "target_dst_dir_path",
        nargs="?",
        default=None,
        help="Path to one of the dirs (normally under `@/dst/`) to be used as target for `@/conf/` symlink.",
    )
    return arg_parser


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

    return "\n".join(output_text) + "\n"


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

    extras_spec = ",".join(extras_list)
    package_spec = f"{package_path}[{extras_spec}]"
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


class ContextPhase(enum.Enum):
    # TODO: select final name: *Phase *Type?

    # TODO: select final names:
    #       proto vs neo
    #       pre_venv vs post_venv
    #       immature vs mature
    #       primitive vs evolved

    proto_primer = enum.auto()

    client_primer = enum.auto()


class RunMode(enum.Enum):
    """
    Various modes the script can be run in.
    """

    print_dag = enum.auto()

    bootstrap_env = enum.auto()


class AbstractBootstrapperVisitor:
    """
    Visitor pattern to work with bootstrappers.
    """

    def visit_bootstrapper(
        self,
        state_bootstrapper: AbstractStateBootstrapper,
    ) -> None:
        raise NotImplementedError()


class SinkPrinterVisitor(AbstractBootstrapperVisitor):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__()
        self.env_ctx: EnvContext = env_ctx
        self.bootstrapper_usage_count: dict[str, int] = {}

    def visit_bootstrapper(
        self,
        state_bootstrapper: AbstractStateBootstrapper,
    ) -> None:
        self.count_usage(
            state_bootstrapper,
        )
        self.print_bootstrapper_parents(
            state_bootstrapper,
            level=0,
        )

    def count_usage(
        self,
        state_bootstrapper,
    ) -> None:
        self.bootstrapper_usage_count.setdefault(
            state_bootstrapper.get_env_state().name,
            0,
        )
        self.bootstrapper_usage_count[state_bootstrapper.get_env_state().name] += 1
        for state_parent in state_bootstrapper.get_state_parents():
            self.count_usage(
                self.env_ctx.state_bootstrappers[state_parent],
            )

    def print_bootstrapper_parents(
        self,
        state_bootstrapper,
        level: int,
    ) -> None:
        print(
            f"{' ' * level}{state_bootstrapper.get_env_state().name} x {self.bootstrapper_usage_count[state_bootstrapper.get_env_state().name]}"
        )
        for state_parent in state_bootstrapper.get_state_parents():
            self.print_bootstrapper_parents(
                self.env_ctx.state_bootstrappers[state_parent],
                level=level + 1,
            )


class PythonExecutable(enum.IntEnum):
    """
    Python executables started during the bootstrap process - each replaces the executable program (via `os.execv`).
    """

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
            self.cached_value = self._bootstrap_once()
            self.is_bootstrapped = True

        return self.cached_value

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        raise NotImplementedError()


# noinspection PyPep8Naming
class Bootstrapper_state_default_log_level(AbstractCachingStateBootstrapper[int]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[],
            env_state=EnvState.state_default_log_level.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        return logging.INFO


# noinspection PyPep8Naming
class Bootstrapper_state_parsed_args(
    AbstractCachingStateBootstrapper[argparse.Namespace]
):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[],
            env_state=EnvState.state_parsed_args.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        parsed_args: argparse.Namespace = init_arg_parser().parse_args()
        return parsed_args


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
                EnvState.state_parsed_args.name,
            ],
            env_state=EnvState.state_py_exec_specified.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        return PythonExecutable[
            self.env_ctx.bootstrap_state(EnvState.state_parsed_args.name).py_exec
        ]


# noinspection PyPep8Naming
class Bootstrapper_state_proto_kernel_dir_path(AbstractCachingStateBootstrapper[str]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_py_exec_specified.name,
            ],
            env_state=EnvState.state_proto_kernel_dir_path.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:

        state_py_exec_specified: PythonExecutable = self.env_ctx.bootstrap_state(
            EnvState.state_py_exec_specified.name
        )
        main_script_file_abs_path = os.path.abspath(sys.argv[0])
        # Assuming main script and `proto_kernel` are in the same directory:
        proto_kernel_dir_path = os.path.dirname(main_script_file_abs_path)
        if state_py_exec_specified == PythonExecutable.py_exec_unknown:
            logger.info(f"main_script_file_abs_path: {main_script_file_abs_path}")
        return proto_kernel_dir_path


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
        state_proto_kernel_dir_path = self.env_ctx.bootstrap_state(
            EnvState.state_proto_kernel_dir_path.name
        )
        return os.path.join(
            state_proto_kernel_dir_path,
            ConfConstInput.default_file_basename_conf_primer,
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
                EnvState.state_parsed_args.name,
                EnvState.state_proto_kernel_config_file_path.name,
            ],
            env_state=EnvState.state_client_dir_path_specified.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:

        # TODO: access by declared name (string constant):
        state_client_dir_path_specified = self.env_ctx.bootstrap_state(
            EnvState.state_parsed_args.name
        ).client_dir_path

        state_proto_kernel_config_file_path = self.env_ctx.bootstrap_state(
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
        state_proto_kernel_config_file_path = self.env_ctx.bootstrap_state(
            EnvState.state_proto_kernel_config_file_path.name
        )

        file_data: dict
        if os.path.exists(state_proto_kernel_config_file_path):
            file_data = read_json_file(state_proto_kernel_config_file_path)
        else:
            state_proto_kernel_dir_path = self.env_ctx.bootstrap_state(
                EnvState.state_proto_kernel_dir_path.name
            )
            state_client_dir_path_specified = self.env_ctx.bootstrap_state(
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
        state_script_config_file_data = self.env_ctx.bootstrap_state(
            EnvState.state_script_config_file_data.name
        )

        field_client_dir_rel_path = state_script_config_file_data[
            ConfConstPrimer.field_dir_rel_path_root_client
        ]

        state_proto_kernel_dir_path = self.env_ctx.bootstrap_state(
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
                EnvState.state_parsed_args.name,
            ],
            env_state=EnvState.state_target_dst_dir_path.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        # TODO: access via declared string constant for arg field:
        return self.env_ctx.bootstrap_state(
            EnvState.state_parsed_args.name
        ).target_dst_dir_path


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
            ],
            env_state=EnvState.state_client_conf_file_path.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        state_client_dir_path_configured = self.env_ctx.bootstrap_state(
            EnvState.state_client_dir_path_configured.name
        )

        state_script_config_file_data = self.env_ctx.bootstrap_state(
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

        state_client_conf_file_path = self.env_ctx.bootstrap_state(
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
        file_data = self.env_ctx.bootstrap_state(
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
            self.env_ctx.bootstrap_state(
                EnvState.state_client_dir_path_configured.name
            ),
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

        state_target_dst_dir_path = self.env_ctx.bootstrap_state(
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
        state_env_conf_dir_path = self.env_ctx.bootstrap_state(
            EnvState.state_env_conf_dir_path.name
        )
        state_target_dst_dir_path = self.env_ctx.bootstrap_state(
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
                    f"The `@/conf/` dir does not exists and `target_dst_dir_path` is not provided - see `--help`.",
                )
            else:
                state_target_dst_dir_path_verified = self.env_ctx.bootstrap_state(
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
        state_env_conf_dir_path_verified = self.env_ctx.bootstrap_state(
            EnvState.state_env_conf_dir_path_verified.name
        )
        assert state_env_conf_dir_path_verified

        state_client_dir_path_configured = self.env_ctx.bootstrap_state(
            EnvState.state_client_dir_path_configured.name
        )
        state_env_conf_file_path = os.path.join(
            state_client_dir_path_configured,
            ConfConstClient.default_dir_rel_path_conf_env_link_name,
            # TODO: Do not use default values directly - resolve it differently at the prev|next step based on the need:
            ConfConstClient.default_file_basename_conf_env,
        )
        state_env_conf_dir_path = self.env_ctx.bootstrap_state(
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
        state_env_conf_file_path = self.env_ctx.bootstrap_state(
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
        file_data = self.env_ctx.bootstrap_state(EnvState.state_env_conf_file_data.name)

        state_env_path_to_python = file_data.get(
            ConfConstEnv.field_file_abs_path_python,
            # TODO: Do not use default values directly - resolve it differently at the prev|next step based on the need:
            ConfConstEnv.default_file_abs_path_python,
        )

        if not os.path.isabs(state_env_path_to_python):
            state_env_path_to_python = os.path.join(
                self.env_ctx.bootstrap_state(
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
            ],
            env_state=EnvState.state_env_path_to_venv.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        file_data = self.env_ctx.bootstrap_state(EnvState.state_env_conf_file_data.name)

        state_env_path_to_venv = file_data.get(
            ConfConstEnv.field_dir_rel_path_venv,
            # TODO: Do not use default values directly - resolve it differently at the prev|next step based on the need:
            ConfConstEnv.default_dir_rel_path_venv,
        )

        if not os.path.isabs(state_env_path_to_venv):
            state_env_path_to_venv = os.path.join(
                self.env_ctx.bootstrap_state(
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

        state_py_exec_specified: PythonExecutable = self.env_ctx.bootstrap_state(
            EnvState.state_py_exec_specified.name
        )

        state_env_path_to_python = self.env_ctx.bootstrap_state(
            EnvState.state_env_path_to_python.name
        )
        state_env_path_to_venv = self.env_ctx.bootstrap_state(
            EnvState.state_env_path_to_venv.name
        )

        # TODO: Make it separate validation state
        #       (not a dependency of this because, technically, we do not know where `EnvState.state_env_path_to_python` and `EnvState.state_env_path_to_venv` came from):
        if is_sub_path(state_env_path_to_python, state_env_path_to_venv):
            state_env_conf_file_path = self.env_ctx.bootstrap_state(
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

        def switch_to_required_python():
            assert state_py_exec_specified == PythonExecutable.py_exec_unknown
            self.env_ctx.py_exec = PythonExecutable.py_exec_arbitrary
            logger.info(
                f"switching from current `python` interpreter [{path_to_curr_python}] to required one [{state_env_path_to_python}]"
            )
            os.execv(
                state_env_path_to_python,
                [
                    state_env_path_to_python,
                    *sys.argv,
                    ArgConst.arg_py_exec,
                    PythonExecutable.py_exec_required.name,
                ],
            )

        venv_path_to_python = os.path.join(
            state_env_path_to_venv,
            ConfConstGeneral.file_rel_path_venv_python,
        )
        path_to_curr_python = get_path_to_curr_python()
        if is_sub_path(path_to_curr_python, state_env_path_to_venv):
            if path_to_curr_python != venv_path_to_python:
                # Ensure `python` is from the correct `venv` path
                switch_to_required_python()
            else:
                # If already under `venv` with the expected path, nothing to do.
                assert (
                    state_py_exec_specified == PythonExecutable.py_exec_unknown
                    or state_py_exec_specified >= PythonExecutable.py_exec_venv
                )
                # Successfully reached end goal:
                if state_py_exec_specified == PythonExecutable.py_exec_unknown:
                    self.env_ctx.py_exec = PythonExecutable.py_exec_venv
                else:
                    self.env_ctx.py_exec = state_py_exec_specified
        else:
            if path_to_curr_python != state_env_path_to_python:
                switch_to_required_python()
            else:
                assert (
                    state_py_exec_specified == PythonExecutable.py_exec_unknown
                    or state_py_exec_specified == PythonExecutable.py_exec_required
                )
                self.env_ctx.py_exec = PythonExecutable.py_exec_required
                if not os.path.exists(state_env_path_to_venv):
                    logger.info(f"creating `venv` [{state_env_path_to_venv}]")
                    venv.create(
                        state_env_path_to_venv,
                        with_pip=True,
                    )
                else:
                    logger.info(f"reusing existing `venv` [{state_env_path_to_venv}]")
                logger.info(
                    f"switching from current `python` interpreter [{state_env_path_to_python}] to `venv` interpreter [{venv_path_to_python}]"
                )
                os.execv(
                    venv_path_to_python,
                    [
                        venv_path_to_python,
                        *sys.argv,
                        ArgConst.arg_py_exec,
                        PythonExecutable.py_exec_venv.name,
                    ],
                )

        return self.env_ctx.py_exec


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
            ],
            env_state=EnvState.state_protoprimer_package_installed.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        state_py_exec_selected: PythonExecutable = self.env_ctx.bootstrap_state(
            EnvState.state_py_exec_selected.name
        )
        assert state_py_exec_selected >= PythonExecutable.py_exec_venv

        state_client_dir_path_configured = self.env_ctx.bootstrap_state(
            EnvState.state_client_dir_path_configured.name
        )

        setup_py_dir = os.path.join(
            state_client_dir_path_configured,
            "src",
        )
        assert os.path.isfile(os.path.join(setup_py_dir, "setup.py"))

        if state_py_exec_selected == PythonExecutable.py_exec_venv:
            # TODO: This has to be changed for released version of `primer_kernel`:
            install_editable_package(
                setup_py_dir,
                [
                    "test",
                ],
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
                EnvState.state_protoprimer_package_installed.name,
            ],
            env_state=EnvState.state_py_exec_updated_protoprimer_package_reached.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:

        state_py_exec_specified: PythonExecutable = self.env_ctx.bootstrap_state(
            EnvState.state_py_exec_specified.name
        )

        state_protoprimer_package_installed: bool = self.env_ctx.bootstrap_state(
            EnvState.state_protoprimer_package_installed.name
        )
        assert state_protoprimer_package_installed

        venv_path_to_python = get_path_to_curr_python()

        if (
            state_py_exec_specified.value
            < PythonExecutable.py_exec_updated_protoprimer_package.value
        ):
            self.env_ctx.py_exec = PythonExecutable.py_exec_updated_protoprimer_package
            logger.info(
                f"restarting current `python` interpreter [{venv_path_to_python}] to make [{EnvState.state_protoprimer_package_installed.name}] effective"
            )
            os.execv(
                venv_path_to_python,
                [
                    venv_path_to_python,
                    *sys.argv,
                    ArgConst.arg_py_exec,
                    PythonExecutable.py_exec_updated_protoprimer_package.name,
                ],
            )
        else:
            # Successfully reached end goal:
            self.env_ctx.py_exec = state_py_exec_specified

        return self.env_ctx.py_exec


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
                EnvState.state_proto_kernel_dir_path.name,
            ],
            env_state=EnvState.state_proto_kernel_updated.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        state_py_exec_updated_protoprimer_package_reached: PythonExecutable = (
            self.env_ctx.bootstrap_state(
                EnvState.state_py_exec_updated_protoprimer_package_reached.name
            )
        )
        assert (
            state_py_exec_updated_protoprimer_package_reached
            >= PythonExecutable.py_exec_updated_protoprimer_package
        )

        # TODO: optimize: run this logic only when `PythonExecutable.py_exec_updated_protoprimer_package`

        state_proto_kernel_dir_path = self.env_ctx.bootstrap_state(
            EnvState.state_proto_kernel_dir_path.name
        )
        assert os.path.isabs(state_proto_kernel_dir_path)

        proto_kernel_abs_path = os.path.join(
            state_proto_kernel_dir_path,
            # TODO: be able to configure it:
            ConfConstGeneral.default_proto_kernel_basename,
        )
        assert not os.path.islink(proto_kernel_abs_path)
        assert os.path.isfile(proto_kernel_abs_path)

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
            f"writing `primer_kernel_abs_path` [{primer_kernel_abs_path}] over `proto_kernel_abs_path` [{proto_kernel_abs_path}]"
        )
        write_text_file(
            file_path=proto_kernel_abs_path,
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
            ],
            env_state=EnvState.state_py_exec_updated_proto_kernel_code.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:

        state_py_exec_specified: PythonExecutable = self.env_ctx.bootstrap_state(
            EnvState.state_py_exec_specified.name
        )

        state_proto_kernel_updated: bool = self.env_ctx.bootstrap_state(
            EnvState.state_proto_kernel_updated.name
        )
        assert state_proto_kernel_updated

        venv_path_to_python = get_path_to_curr_python()

        if (
            state_py_exec_specified.value
            < PythonExecutable.py_exec_updated_proto_kernel_code.value
        ):
            self.env_ctx.py_exec = PythonExecutable.py_exec_updated_proto_kernel_code
            logger.info(
                f"restarting current `python` interpreter [{venv_path_to_python}] to make [{EnvState.state_proto_kernel_updated.name}] effective"
            )
            os.execv(
                venv_path_to_python,
                [
                    venv_path_to_python,
                    *sys.argv,
                    ArgConst.arg_py_exec,
                    PythonExecutable.py_exec_updated_proto_kernel_code.name,
                ],
            )
        else:
            # Successfully reached end goal:
            self.env_ctx.py_exec = state_py_exec_specified

        return self.env_ctx.py_exec


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

        state_py_exec_updated_proto_kernel_code = self.env_ctx.bootstrap_state(
            EnvState.state_py_exec_updated_proto_kernel_code.name
        )

        assert state_py_exec_updated_proto_kernel_code

        # TODO: this should be the last executable here:
        assert (
            self.env_ctx.py_exec >= PythonExecutable.py_exec_updated_protoprimer_package
        )

        state_env_path_to_venv = self.env_ctx.bootstrap_state(
            EnvState.state_env_path_to_venv.name
        )

        venv_path_to_activate = os.path.join(
            state_env_path_to_venv,
            ConfConstGeneral.file_rel_path_venv_activate,
        )

        # TODO: avoid generating new temp file:
        temp_file = tempfile.NamedTemporaryFile(mode="w+t", encoding="utf-8")
        temp_file.write(f"source ~/.bashrc && source {venv_path_to_activate}")
        temp_file.flush()
        file_path = temp_file.name
        logger.info(f"file_path: {temp_file.name}")
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
    """

    def __init__(
        self,
        # Default implementation (for reference):
        default_impl,
    ):
        self.default_impl = default_impl

    state_default_log_level = (Bootstrapper_state_default_log_level,)

    state_parsed_args = (Bootstrapper_state_parsed_args,)

    state_py_exec_specified = (Bootstrapper_state_py_exec_specified,)

    state_proto_kernel_dir_path = (Bootstrapper_state_proto_kernel_dir_path,)

    state_proto_kernel_config_file_path = (
        Bootstrapper_state_proto_kernel_config_file_path,
    )

    state_client_dir_path_specified = (Bootstrapper_state_client_dir_path_specified,)

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
    Some of the key `EnvState`-s which are often used as bootstrap targets.
    """

    target_full_proto_bootstrap: str = (
        EnvState.state_py_exec_updated_proto_kernel_code.name
    )

    target_activated_venv_shell: str = EnvState.state_activated_venv_shell_started.name


class ArgConst:

    # TODO: decide on convention for pure `arg_name` and `--arg_name`:
    name_recursion_flag = "recursion_flag"
    name_client_dir_path = "client_dir_path"
    name_py_exec = "py_exec"

    arg_recursion_flag = f"--{name_recursion_flag}"
    arg_client_dir_path = f"--{name_client_dir_path}"
    arg_py_exec = f"--{name_py_exec}"


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

    default_file_basename_conf_primer = (
        f"conf_primer.{ConfConstGeneral.default_primer_kernel_module}.json"
    )


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

    default_dir_rel_path_conf_env_link_name = os.path.join(
        "conf_env",
    )

    default_file_basename_conf_env = (
        f"conf_env.{ConfConstGeneral.default_primer_kernel_module}.json"
    )


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

        self.py_exec: PythonExecutable = PythonExecutable.py_exec_unknown

        self.recursion_flag: bool = False
        self.activate_venv_only_flag: bool = False

        self.custom_logger: logging.Logger = logging.getLogger()

        self.register_bootstrapper(Bootstrapper_state_default_log_level(self))
        self.register_bootstrapper(Bootstrapper_state_parsed_args(self))
        self.register_bootstrapper(Bootstrapper_state_py_exec_specified(self))
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

    def configure_logger(
        self,
    ) -> None:
        # Make all warnings be captured by the logging subsystem:
        logging.captureWarnings(True)

        log_formatter = CustomFormatter()

        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(logging.NOTSET)
        stderr_handler.setFormatter(log_formatter)

        self.custom_logger.addHandler(stderr_handler)

        # TODO: Is it the way we want to do it (given that this function is called outside the bootstrap process)?
        #       Review all other similar cases.
        self.set_log_level(self.bootstrap_state(EnvState.state_default_log_level.name))

    def set_log_level(
        self,
        log_level: int,
    ):
        self.log_level = log_level
        self.custom_logger.setLevel(self.log_level)

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

        is_reportable: bool
        if is_successful:
            color_status = color_success
            status_name = "SUCCESS"
            is_reportable = self.log_level <= logging.INFO
        else:
            color_status = color_failure
            status_name = "FAILURE"
            is_reportable = self.log_level <= logging.CRITICAL

        if is_reportable:
            print(
                f"{color_status}{status_name}{color_reset}: {get_path_to_curr_python()} {get_script_command_line()}",
                file=sys.stderr,
                flush=True,
            )

    def select_log_level_from_cli_args(
        self,
        parsed_args,
    ):
        if parsed_args.log_level_silent:
            # disable logs = no output:
            self.set_log_level(logging.CRITICAL + 1)
        elif parsed_args.log_level_quiet:
            self.set_log_level(logging.ERROR)
        elif parsed_args.log_level_verbose >= 2:
            self.set_log_level(logging.NOTSET)
        elif parsed_args.log_level_verbose == 1:
            self.set_log_level(logging.DEBUG)
        else:
            self.set_log_level(
                self.bootstrap_state(EnvState.state_default_log_level.name)
            )

    def run_stages(
        self,
    ):
        run_mode: RunMode = RunMode[
            self.bootstrap_state(EnvState.state_parsed_args.name).run_mode
        ]
        state_name: str = self.bootstrap_state(
            EnvState.state_parsed_args.name
        ).state_name

        if state_name is None:
            env_state = self.universal_sink
        else:
            env_state: str = EnvState[state_name].name

        if run_mode is None:
            pass
        elif run_mode == RunMode.print_dag:
            self.do_print_dag(env_state)
        elif run_mode == RunMode.bootstrap_env:
            self.do_bootstrap_env(env_state)
        else:
            raise ValueError(f"cannot handle run mode [{run_mode}]")

    def do_print_dag(
        self,
        env_state: str,
    ):
        state_bootstrapper: AbstractBootstrapperVisitor = self.state_bootstrappers[
            env_state
        ]
        SinkPrinterVisitor(self).visit_bootstrapper(state_bootstrapper)

    def do_bootstrap_env(
        self,
        # TODO: use this:
        env_state: str,
    ):
        # FS_28_84_41_40: flexible bootstrap
        # `init_venv`
        self.bootstrap_state(env_state)

        # FS_28_84_41_40: flexible bootstrap
        # `install_deps`
        # TODO: TODO_11_66_62_70: python_bootstrap:

        # FS_28_84_41_40: flexible bootstrap
        # `generate_files`
        # TODO: TODO_11_66_62_70: python_bootstrap:


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


if __name__ == "__main__":
    main()
