#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (C) 2025 Alexey Pakseykin
# Source: https://github.com/uvsmtid/protoprimer
"""

TODO: TODO_91_75_37_57.implement_shebang_update.md / FT_02_89_37_65.shebang_line.md and update this comment:
The script must be run with Python 3.
Ensure that `python3` is in the `PATH` for shebang to work.
"""
from __future__ import annotations

import argparse
import atexit
import datetime
import enum
import importlib
import importlib.util
import json
import logging
import os
import pathlib
import shlex
import shutil
import subprocess
import sys
import tempfile
import typing
import venv

__version__ = "0.0.6"

from typing import (
    Any,
    Generic,
    TypeVar,
)

logger: logging.Logger = logging.getLogger()

ValueType = TypeVar("ValueType")


def main(
    configure_env_context: typing.Callable[[], EnvContext] | None = None,
):

    try:
        ensure_min_python_version()

        if configure_env_context is None:
            env_ctx = EnvContext()
        else:
            # See UC_10_80_27_57.extend_DAG.md:
            env_ctx = configure_env_context()

        # TODO: Do not call `state_graph.eval_state` directly - evaluate state via child state (to check that this is eligible).
        #       But... What is the child state here?
        state_run_mode_executed: bool = env_ctx.state_graph.eval_state(
            TargetState.target_run_mode_executed
        )
        assert state_run_mode_executed
        atexit.register(lambda: env_ctx.print_exit_line(0))
    except SystemExit as sys_exit:
        exit_code: int = sys_exit.code
        if exit_code is None or exit_code == 0:
            atexit.register(lambda: env_ctx.print_exit_line(0))
        else:
            atexit.register(lambda: env_ctx.print_exit_line(exit_code))
        # We only catch `SystemExit` to print the status line.
        # The actual exit code is already in-flight with `SystemExit`, propagate it:
        raise
    except:
        atexit.register(lambda: env_ctx.print_exit_line(1))
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


class PythonExecutable(enum.IntEnum):
    """
    Python executables started during the bootstrap process - each replaces the executable program (via `os.execv`).

    See FT_72_45_12_06.python_executable.md
    """

    # `python` executable has not been categorized yet:
    py_exec_unknown = -1

    # To run `proto_code` by any `python` outside `venv`:
    py_exec_arbitrary = 1

    # To run `python` of specific version (to create `venv` using that `python`):
    py_exec_required = 2

    # To use `venv` (to install packages):
    py_exec_venv = 3

    # After making the latest `protoprimer` effective:
    py_exec_updated_protoprimer_package = 4

    # After making the updated `proto_code` effective:
    py_exec_updated_proto_code = 5

    # TODO: make "proto" clone of client extension effective:
    py_exec_updated_client_package = 6

    def __str__(self):
        return f"{self.name}[{self.value}]"


class TermColor(enum.Enum):
    """
    Color codes for terminal text

    Reference:
    *   https://pkg.go.dev/github.com/whitedevops/colors
    *   https://gist.github.com/vratiu/9780109
    """

    # Direct colors:
    # do not use them directly, use semantic colors instead (below).

    back_dark_red = "\033[41m"
    back_dark_green = "\033[42m"
    back_dark_yellow = "\033[43m"
    back_dark_blue = "\033[44m"

    back_light_gray = "\033[47m"

    back_bright_red = "\033[101m"
    back_bright_green = "\033[102m"
    back_bright_yellow = "\033[103m"

    fore_dark_black = "\033[30m"
    fore_dark_red = "\033[31m"
    fore_dark_green = "\033[32m"
    fore_dark_yellow = "\033[33m"
    fore_dark_blue = "\033[34m"
    fore_dark_magenta = "\033[35m"
    fore_dark_cyan = "\033[36m"
    fore_dark_gray = "\033[90m"

    fore_bright_gray = "\033[90m"
    fore_bright_red = "\033[91m"
    fore_bright_green = "\033[92m"
    fore_bright_yellow = "\033[93m"
    fore_bright_blue = "\033[94m"
    fore_bright_magenta = "\033[95m"
    fore_bright_cyan = "\033[96m"
    fore_bright_white = "\033[97m"

    fore_bold_dark_red = "\033[1;31m"

    # Semantic colors:

    field_name = f"{fore_bright_magenta}"
    field_description = f"{fore_bright_cyan}"
    field_review = f"{fore_bright_green}"
    error_text = f"{back_bright_yellow}{fore_dark_red}"

    reset_style = "\033[0m"


class ConfLeap(enum.Enum):
    """
    See FT_89_41_35_82.conf_leap.md
    """

    leap_input = "input"

    leap_primer = "primer"

    leap_client = "client"

    leap_env = "env"


class PrimerRuntime(enum.Enum):
    """
    See FT_14_52_73_23.primer_runtime.md
    """

    runtime_proto = "proto"

    runtime_neo = "neo"


class RunMode(enum.Enum):
    """
    Various modes the script can be run in.

    See FT_11_27_29_83.run_mode.md
    """

    mode_prime = "prime"

    # TODO: implement:
    mode_check = "check"

    mode_wizard = "wizard"

    mode_graph = "graph"


class CommandAction(enum.Enum):

    # See UC_61_12_90_59.reinstall_venv.md
    action_reinstall = "reinstall"

    action_command = "command"


class WizardStage(enum.Enum):

    wizard_started = "wizard_started"

    wizard_finished = "wizard_finished"


class FilesystemObject(enum.Enum):

    fs_object_file = "file"

    fs_object_dir = "dir"


class PathType(enum.Enum):

    # If both paths are possible (absolute or relative):
    path_any = "any_path"

    # Relative path:
    path_rel = "rel_path"

    # Absolute path:
    path_abs = "abs_path"


class EnvVar(enum.Enum):
    """
    See FT_08_92_69_92.env_var.md
    """

    var_PROTOPRIMER_STDERR_LOG_LEVEL = "PROTOPRIMER_STDERR_LOG_LEVEL"

    var_PROTOPRIMER_PY_EXEC = "PROTOPRIMER_PY_EXEC"

    var_PROTOPRIMER_DO_INSTALL = "PROTOPRIMER_DO_INSTALL"


class ConfDst(enum.Enum):
    """
    See FT_23_37_64_44.conf_dst.md
    """

    dst_shebang = "shebang"

    dst_global = "gconf"

    dst_local = "lconf"


class ValueName(enum.Enum):

    value_stderr_log_level = "stderr_log_level"

    value_do_install = "do_install"

    value_run_mode = "run_mode"

    value_wizard_stage = "wizard_stage"

    value_final_state = "final_state"

    value_py_exec = "py_exec"

    value_primer_runtime = "primer_runtime"

    value_start_id = "start_id"

    value_project_descriptors = "project_descriptors"

    value_install_extras = "install_extras"


class PathName(enum.Enum):

    path_proto_code = "proto_code"

    # TODO: make use of it in naming states (instead of using only `path_proto_code`):
    path_proto_dir = "proto_dir"

    # TODO: Add a `feature_topic` for `ref root`:
    path_ref_root = "ref_root"

    # See FT_89_41_35_82.conf_leap.md / primer
    path_conf_primer = f"conf_{ConfLeap.leap_primer.value}"

    # See FT_89_41_35_82.conf_leap.md / env
    path_conf_client = f"conf_{ConfLeap.leap_client.value}"

    # See FT_89_41_35_82.conf_leap.md / env
    path_conf_env = f"conf_{ConfLeap.leap_env.value}"

    # TODO: Rename to "lconf_link" (otherwise, `client_link_name_dir_rel_path` does not reflect anything about `lconf` or `leap_env`):
    path_link_name = "link_name"

    path_default_env = "default_env"

    path_local_env = "local_env"

    path_local_python = "local_python"

    path_local_venv = "local_venv"

    path_local_log = "local_log"

    path_local_tmp = "local_tmp"

    path_build_root = "build_root"


class ParsedArg(enum.Enum):
    name_proto_code = (
        f"{PathName.path_proto_code.value}_{FilesystemObject.fs_object_file.value}"
    )

    name_reinstall = f"do_{CommandAction.action_reinstall.value}"

    name_command = f"run_{CommandAction.action_command.value}"

    name_primer_runtime = str(ValueName.value_primer_runtime.value)
    name_start_id = str(ValueName.value_start_id.value)
    name_run_mode = str(ValueName.value_run_mode.value)
    name_wizard_stage = str(ValueName.value_wizard_stage.value)
    name_final_state = str(ValueName.value_final_state.value)


# TODO: Add file_log_level (but not via CLI, via config):
class LogLevel(enum.Enum):
    name_silent = "silent"
    name_quiet = "quiet"
    name_verbose = "verbose"


class SyntaxArg:

    arg_reinstall = f"--{CommandAction.action_reinstall.value}"

    arg_mode_graph = f"--{RunMode.mode_graph.value}"
    arg_mode_prime = f"--{RunMode.mode_prime.value}"
    arg_mode_check = f"--{RunMode.mode_check.value}"
    arg_mode_wizard = f"--{RunMode.mode_wizard.value}"

    arg_proto_code_abs_file_path = f"--{ParsedArg.name_proto_code.value}"
    arg_primer_runtime = f"--{ParsedArg.name_primer_runtime.value}"
    arg_start_id = f"--{ParsedArg.name_start_id.value}"
    arg_run_mode = f"--{ParsedArg.name_run_mode.value}"
    arg_wizard_stage = f"--{ParsedArg.name_wizard_stage.value}"
    arg_final_state = f"--{ParsedArg.name_final_state.value}"

    arg_c = f"-{CommandAction.action_command.value[0]}"
    arg_command = f"--{CommandAction.action_command.value}"

    arg_s = f"-{LogLevel.name_silent.value[0]}"
    arg_silent = f"--{LogLevel.name_silent.value}"
    dest_silent = f"{ValueName.value_stderr_log_level}_{LogLevel.name_silent.value}"

    arg_q = f"-{LogLevel.name_quiet.value[0]}"
    arg_quiet = f"--{LogLevel.name_quiet.value}"
    dest_quiet = f"{ValueName.value_stderr_log_level}_{LogLevel.name_quiet.value}"

    arg_v = f"-{LogLevel.name_verbose.value[0]}"
    arg_verbose = f"--{LogLevel.name_verbose.value}"
    dest_verbose = f"{ValueName.value_stderr_log_level}_{LogLevel.name_verbose.value}"


class ConfField(enum.Enum):

    field_primer_ref_root_dir_rel_path = f"{ConfLeap.leap_primer.value}_{PathName.path_ref_root.value}_{FilesystemObject.fs_object_dir.value}_{PathType.path_rel.value}"

    field_primer_conf_client_file_rel_path = f"{ConfLeap.leap_primer.value}_{PathName.path_conf_client.value}_{FilesystemObject.fs_object_file.value}_{PathType.path_rel.value}"

    field_client_link_name_dir_rel_path = f"{ConfLeap.leap_client.value}_{PathName.path_link_name.value}_{FilesystemObject.fs_object_dir.value}_{PathType.path_rel.value}"

    field_client_default_env_dir_rel_path = f"{ConfLeap.leap_client.value}_{PathName.path_default_env.value}_{FilesystemObject.fs_object_dir.value}_{PathType.path_rel.value}"

    field_env_local_python_file_abs_path = f"{ConfLeap.leap_env.value}_{PathName.path_local_python.value}_{FilesystemObject.fs_object_file.value}_{PathType.path_abs.value}"

    field_env_local_venv_dir_rel_path = f"{ConfLeap.leap_env.value}_{PathName.path_local_venv.value}_{FilesystemObject.fs_object_dir.value}_{PathType.path_rel.value}"

    field_env_local_log_dir_rel_path = f"{ConfLeap.leap_env.value}_{PathName.path_local_log.value}_{FilesystemObject.fs_object_dir.value}_{PathType.path_rel.value}"

    field_env_local_tmp_dir_rel_path = f"{ConfLeap.leap_env.value}_{PathName.path_local_tmp.value}_{FilesystemObject.fs_object_dir.value}_{PathType.path_rel.value}"

    field_env_project_descriptors = (
        f"{ConfLeap.leap_env.value}_{ValueName.value_project_descriptors.value}"
    )

    field_env_build_root_dir_rel_path = f"{ConfLeap.leap_env.value}_{PathName.path_build_root.value}_{FilesystemObject.fs_object_dir.value}_{PathType.path_rel.value}"

    field_env_install_extras = (
        f"{ConfLeap.leap_env.value}_{ValueName.value_install_extras.value}"
    )


class ConfConstGeneral:

    name_protoprimer_package = "protoprimer"
    name_proto_code = "proto_code"
    name_primer_kernel_module = "primer_kernel"
    default_proto_code_module = "proto_kernel"
    default_proto_code_basename = f"{default_proto_code_module}.py"

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

    func_get_proto_code_generated_boilerplate_multiple_body = lambda module_obj: (
        f"""
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
"""
    )

    func_get_proto_code_generated_boilerplate_single_header = lambda module_obj: (
        f"""
################################################################################
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
################################################################################
# This is a (proto) copy of `{module_obj.__name__}` updated automatically.
# It is supposed to be versioned
# (to be available in the target client repo on clone),
# but it should not be linted
# (as its content/style is governed by the source repo).
################################################################################
"""
    )


class ConfConstInput:
    """
    Constants for FT_89_41_35_82.conf_leap.md / leap_input
    """

    file_abs_path_script = ConfConstGeneral.input_based
    dir_abs_path_current = ConfConstGeneral.input_based

    default_proto_conf_dir_rel_path: str = f"{ConfConstGeneral.name_proto_code}"

    # Next FT_89_41_35_82.conf_leap.md: `ConfLeap.leap_primer`:
    default_file_basename_conf_primer = f"{ConfConstGeneral.default_proto_code_module}.{PathName.path_conf_primer.value}.json"

    ext_env_var_VIRTUAL_ENV: str = "VIRTUAL_ENV"
    ext_env_var_PATH: str = "PATH"
    ext_env_var_PYTHONPATH: str = "PYTHONPATH"

    default_PROTOPRIMER_STDERR_LOG_LEVEL: str = "INFO"

    default_PROTOPRIMER_PY_EXEC: str = PythonExecutable.py_exec_unknown.name

    default_PROTOPRIMER_DO_INSTALL: str = str(True)


class ConfConstPrimer:
    """
    Constants for FT_89_41_35_82.conf_leap.md / leap_primer
    """

    default_client_conf_dir_rel_path: str = f"{ConfDst.dst_global.value}"

    # Next FT_89_41_35_82.conf_leap.md: `ConfLeap.leap_client`:
    default_file_basename_leap_client: str = (
        f"{ConfConstGeneral.default_proto_code_module}.{PathName.path_conf_client.value}.json"
    )

    default_client_conf_file_rel_path: str = os.path.join(
        default_client_conf_dir_rel_path,
        default_file_basename_leap_client,
    )


class ConfConstClient:
    """
    Constants for FT_89_41_35_82.conf_leap.md / leap_client
    """

    default_dir_rel_path_leap_env_link_name: str = os.path.join(
        ConfDst.dst_local.value,
    )

    # FT_59_95_81_63.env_layout.md / max layout
    default_client_default_env_dir_rel_path: str = os.path.join(
        "dst",
        "default_env",
    )

    # Next FT_89_41_35_82.conf_leap.md: `ConfLeap.leap_env`:
    default_file_basename_leap_env: str = (
        f"{ConfConstGeneral.default_proto_code_module}.{PathName.path_conf_env.value}.json"
    )

    default_env_conf_file_rel_path: str = os.path.join(
        default_client_default_env_dir_rel_path,
        default_file_basename_leap_env,
    )

    default_pyproject_toml_basename = "pyproject.toml"


class ConfConstEnv:
    """
    Constants for FT_89_41_35_82.conf_leap.md / leap_env
    """

    # TODO: This may not work everywhere:
    default_file_abs_path_python = "/usr/bin/python"

    default_dir_rel_path_venv = "venv"

    default_dir_rel_path_log = "log"

    default_dir_rel_path_tmp = "tmp"

    default_project_descriptors = []

    constraints_txt_basename = "constraints.txt"


class FieldWizardMeta:

    def __init__(
        self,
        field_name: str,
        field_help: typing.Callable[[FieldWizardMeta, StateNode, dict], str],
        field_leap: ConfLeap,
        # Field name which contains this field as a nested structure (normally, `None`):
        root_ancestor_field: str | None,
        # Warn if the wizard cannot handle the field:
        warn_if_not_wizard_able: typing.Callable[
            [FieldWizardMeta, StateNode, dict], str | None
        ],
        read_value: typing.Callable[[FieldWizardMeta, StateNode, dict], str],
        validate_value: typing.Callable[
            [FieldWizardMeta, StateNode, dict, str], str | None
        ],
        review_value: typing.Callable[
            [FieldWizardMeta, StateNode, dict, str], str | None
        ],
        write_value: typing.Callable[[FieldWizardMeta, StateNode, dict, str], None],
    ):
        self.field_name: str = field_name
        self.field_help: typing.Callable[[FieldWizardMeta, StateNode, dict], str] = (
            FieldWizardMeta.get_callable(field_help)
        )
        self.field_leap: ConfLeap = field_leap
        # Set to `field_name` if `none` for simplicity:
        self.root_ancestor_field: str = (
            field_name if root_ancestor_field is None else root_ancestor_field
        )
        self.warn_if_not_wizard_able: typing.Callable[
            [FieldWizardMeta, StateNode, dict], str | None
        ] = FieldWizardMeta.get_callable(warn_if_not_wizard_able)
        self.read_value: typing.Callable[[FieldWizardMeta, StateNode, dict], str] = (
            FieldWizardMeta.get_callable(read_value)
        )
        self.validate_value: typing.Callable[
            [FieldWizardMeta, StateNode, dict, str], str | None
        ] = FieldWizardMeta.get_callable(validate_value)
        self.review_value: typing.Callable[
            [FieldWizardMeta, StateNode, dict, str], str | None
        ] = FieldWizardMeta.get_callable(review_value)
        self.write_value: typing.Callable[
            [FieldWizardMeta, StateNode, dict, str], None
        ] = FieldWizardMeta.get_callable(write_value)

    @staticmethod
    def get_callable(staticmethod_or_callable):
        """
        This explicit function is only needed for earlier Python (e.g. 3.8) due to PEP 695 - ask LLM why.
        """
        if isinstance(staticmethod_or_callable, staticmethod):
            return staticmethod_or_callable.__func__
        else:
            return staticmethod_or_callable


class WizardField(enum.Enum):

    @staticmethod
    def enumerate_conf_leap_fields(
        conf_leap: ConfLeap,
    ) -> list[tuple[int, WizardField]]:
        enumerated_conf_leap_fields: list[tuple[int, WizardField]] = []
        for total_ordinal_i, wizard_field in enumerate(WizardField):
            if wizard_field.value.field_leap == conf_leap:
                enumerated_conf_leap_fields.append((total_ordinal_i, wizard_field))
        return enumerated_conf_leap_fields

    @staticmethod
    def warn_if_not_wizard_able_field_env_build_root_dir_rel_path(
        wizard_meta: FieldWizardMeta,
        state_node: StateNode,
        file_data: dict,
    ) -> str | None:
        """
        Wizard is limited to simple field-value pairs only in the root of the conf file.
        But `ConfField.field_env_build_root_dir_rel_path` is part of a `list` of nested `dict`-s.
        Since the wizard is supposed to be used only for initial setup,
        it only supports updating a path to a lone project.
        Essentially, the wizard reduces that field to a single field-value pair only.
        """
        assert (
            wizard_meta.field_name == ConfField.field_env_build_root_dir_rel_path.value
        )
        warn_text = (
            f"WARNING: Field [{ConfField.field_env_build_root_dir_rel_path.value}] cannot be updated by the wizard anymore. "
            f"To use the wizard for this field again, remove the entire [{ConfField.field_env_project_descriptors.value}] field manually. "
            f"See in the corresponding [{FieldWizardMeta.__name__}] entry in the code. "
        )
        if ConfField.field_env_project_descriptors.value not in file_data:
            return None
        field_env_project_descriptors = file_data[
            ConfField.field_env_project_descriptors.value
        ]
        assert isinstance(field_env_project_descriptors, list)
        if len(field_env_project_descriptors) > 1:
            return warn_text
        if len(field_env_project_descriptors) < 1:
            return None
        single_project_descriptor = field_env_project_descriptors[0]
        assert isinstance(single_project_descriptor, dict)

        if (
            ConfField.field_env_build_root_dir_rel_path.value
            in single_project_descriptor
        ):
            build_root = single_project_descriptor[
                ConfField.field_env_build_root_dir_rel_path.value
            ]
            assert isinstance(build_root, str)

        if ConfField.field_env_install_extras.value in single_project_descriptor:
            install_extras = single_project_descriptor[
                ConfField.field_env_install_extras.value
            ]
            assert isinstance(install_extras, list)
            if len(install_extras) > 0:
                return warn_text

        return None

    @staticmethod
    def read_field_env_build_root_dir_rel_path(
        wizard_meta: FieldWizardMeta,
        state_node: StateNode,
        file_data: dict,
    ) -> str:
        """
        Reads a single value of `ConfField.field_env_build_root_dir_rel_path`.

        See `warn_if_not_wizard_able_field_env_build_root_dir_rel_path`.
        """
        single_project = WizardField.get_assumed_single_project_descriptor(file_data)

        field_env_build_root_dir_rel_path: str
        if ConfField.field_env_build_root_dir_rel_path.value in single_project:
            field_env_build_root_dir_rel_path = single_project[
                ConfField.field_env_build_root_dir_rel_path.value
            ]
        else:
            field_env_build_root_dir_rel_path = "."
        assert isinstance(field_env_build_root_dir_rel_path, str)

        return field_env_build_root_dir_rel_path

    @staticmethod
    def write_field_env_build_root_dir_rel_path(
        wizard_meta: FieldWizardMeta,
        state_node: StateNode,
        file_data: dict,
        field_value: str,
    ) -> None:
        """
        Writes a single value of `ConfField.field_env_build_root_dir_rel_path`.

        See `warn_if_not_wizard_able_field_env_build_root_dir_rel_path`.
        """
        single_project = WizardField.get_assumed_single_project_descriptor(file_data)
        single_project[ConfField.field_env_build_root_dir_rel_path.value] = field_value
        file_data[ConfField.field_env_project_descriptors.value] = [
            single_project,
        ]

    @staticmethod
    def get_assumed_single_project_descriptor(file_data: dict) -> dict:
        project_descriptors: list[dict]
        if ConfField.field_env_project_descriptors.value in file_data:
            project_descriptors = file_data[
                ConfField.field_env_project_descriptors.value
            ]
        else:
            project_descriptors = []
        assert isinstance(project_descriptors, list)
        if len(project_descriptors) < 1:
            project_descriptors.append({})
        assert len(project_descriptors) == 1
        single_project = project_descriptors[0]
        return single_project

    @staticmethod
    def read_value_trivially(
        wizard_meta: FieldWizardMeta,
        state_node: StateNode,
        file_data: dict,
    ) -> str:
        return file_data[wizard_meta.field_name]

    @staticmethod
    def validate_value_trivially(
        wizard_meta: FieldWizardMeta,
        state_node: StateNode,
        file_data: dict,
        field_value: str,
    ) -> str | None:
        return None

    @staticmethod
    def validate_rel_path_exists(
        wizard_meta,
        state_node,
        file_data,
        rel_path: str,
        base_name: str,
        base_abs_path: str,
    ) -> str | None:
        full_abs_path: str = os.path.join(
            base_abs_path,
            rel_path,
        )
        if os.path.exists(full_abs_path):
            return None
        else:
            return f"The base `{base_name}` [{base_abs_path}] and relative `{wizard_meta.field_name}` [{rel_path}] point to a non-existent path [{full_abs_path}]."

    @staticmethod
    def write_value_trivially(
        wizard_meta: FieldWizardMeta,
        state_node: StateNode,
        file_data: dict,
        # TODO: support any type of field values (currently, only `str` exists):
        field_value: str,
    ) -> None:
        file_data[wizard_meta.field_name] = field_value

    @staticmethod
    def review_value_trivially(
        wizard_meta: FieldWizardMeta,
        state_node: StateNode,
        file_data: dict,
        field_value: str,
    ) -> str | None:
        return None

    field_primer_ref_root_dir_rel_path = FieldWizardMeta(
        field_name=ConfField.field_primer_ref_root_dir_rel_path.value,
        field_help=lambda wizard_meta, state_node, file_data: (
            f"Field `{ConfField.field_primer_ref_root_dir_rel_path.value}` (or `{PathName.path_ref_root.value}` for short) leads to the client reference root "
            f"from the proto code script dir [{state_node.eval_parent_state(EnvState.state_input_proto_code_dir_abs_path_eval_finalized.name)}]. "
            f"Subsequently, the client reference root `{PathName.path_ref_root.value}` is used as a base path for the most of the relative paths. "
        ),
        field_leap=ConfLeap.leap_primer,
        root_ancestor_field=None,
        warn_if_not_wizard_able=lambda wizard_meta, state_node, file_data: None,
        read_value=read_value_trivially,
        validate_value=lambda wizard_meta, state_node, file_data, field_value: WizardField.validate_rel_path_exists(
            wizard_meta,
            state_node,
            file_data,
            field_value,
            PathName.path_proto_dir.value,
            state_node.eval_parent_state(
                EnvState.state_input_proto_code_dir_abs_path_eval_finalized.name
            ),
        ),
        # TODO: consider wrapping it into a function - line is too long:
        review_value=lambda wizard_meta, state_node, file_data, field_value: (
            f"The base [{state_node.eval_parent_state(EnvState.state_input_proto_code_dir_abs_path_eval_finalized.name)}] "
            f"and the relative [{field_value}] paths resolves into absolute "
            f"[{os.path.normpath(os.path.join(state_node.eval_parent_state(EnvState.state_input_proto_code_dir_abs_path_eval_finalized.name), field_value))}]. "
        ),
        write_value=write_value_trivially,
    )

    field_primer_conf_client_file_rel_path = FieldWizardMeta(
        field_name=ConfField.field_primer_conf_client_file_rel_path.value,
        field_help=lambda wizard_meta, state_node, file_data: (
            f"Field `{ConfField.field_primer_conf_client_file_rel_path.value}` (or `{PathName.path_conf_client.value}` for short) leads to the client global configuration "
            f"from the client reference root `{PathName.path_ref_root.value}`. "
            f"Subsequently, the client global configuration `{PathName.path_conf_client.value}` (configuration not specific to the local environment) "
            f"is used by every deployment. "
        ),
        field_leap=ConfLeap.leap_primer,
        root_ancestor_field=None,
        warn_if_not_wizard_able=lambda wizard_meta, state_node, file_data: None,
        read_value=read_value_trivially,
        # NOTE: The file is allowed not to exist:
        validate_value=validate_value_trivially,
        # TODO: consider wrapping it into a function - line is too long:
        review_value=lambda wizard_meta, state_node, file_data, field_value: (
            f"The relative path [{field_value}] "
            f"resolves into absolute path "
            f"[{os.path.normpath(os.path.join(state_node.eval_parent_state(EnvState.state_input_proto_code_dir_abs_path_eval_finalized.name), WizardField.field_primer_ref_root_dir_rel_path.value.read_value(WizardField.field_primer_ref_root_dir_rel_path.value, state_node, file_data), field_value))}]. "
        ),
        write_value=write_value_trivially,
    )

    field_client_link_name_dir_rel_path = FieldWizardMeta(
        field_name=ConfField.field_client_link_name_dir_rel_path.value,
        field_help=lambda wizard_meta, state_node, file_data: (
            # TODO:
            f"Field `{ConfField.field_client_link_name_dir_rel_path.value}` TODO"
        ),
        field_leap=ConfLeap.leap_client,
        root_ancestor_field=None,
        warn_if_not_wizard_able=lambda wizard_meta, state_node, file_data: None,
        read_value=read_value_trivially,
        # TODO:
        validate_value=validate_value_trivially,
        # TODO:
        review_value=review_value_trivially,
        write_value=write_value_trivially,
    )

    field_client_default_env_dir_rel_path = FieldWizardMeta(
        field_name=ConfField.field_client_default_env_dir_rel_path.value,
        field_help=lambda wizard_meta, state_node, file_data: (
            # TODO:
            f"Field `{ConfField.field_client_default_env_dir_rel_path.value}` TODO"
        ),
        field_leap=ConfLeap.leap_client,
        root_ancestor_field=None,
        warn_if_not_wizard_able=lambda wizard_meta, state_node, file_data: None,
        read_value=read_value_trivially,
        # TODO:
        validate_value=validate_value_trivially,
        # TODO:
        review_value=review_value_trivially,
        write_value=write_value_trivially,
    )

    field_env_local_python_file_abs_path = FieldWizardMeta(
        field_name=ConfField.field_env_local_python_file_abs_path.value,
        field_help=lambda wizard_meta, state_node, file_data: (
            # TODO:
            f"Field `{ConfField.field_env_local_python_file_abs_path.value}` TODO"
        ),
        field_leap=ConfLeap.leap_env,
        root_ancestor_field=None,
        warn_if_not_wizard_able=lambda wizard_meta, state_node, file_data: None,
        read_value=read_value_trivially,
        # TODO:
        validate_value=validate_value_trivially,
        # TODO:
        review_value=review_value_trivially,
        write_value=write_value_trivially,
    )

    field_env_local_venv_dir_rel_path = FieldWizardMeta(
        field_name=ConfField.field_env_local_venv_dir_rel_path.value,
        field_help=lambda wizard_meta, state_node, file_data: (
            # TODO:
            f"Field `{ConfField.field_env_local_venv_dir_rel_path.value}` TODO"
        ),
        field_leap=ConfLeap.leap_env,
        root_ancestor_field=None,
        warn_if_not_wizard_able=lambda wizard_meta, state_node, file_data: None,
        read_value=read_value_trivially,
        # TODO:
        validate_value=validate_value_trivially,
        # TODO:
        review_value=review_value_trivially,
        write_value=write_value_trivially,
    )

    field_env_local_log_dir_rel_path = FieldWizardMeta(
        field_name=ConfField.field_env_local_log_dir_rel_path.value,
        field_help=lambda wizard_meta, state_node, file_data: (
            f"Field `{ConfField.field_env_local_log_dir_rel_path.value}` (or `{PathName.path_local_log.value}` for short) leads to the client with log files."
        ),
        field_leap=ConfLeap.leap_env,
        root_ancestor_field=None,
        warn_if_not_wizard_able=lambda wizard_meta, state_node, file_data: None,
        read_value=read_value_trivially,
        validate_value=validate_value_trivially,
        review_value=review_value_trivially,
        write_value=write_value_trivially,
    )

    field_env_local_tmp_dir_rel_path = FieldWizardMeta(
        field_name=ConfField.field_env_local_tmp_dir_rel_path.value,
        field_help=lambda wizard_meta, state_node, file_data: (
            f"Field `{ConfField.field_env_local_tmp_dir_rel_path.value}` (or `{PathName.path_local_tmp.value}` for short) leads to the client with temp files."
        ),
        field_leap=ConfLeap.leap_env,
        root_ancestor_field=None,
        warn_if_not_wizard_able=lambda wizard_meta, state_node, file_data: None,
        read_value=read_value_trivially,
        validate_value=validate_value_trivially,
        review_value=review_value_trivially,
        write_value=write_value_trivially,
    )

    field_env_build_root_dir_rel_path = FieldWizardMeta(
        field_name=ConfField.field_env_build_root_dir_rel_path.value,
        field_help=lambda wizard_meta, state_node, file_data: (
            # TODO:
            f"Field `{ConfField.field_env_build_root_dir_rel_path.value}` TODO"
        ),
        field_leap=ConfLeap.leap_env,
        root_ancestor_field=ConfField.field_env_project_descriptors.value,
        warn_if_not_wizard_able=warn_if_not_wizard_able_field_env_build_root_dir_rel_path,
        read_value=read_field_env_build_root_dir_rel_path,
        # TODO:
        validate_value=validate_value_trivially,
        # TODO:
        review_value=review_value_trivially,
        write_value=write_field_env_build_root_dir_rel_path,
    )


def init_arg_parser():

    suppress_internal_args: bool = True

    arg_parser = argparse.ArgumentParser(
        description="Prime the environment based on existing configuration.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    arg_parser.add_argument(
        SyntaxArg.arg_reinstall,
        type=str2bool,
        nargs="?",
        const=True,
        default=False,
        dest=ParsedArg.name_reinstall.value,
        help="Re-create `venv`, re-install dependencies, and re-pin versions.",
    )

    arg_parser.add_argument(
        SyntaxArg.arg_c,
        SyntaxArg.arg_command,
        type=str,
        dest=ParsedArg.name_command.value,
        help="Command to execute after the bootstrap.",
    )

    mutex_group = arg_parser.add_mutually_exclusive_group()

    mutex_group.add_argument(
        SyntaxArg.arg_mode_prime,
        action="store_const",
        dest=ParsedArg.name_run_mode.value,
        const=RunMode.mode_prime.value,
        help="Prime the environment to be ready to use.",
    )
    mutex_group.add_argument(
        SyntaxArg.arg_mode_check,
        action="store_const",
        dest=ParsedArg.name_run_mode.value,
        const=RunMode.mode_check.value,
        help="Check the environment configuration.",
    )
    mutex_group.add_argument(
        SyntaxArg.arg_mode_wizard,
        action="store_const",
        dest=ParsedArg.name_run_mode.value,
        const=RunMode.mode_wizard.value,
        help="Wizard through the environment configuration.",
    )
    mutex_group.add_argument(
        SyntaxArg.arg_mode_graph,
        action="store_const",
        dest=ParsedArg.name_run_mode.value,
        const=RunMode.mode_graph.value,
        help="Render the graph of state dependencies.",
    )

    mutex_group.set_defaults(run_mode=RunMode.mode_prime.value)

    arg_parser.add_argument(
        # TODO: Make use of or clean up:
        SyntaxArg.arg_primer_runtime,
        type=str,
        choices=[context_phase.name for context_phase in PrimerRuntime],
        default=PrimerRuntime.runtime_proto.name,
        help=(
            argparse.SUPPRESS
            if suppress_internal_args
            else f"Used internally: specifies `{PrimerRuntime.__name__}`."
        ),
    )
    # TODO: Use only -q and -v options in a simpler way:
    arg_parser.add_argument(
        SyntaxArg.arg_s,
        SyntaxArg.arg_silent,
        action="store_true",
        dest=SyntaxArg.dest_silent,
        # In the case of exceptions, stack traces are still printed:
        help="Do not log (set only non-zero exit code on error).",
    )
    arg_parser.add_argument(
        SyntaxArg.arg_q,
        SyntaxArg.arg_quiet,
        action="store_true",
        dest=SyntaxArg.dest_quiet,
        help="Log errors messages only.",
    )
    arg_parser.add_argument(
        SyntaxArg.arg_v,
        SyntaxArg.arg_verbose,
        action="count",
        dest=SyntaxArg.dest_verbose,
        default=0,
        help="Increase log verbosity level.",
    )
    arg_parser.add_argument(
        SyntaxArg.arg_wizard_stage,
        type=str,
        choices=[wizard_stage.value for wizard_stage in WizardStage],
        default=WizardStage.wizard_started.value,
        help=(
            argparse.SUPPRESS
            if suppress_internal_args
            else f"Used internally: specifies `{WizardStage.__name__}`."
        ),
    )
    arg_parser.add_argument(
        # TODO: Remove this arg - it does not support any strong use case:
        SyntaxArg.arg_final_state,
        type=str,
        # TODO: Decide to print choices or not (they look too excessive). Maybe print those in `TargetState` only?
        # choices=[state_name.name for state_name in EnvState],
        # Keep default `None` to indicate there was no user override (and select the actual default conditionally):
        default=None,
        # TODO: Compute universal sink:
        help=f"Select final `{EnvState.__name__}` name.",
    )
    arg_parser.add_argument(
        SyntaxArg.arg_proto_code_abs_file_path,
        type=str,
        default=None,
        help=(
            argparse.SUPPRESS
            if suppress_internal_args
            else f"Used internally: path to `{ConfConstGeneral.name_proto_code}` identified before `{PythonExecutable.py_exec_venv.name}`."
        ),
    )
    arg_parser.add_argument(
        SyntaxArg.arg_start_id,
        type=str,
        default=get_default_start_id(),
        help=(
            argparse.SUPPRESS
            if suppress_internal_args
            else (
                f"Used internally: specifies `{ValueName.value_start_id}` "
                f"which associates multiple `os.execv` invocations."
            )
        ),
    )
    return arg_parser


# TODO: add test
def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError(f"[{bool.__name__}] value expected.")


class RunStrategy:
    """
    See related:
    *   `RunMode`
    *   FT_11_27_29_83.run_mode.md
    """

    def execute_strategy(
        self,
        state_node: StateNode,
    ) -> None:
        raise NotImplementedError()


class ExitCodeReporter(RunStrategy):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__()
        self.env_ctx: EnvContext = env_ctx

    def execute_strategy(
        self,
        state_node: StateNode,
    ) -> None:
        """
        This is a trivial implementation.

        No special DAG traversal because nodes traverse their own dependencies.
        But it may not reach all nodes because
        dependencies will be conditionally evaluated by the implementation of those nodes.
        """
        # NOTE: The `EnvContext.final_state` must return `int` with this strategy:
        exit_code: int = state_node.eval_own_state()
        assert type(exit_code) is int, "`exit_code` must be an `int`"
        sys.exit(exit_code)


class GraphPrinter(RunStrategy):
    """
    This class prints reduced DAG of `EnvState`-s.

    Full DAG for a target may involve the same dependency/parent multiple times.
    Printing each dependency multiple times (with all its transient dependencies) looks excessive.
    Instead, this class prints each dependency/parent only if any of its siblings have not been printed yet.
    Therefore, there is some duplication, but the result is both more concise and less confusing.
    """

    rendered_no_parents: str = "[none]"

    def __init__(
        self,
        state_graph: StateGraph,
    ):
        super().__init__()
        self.state_graph: StateGraph = state_graph
        self.already_printed: set[str] = set()

    def execute_strategy(
        self,
        state_node: StateNode,
    ) -> None:
        self.print_node_parents(
            state_node,
            force_print=False,
            level=0,
        )

    def print_node_parents(
        self,
        state_node,
        force_print: bool,
        level: int,
    ) -> None:
        if state_node.get_state_name() in self.already_printed and not force_print:
            return
        else:
            self.already_printed.add(state_node.get_state_name())

        # Indented name:
        print(
            f"{' ' * level * 4}{state_node.get_state_name()}",
            end="",
        )
        # Dependencies (parents):
        rendered_parent_states: str
        if len(state_node.get_parent_states()) > 0:
            rendered_parent_states = " ".join(state_node.get_parent_states())
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
        for state_parent in state_node.get_parent_states():
            if state_parent not in self.already_printed:
                any_parent_to_print = True
                break

        # Recurse:
        if any_parent_to_print:
            for state_parent in state_node.get_parent_states():
                self.print_node_parents(
                    self.state_graph.state_nodes[state_parent],
                    # Even if this state was already printed, since we are printing siblings, print them all:
                    force_print=any_parent_to_print,
                    level=level + 1,
                )


class StateNode(Generic[ValueType]):
    """
    All nodes form a `StateGraph`, which must be a DAG.
    """

    def __init__(
        self,
        env_ctx: EnvContext,
        parent_states: list[str],
        state_name: str,
    ):
        self.env_ctx: EnvContext = env_ctx
        self.state_name: str = state_name

        # Ensure no duplicates:
        assert len(parent_states) == len(set(parent_states))

        self.parent_states: list[str] = parent_states

        assert type(state_name) is str

        for state_parent in parent_states:
            assert type(state_parent) is str

    def get_state_name(
        self,
    ) -> str:
        return self.state_name

    def get_parent_states(
        self,
    ) -> list[str]:
        return self.parent_states

    def eval_parent_state(
        self,
        parent_state: str,
    ) -> typing.Any:
        if parent_state not in self.parent_states:
            raise AssertionError(
                f"parent_state[{parent_state}] is not parent of [{self.state_name}]"
            )
        return self.env_ctx.state_graph.eval_state(parent_state)

    def eval_own_state(
        self,
    ) -> ValueType:
        return self._eval_own_state()

    def _eval_own_state(
        self,
    ) -> ValueType:
        raise NotImplementedError()


class AbstractCachingStateNode(StateNode[ValueType]):

    def __init__(
        self,
        env_ctx: EnvContext,
        parent_states: list[str],
        state_name: str,
        auto_boostrap_parents: bool = True,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=parent_states,
            state_name=state_name,
        )
        self.auto_boostrap_parents: bool = auto_boostrap_parents
        self.is_cached: bool = False
        self.cached_value: ValueType | None = None

    def _eval_own_state(
        self,
    ) -> ValueType:
        if not self.is_cached:

            if self.auto_boostrap_parents:
                # Bootstrap all dependencies:
                for state_name in self.parent_states:
                    self.eval_parent_state(state_name)

            # See FT_30_24_95_65.state_idempotency.md
            self.cached_value = self._eval_state_once()
            logger.debug(
                f"state [{self.state_name}] evaluated value [{self.cached_value}]"
            )
            self.is_cached = True

        return self.cached_value

    def _eval_state_once(
        self,
    ) -> ValueType:
        raise NotImplementedError()


# noinspection PyPep8Naming
class Bootstrapper_state_input_stderr_log_level_var_loaded(
    AbstractCachingStateNode[int]
):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[],
            state_name=if_none(
                state_name, EnvState.state_input_stderr_log_level_var_loaded.name
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:
        default_stderr_level: str = os.getenv(
            EnvVar.var_PROTOPRIMER_STDERR_LOG_LEVEL.value,
            ConfConstInput.default_PROTOPRIMER_STDERR_LOG_LEVEL,
        )
        if str.isdigit(default_stderr_level):
            state_input_stderr_log_level_var_loaded: int = int(default_stderr_level)
            assert state_input_stderr_log_level_var_loaded >= 0
        else:
            state_input_stderr_log_level_var_loaded: int = getattr(
                logging,
                default_stderr_level,
            )
        return state_input_stderr_log_level_var_loaded


# noinspection PyPep8Naming
class Bootstrapper_state_input_do_install_var_loaded(AbstractCachingStateNode[bool]):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[],
            state_name=if_none(
                state_name, EnvState.state_input_do_install_var_loaded.name
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:
        state_input_do_install_var_loaded: bool = str2bool(
            os.getenv(
                EnvVar.var_PROTOPRIMER_DO_INSTALL.value,
                ConfConstInput.default_PROTOPRIMER_DO_INSTALL,
            )
        )
        return state_input_do_install_var_loaded


# noinspection PyPep8Naming
class Bootstrapper_state_default_stderr_log_handler_configured(
    AbstractCachingStateNode[logging.Handler]
):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_input_stderr_log_level_var_loaded.name,
            ],
            state_name=if_none(
                state_name, EnvState.state_default_stderr_log_handler_configured.name
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:
        # Make all warnings be captured by the logging subsystem:
        logging.captureWarnings(True)

        state_input_stderr_log_level_var_loaded: int = self.eval_parent_state(
            EnvState.state_input_stderr_log_level_var_loaded.name
        )
        assert state_input_stderr_log_level_var_loaded >= 0

        # Log everything (the filters are supposed to be set on output handlers instead):
        logger.setLevel(logging.NOTSET)

        stderr_handler: logging.Handler = logging.StreamHandler(sys.stderr)
        stderr_handler.addFilter(PythonExecutableFilter())

        stderr_formatter = ColorFormatter()

        stderr_handler.setLevel(state_input_stderr_log_level_var_loaded)
        stderr_handler.setFormatter(stderr_formatter)

        logger.addHandler(stderr_handler)

        return stderr_handler


# noinspection PyPep8Naming
class Bootstrapper_state_args_parsed(AbstractCachingStateNode[argparse.Namespace]):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[],
            state_name=if_none(state_name, EnvState.state_args_parsed.name),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:
        state_args_parsed: argparse.Namespace = init_arg_parser().parse_args()
        return state_args_parsed


# noinspection PyPep8Naming
class Bootstrapper_state_input_wizard_stage_arg_loaded(
    AbstractCachingStateNode[WizardStage]
):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_args_parsed.name,
            ],
            state_name=if_none(
                state_name, EnvState.state_input_wizard_stage_arg_loaded.name
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:
        return WizardStage[
            getattr(
                self.eval_parent_state(EnvState.state_args_parsed.name),
                ParsedArg.name_wizard_stage.value,
            )
        ]


# noinspection PyPep8Naming
class Bootstrapper_state_input_stderr_log_level_eval_finalized(
    AbstractCachingStateNode[int]
):
    """
    There is a narrow window between the default log level is set and this state is evaluated.
    To control the default log level, see `EnvVar.var_PROTOPRIMER_STDERR_LOG_LEVEL`.
    """

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_input_stderr_log_level_var_loaded.name,
                EnvState.state_default_stderr_log_handler_configured.name,
                EnvState.state_args_parsed.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_input_stderr_log_level_eval_finalized.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:

        state_input_stderr_log_level_var_loaded: int = self.eval_parent_state(
            EnvState.state_input_stderr_log_level_var_loaded.name,
        )

        state_default_stderr_logger_configured: logging.Handler = (
            self.eval_parent_state(
                EnvState.state_default_stderr_log_handler_configured.name
            )
        )

        parsed_args = self.eval_parent_state(EnvState.state_args_parsed.name)
        stderr_log_level_silent = getattr(
            parsed_args,
            SyntaxArg.dest_silent,
        )
        stderr_log_level_quiet = getattr(
            parsed_args,
            SyntaxArg.dest_quiet,
        )
        stderr_log_level_verbose = getattr(
            parsed_args,
            SyntaxArg.dest_verbose,
        )

        stderr_log_level_eval_finalized: int = state_input_stderr_log_level_var_loaded
        if stderr_log_level_silent:
            # almost disable logs:
            stderr_log_level_eval_finalized = logging.CRITICAL + 1
        elif stderr_log_level_quiet:
            stderr_log_level_eval_finalized = logging.ERROR
        elif stderr_log_level_verbose:
            if stderr_log_level_verbose >= 2:
                stderr_log_level_eval_finalized = logging.NOTSET
            elif stderr_log_level_verbose == 1:
                stderr_log_level_eval_finalized = logging.DEBUG

        state_default_stderr_logger_configured.setLevel(stderr_log_level_eval_finalized)

        # Set default log level for subsequent invocations:
        level_var_value = logging.getLevelName(stderr_log_level_eval_finalized)
        if isinstance(level_var_value, str):
            if " " in level_var_value:
                # Due to some hacks in the `python` `logging` library,
                # it may return non-existing level names - use number instead:
                level_var_value = str(stderr_log_level_eval_finalized)
        os.environ[EnvVar.var_PROTOPRIMER_STDERR_LOG_LEVEL.value] = level_var_value

        return stderr_log_level_eval_finalized


# noinspection PyPep8Naming
class Bootstrapper_state_input_run_mode_arg_loaded(AbstractCachingStateNode[RunMode]):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_args_parsed.name,
            ],
            state_name=if_none(
                state_name, EnvState.state_input_run_mode_arg_loaded.name
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:
        state_args_parsed: argparse.Namespace = self.eval_parent_state(
            EnvState.state_args_parsed.name
        )
        state_input_run_mode_arg_loaded: RunMode = RunMode(
            getattr(
                state_args_parsed,
                ParsedArg.name_run_mode.value,
            )
        )
        return state_input_run_mode_arg_loaded


# noinspection PyPep8Naming
class Bootstrapper_state_input_final_state_eval_finalized(
    AbstractCachingStateNode[str]
):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_args_parsed.name,
            ],
            state_name=if_none(
                state_name, EnvState.state_input_final_state_eval_finalized.name
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:
        state_args_parsed = self.eval_parent_state(EnvState.state_args_parsed.name)
        state_input_final_state_eval_finalized = getattr(
            state_args_parsed,
            ParsedArg.name_final_state.value,
        )

        if state_input_final_state_eval_finalized is None:
            # TODO: Fix duplicated logs: try default bootstrap - this line is printed repeatedly.
            #       Pass the arg after the start to subsequent `switch_python` calls.
            logger.info(
                f"selecting `final_state`[{self.env_ctx.final_state}] as no `{SyntaxArg.arg_final_state}` specified"
            )
            state_input_final_state_eval_finalized = self.env_ctx.final_state

        return state_input_final_state_eval_finalized


# noinspection PyPep8Naming
class Bootstrapper_state_run_mode_executed(AbstractCachingStateNode[bool]):
    """
    This is a special node - it traverses ALL nodes.

    BUT: It does not depend on ALL nodes - instead, it uses a run mode strategy implementation.
    """

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_input_stderr_log_level_eval_finalized.name,
                EnvState.state_input_final_state_eval_finalized.name,
                EnvState.state_input_run_mode_arg_loaded.name,
            ],
            state_name=if_none(state_name, EnvState.state_run_mode_executed.name),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:

        state_input_stderr_log_level_eval_finalized = self.eval_parent_state(
            EnvState.state_input_stderr_log_level_eval_finalized.name
        )
        assert state_input_stderr_log_level_eval_finalized >= 0

        state_input_final_state_eval_finalized: str = self.eval_parent_state(
            EnvState.state_input_final_state_eval_finalized.name
        )

        state_input_run_mode_arg_loaded: RunMode = self.eval_parent_state(
            EnvState.state_input_run_mode_arg_loaded.name
        )

        state_node: StateNode = self.env_ctx.state_graph.state_nodes[
            state_input_final_state_eval_finalized
        ]

        selected_strategy: RunStrategy
        if state_input_run_mode_arg_loaded is None:
            raise ValueError(f"run mode is not defined")
        elif state_input_run_mode_arg_loaded == RunMode.mode_graph:
            selected_strategy = GraphPrinter(self.env_ctx.state_graph)
        elif state_input_run_mode_arg_loaded == RunMode.mode_prime:
            selected_strategy = ExitCodeReporter(self.env_ctx)
        elif state_input_run_mode_arg_loaded == RunMode.mode_wizard:
            for wizard_state in WizardState:
                self.env_ctx.state_graph.register_node(
                    wizard_state.value(self.env_ctx),
                    replace_existing=True,
                )
            selected_strategy = ExitCodeReporter(self.env_ctx)
        else:
            raise ValueError(
                f"cannot handle run mode [{state_input_run_mode_arg_loaded}]"
            )

        selected_strategy.execute_strategy(state_node)

        return True


# noinspection PyPep8Naming
class Bootstrapper_state_input_py_exec_var_loaded(
    AbstractCachingStateNode[PythonExecutable]
):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_args_parsed.name,
            ],
            state_name=if_none(
                state_name, EnvState.state_input_py_exec_var_loaded.name
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:
        return PythonExecutable[
            os.getenv(
                EnvVar.var_PROTOPRIMER_PY_EXEC.value,
                ConfConstInput.default_PROTOPRIMER_PY_EXEC,
            )
        ]


# noinspection PyPep8Naming
class Bootstrapper_state_py_exec_arbitrary_reached(
    AbstractCachingStateNode[PythonExecutable]
):
    """
    Implements UC_90_98_17_93.run_under_venv.md.
    """

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_input_py_exec_var_loaded.name,
                EnvState.state_args_parsed.name,
                EnvState.state_input_wizard_stage_arg_loaded.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_py_exec_arbitrary_reached.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:
        state_input_py_exec_var_loaded: PythonExecutable = self.eval_parent_state(
            EnvState.state_input_py_exec_var_loaded.name
        )

        state_args_parsed: argparse.Namespace = self.eval_parent_state(
            EnvState.state_args_parsed.name
        )

        start_id: str = getattr(
            state_args_parsed,
            ParsedArg.name_start_id.value,
        )

        if (
            state_input_py_exec_var_loaded.value
            == PythonExecutable.py_exec_unknown.value
        ):
            log_python_context(logging.DEBUG)

            # UC_90_98_17_93.run_under_venv.md
            # Switch out of the current `venv` -
            # it might be a wrong one,
            # and even if it is the right one,
            # child states require out of `venv` execution.

            cleaned_env = os.environ.copy()

            orig_venv_abs_path = cleaned_env.pop(
                ConfConstInput.ext_env_var_VIRTUAL_ENV, None
            )
            orig_PYTHONPATH_value = cleaned_env.pop(
                ConfConstInput.ext_env_var_PYTHONPATH, None
            )
            orig_PATH_value: str = cleaned_env.get(ConfConstInput.ext_env_var_PATH, "")

            if orig_venv_abs_path is not None:
                # Remove `venv/bin` dir from the `PATH` env var:
                venv_bin_abs_path: str = os.path.join(orig_venv_abs_path, "bin")
                PATH_parts: list[str] = orig_PATH_value.split(os.pathsep)
                cleaned_path_parts = [p for p in PATH_parts if p != venv_bin_abs_path]
                cleaned_env[ConfConstInput.ext_env_var_PATH] = os.pathsep.join(
                    cleaned_path_parts
                )

            path_to_curr_python = get_path_to_curr_python()
            path_to_next_python = get_path_to_base_python()
            switch_python(
                curr_py_exec=state_input_py_exec_var_loaded,
                curr_python_path=path_to_curr_python,
                next_py_exec=PythonExecutable.py_exec_arbitrary,
                next_python_path=path_to_next_python,
                start_id=start_id,
                proto_code_abs_file_path=None,
                wizard_stage=self.env_ctx.mutable_state_input_wizard_stage_arg_loaded.get_curr_value(
                    self,
                ),
                required_environ=cleaned_env,
            )

        return state_input_py_exec_var_loaded


# noinspection PyPep8Naming
class Bootstrapper_state_input_proto_code_file_abs_path_eval_finalized(
    AbstractCachingStateNode[str]
):
    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_py_exec_arbitrary_reached.name,
                EnvState.state_args_parsed.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_input_proto_code_file_abs_path_eval_finalized.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:

        state_py_exec_arbitrary_reached: PythonExecutable = self.eval_parent_state(
            EnvState.state_py_exec_arbitrary_reached.name
        )

        state_args_parsed: argparse.Namespace = self.eval_parent_state(
            EnvState.state_args_parsed.name
        )

        state_input_proto_code_file_abs_path_eval_finalized: str
        if state_py_exec_arbitrary_reached.value >= PythonExecutable.py_exec_venv.value:
            arg_proto_code_abs_file_path = getattr(
                state_args_parsed,
                ParsedArg.name_proto_code.value,
            )
            if arg_proto_code_abs_file_path is None:
                raise AssertionError(
                    f"`{SyntaxArg.arg_proto_code_abs_file_path}` is not specified at `{EnvState.state_py_exec_arbitrary_reached.name}` [{state_py_exec_arbitrary_reached}]"
                )
            # rely on the path given in args:
            state_input_proto_code_file_abs_path_eval_finalized = (
                arg_proto_code_abs_file_path
            )
        else:
            assert not is_venv()
            warn_if_non_venv_package_installed()
            state_input_proto_code_file_abs_path_eval_finalized = os.path.abspath(
                __file__
            )

        assert os.path.isabs(state_input_proto_code_file_abs_path_eval_finalized)
        return state_input_proto_code_file_abs_path_eval_finalized


# noinspection PyPep8Naming
class Bootstrapper_state_input_proto_code_dir_abs_path_eval_finalized(
    AbstractCachingStateNode[str]
):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_input_proto_code_file_abs_path_eval_finalized.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_input_proto_code_dir_abs_path_eval_finalized.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:

        state_input_proto_code_file_abs_path_eval_finalized = self.eval_parent_state(
            EnvState.state_input_proto_code_file_abs_path_eval_finalized.name
        )
        state_input_proto_code_dir_abs_path_eval_finalized = os.path.dirname(
            state_input_proto_code_file_abs_path_eval_finalized
        )

        assert os.path.isabs(state_input_proto_code_dir_abs_path_eval_finalized)
        return state_input_proto_code_dir_abs_path_eval_finalized


# noinspection PyPep8Naming
class Bootstrapper_state_input_proto_conf_primer_file_abs_path_eval_finalized(
    AbstractCachingStateNode[str]
):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_input_proto_code_dir_abs_path_eval_finalized.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_input_proto_conf_primer_file_abs_path_eval_finalized.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:
        state_input_proto_code_dir_abs_path_eval_finalized = self.eval_parent_state(
            EnvState.state_input_proto_code_dir_abs_path_eval_finalized.name
        )

        # TODO: be able to configure path:
        return os.path.join(
            state_input_proto_code_dir_abs_path_eval_finalized,
            ConfConstInput.default_file_basename_conf_primer,
        )


# noinspection PyPep8Naming
class Bootstrapper_state_proto_conf_file_data(AbstractCachingStateNode[dict]):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_input_proto_conf_primer_file_abs_path_eval_finalized.name,
            ],
            state_name=if_none(state_name, EnvState.state_proto_conf_file_data.name),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:
        state_input_proto_conf_primer_file_abs_path_eval_finalized = (
            self.eval_parent_state(
                EnvState.state_input_proto_conf_primer_file_abs_path_eval_finalized.name
            )
        )

        file_data: dict
        if os.path.exists(state_input_proto_conf_primer_file_abs_path_eval_finalized):
            file_data = read_json_file(
                state_input_proto_conf_primer_file_abs_path_eval_finalized
            )
        else:
            raise AssertionError(
                error_on_missing_conf_file(
                    state_input_proto_conf_primer_file_abs_path_eval_finalized
                )
            )
        verify_conf_file_data(
            state_input_proto_conf_primer_file_abs_path_eval_finalized,
            file_data,
            ConfLeap.leap_primer,
        )
        return file_data


# noinspection PyPep8Naming
class Wizard_state_proto_conf_file_data(AbstractCachingStateNode[dict]):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        self.moved_state_name = rename_to_moved_state_name(
            EnvState.state_proto_conf_file_data.name
        )
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_input_wizard_stage_arg_loaded.name,
                EnvState.state_input_proto_conf_primer_file_abs_path_eval_finalized.name,
                EnvState.state_input_proto_code_dir_abs_path_eval_finalized.name,
                # UC_27_40_17_59.replace_by_new_and_use_old.md:
                # Depend on the moved state:
                self.moved_state_name,
            ],
            state_name=if_none(state_name, EnvState.state_proto_conf_file_data.name),
            # Bootstrap manually to avoid touching `moved_state_node`:
            auto_boostrap_parents=False,
        )

        # UC_27_40_17_59.replace_by_new_and_use_old.md:
        # Register the moved state implementation:
        self.moved_state_node = Bootstrapper_state_proto_conf_file_data(
            env_ctx,
            self.moved_state_name,
        )
        self.env_ctx.state_graph.register_node(self.moved_state_node)

    def _eval_state_once(
        self,
    ) -> ValueType:

        state_input_proto_conf_primer_file_abs_path_eval_finalized = (
            self.eval_parent_state(
                EnvState.state_input_proto_conf_primer_file_abs_path_eval_finalized.name
            )
        )

        file_data = wizard_conf_file(
            self,
            ConfLeap.leap_primer,
            state_input_proto_conf_primer_file_abs_path_eval_finalized,
            default_file_data={
                ConfField.field_primer_ref_root_dir_rel_path.value: ".",
                ConfField.field_primer_conf_client_file_rel_path.value: ConfConstPrimer.default_client_conf_file_rel_path,
            },
        )

        return file_data


# noinspection PyPep8Naming
class Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized(
    AbstractCachingStateNode[str]
):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_proto_conf_file_data.name,
                EnvState.state_input_proto_code_dir_abs_path_eval_finalized.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_primer_ref_root_dir_abs_path_eval_finalized.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:
        state_proto_conf_file_data = self.eval_parent_state(
            EnvState.state_proto_conf_file_data.name
        )

        field_client_dir_rel_path = state_proto_conf_file_data[
            ConfField.field_primer_ref_root_dir_rel_path.value
        ]

        state_input_proto_code_dir_abs_path_eval_finalized = self.eval_parent_state(
            EnvState.state_input_proto_code_dir_abs_path_eval_finalized.name
        )

        state_primer_ref_root_dir_abs_path_eval_finalized = os.path.join(
            state_input_proto_code_dir_abs_path_eval_finalized,
            field_client_dir_rel_path,
        )

        state_primer_ref_root_dir_abs_path_eval_finalized = os.path.normpath(
            state_primer_ref_root_dir_abs_path_eval_finalized
        )

        assert os.path.isabs(state_primer_ref_root_dir_abs_path_eval_finalized)
        return state_primer_ref_root_dir_abs_path_eval_finalized


# noinspection PyPep8Naming
class Bootstrapper_state_primer_conf_client_file_abs_path_eval_finalized(
    AbstractCachingStateNode[str]
):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_primer_ref_root_dir_abs_path_eval_finalized.name,
                EnvState.state_proto_conf_file_data.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_primer_conf_client_file_abs_path_eval_finalized.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:
        state_primer_ref_root_dir_abs_path_eval_finalized = self.eval_parent_state(
            EnvState.state_primer_ref_root_dir_abs_path_eval_finalized.name
        )

        state_proto_conf_file_data = self.eval_parent_state(
            EnvState.state_proto_conf_file_data.name
        )

        field_client_config_rel_path = state_proto_conf_file_data[
            ConfField.field_primer_conf_client_file_rel_path.value
        ]

        state_primer_conf_client_file_abs_path_eval_finalized = os.path.join(
            state_primer_ref_root_dir_abs_path_eval_finalized,
            field_client_config_rel_path,
        )

        return state_primer_conf_client_file_abs_path_eval_finalized


# noinspection PyPep8Naming
class Bootstrapper_state_client_conf_file_data(AbstractCachingStateNode[dict]):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_primer_conf_client_file_abs_path_eval_finalized.name,
            ],
            state_name=if_none(state_name, EnvState.state_client_conf_file_data.name),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:

        state_primer_conf_client_file_abs_path_eval_finalized = self.eval_parent_state(
            EnvState.state_primer_conf_client_file_abs_path_eval_finalized.name
        )
        if os.path.exists(state_primer_conf_client_file_abs_path_eval_finalized):
            file_data = read_json_file(
                state_primer_conf_client_file_abs_path_eval_finalized
            )
        else:
            raise AssertionError(
                error_on_missing_conf_file(
                    state_primer_conf_client_file_abs_path_eval_finalized
                )
            )
        verify_conf_file_data(
            state_primer_conf_client_file_abs_path_eval_finalized,
            file_data,
            ConfLeap.leap_client,
        )
        return file_data


# noinspection PyPep8Naming
class Wizard_state_client_conf_file_data(AbstractCachingStateNode[dict]):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        self.moved_state_name = rename_to_moved_state_name(
            EnvState.state_client_conf_file_data.name
        )
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_input_wizard_stage_arg_loaded.name,
                EnvState.state_primer_conf_client_file_abs_path_eval_finalized.name,
                # UC_27_40_17_59.replace_by_new_and_use_old.md:
                # Depend on the moved state:
                self.moved_state_name,
            ],
            state_name=if_none(state_name, EnvState.state_client_conf_file_data.name),
            # Bootstrap manually to avoid touching `moved_state_node`:
            auto_boostrap_parents=False,
        )

        # UC_27_40_17_59.replace_by_new_and_use_old.md:
        # Register the moved state implementation:
        self.moved_state_node = Bootstrapper_state_client_conf_file_data(
            env_ctx,
            self.moved_state_name,
        )
        self.env_ctx.state_graph.register_node(self.moved_state_node)

    def _eval_state_once(
        self,
    ) -> ValueType:

        state_primer_conf_client_file_abs_path_eval_finalized = self.eval_parent_state(
            EnvState.state_primer_conf_client_file_abs_path_eval_finalized.name
        )

        file_data = wizard_conf_file(
            self,
            ConfLeap.leap_client,
            state_primer_conf_client_file_abs_path_eval_finalized,
            default_file_data={
                # TODO: Decide how to support (or avoid) evaluation of value if it does not exist.
                #       Maybe support few actions: check_if_exists and bootstrap_if_does_not_exists?
                #       Using default when value is missing in data does not work here.
                ConfField.field_client_link_name_dir_rel_path.value: ConfConstClient.default_dir_rel_path_leap_env_link_name,
                # TODO: This should not be part of the file - defaults should be configured, not generated (or generated by extensible code):
                # TODO: Prompt use in wizard and validate the value refers to an existing directory:
                ConfField.field_client_default_env_dir_rel_path.value: ConfConstClient.default_client_default_env_dir_rel_path,
            },
        )

        return file_data


# noinspection PyPep8Naming
class Bootstrapper_state_client_local_env_dir_rel_path_eval_finalized(
    AbstractCachingStateNode[str]
):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_client_conf_file_data.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_client_local_env_dir_rel_path_eval_finalized.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:
        state_client_conf_file_data: dict = self.eval_parent_state(
            EnvState.state_client_conf_file_data.name
        )
        state_client_local_env_dir_rel_path_eval_finalized = (
            state_client_conf_file_data.get(
                ConfField.field_client_default_env_dir_rel_path.value,
            )
        )
        if state_client_local_env_dir_rel_path_eval_finalized is None:
            raise AssertionError(
                f"Field `{ConfField.field_client_default_env_dir_rel_path.value}` is [{state_client_local_env_dir_rel_path_eval_finalized}] - re-run with [{SyntaxArg.arg_mode_wizard}] to set it."
            )
        """
        Raises exception if the target path of the `@/conf/` symlink is not allowed.

        NOTE:
        At the moment, only target paths under `client_dir` (under `@/`) are allowed.
        This is not a strict requirement and can be relaxed in the future.
        """
        if os.path.isabs(state_client_local_env_dir_rel_path_eval_finalized):
            raise AssertionError(
                f"Target for `@/conf/` symlink [{state_client_local_env_dir_rel_path_eval_finalized}] must not be absolute path."
            )
        elif (
            ".."
            in pathlib.Path(state_client_local_env_dir_rel_path_eval_finalized).parts
        ):
            raise AssertionError(
                f"Target for `@/conf/` symlink [{state_client_local_env_dir_rel_path_eval_finalized}] must not contain `..` path segments."
            )
        elif not os.path.isdir(state_client_local_env_dir_rel_path_eval_finalized):
            # TODO: This has to be fixed as the rel path is tested against curr dir as base, but must be tested against client ref root:
            raise AssertionError(
                f"Target for `@/conf/` symlink [{state_client_local_env_dir_rel_path_eval_finalized}] must lead to a directory."
            )
        return os.path.normpath(state_client_local_env_dir_rel_path_eval_finalized)


# noinspection PyPep8Naming
class Bootstrapper_state_client_conf_env_dir_abs_path_eval_finalized(
    AbstractCachingStateNode[str]
):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_primer_ref_root_dir_abs_path_eval_finalized.name,
                EnvState.state_client_conf_file_data.name,
                EnvState.state_client_local_env_dir_rel_path_eval_finalized.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_client_conf_env_dir_abs_path_eval_finalized.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:
        file_data: dict = self.eval_parent_state(
            EnvState.state_client_conf_file_data.name
        )

        env_conf_dir_rel_path = file_data.get(
            ConfField.field_client_link_name_dir_rel_path.value,
            ConfConstClient.default_dir_rel_path_leap_env_link_name,
        )

        assert not os.path.isabs(env_conf_dir_rel_path)

        state_primer_ref_root_dir_abs_path_eval_finalized = self.eval_parent_state(
            EnvState.state_primer_ref_root_dir_abs_path_eval_finalized.name
        )

        # Convert to absolute:
        state_client_conf_env_dir_abs_path_eval_finalized = os.path.join(
            self.eval_parent_state(
                EnvState.state_primer_ref_root_dir_abs_path_eval_finalized.name
            ),
            env_conf_dir_rel_path,
        )

        state_client_local_env_dir_rel_path_eval_finalized = self.eval_parent_state(
            EnvState.state_client_local_env_dir_rel_path_eval_finalized.name
        )
        assert state_client_local_env_dir_rel_path_eval_finalized is not None

        if os.path.exists(state_client_conf_env_dir_abs_path_eval_finalized):
            if os.path.islink(state_client_conf_env_dir_abs_path_eval_finalized):
                if os.path.isdir(state_client_conf_env_dir_abs_path_eval_finalized):
                    if state_client_local_env_dir_rel_path_eval_finalized is None:
                        # TODO: Can we make it mandatory?
                        #       In cases when there is no env-specifics,
                        #       it can point to ref root (and entire link can be avoided if name is blank)?
                        # not configured or not specified => not required by user => nothing to do:
                        pass
                    else:
                        # Compare the existing link target and the configured one:
                        conf_dir_path = os.path.normpath(
                            os.readlink(
                                state_client_conf_env_dir_abs_path_eval_finalized
                            )
                        )

                        if (
                            state_client_local_env_dir_rel_path_eval_finalized
                            != conf_dir_path
                        ):
                            raise AssertionError(
                                f"The `@/conf/` target [{conf_dir_path}] is not the same as the provided target [{state_client_local_env_dir_rel_path_eval_finalized}]."
                            )
                else:
                    raise AssertionError(
                        f"The `@/conf/` [{state_client_conf_env_dir_abs_path_eval_finalized}] target is not a directory.",
                    )
            else:
                raise AssertionError(
                    f"The `@/conf/` [{state_client_conf_env_dir_abs_path_eval_finalized}] is not a symlink.",
                )
        else:
            os.symlink(
                os.path.normpath(state_client_local_env_dir_rel_path_eval_finalized),
                state_client_conf_env_dir_abs_path_eval_finalized,
            )

        return state_client_conf_env_dir_abs_path_eval_finalized


# noinspection PyPep8Naming
class Bootstrapper_state_client_link_name_dir_rel_path_eval_finalized(
    AbstractCachingStateNode[str]
):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_client_conf_file_data.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_client_link_name_dir_rel_path_eval_finalized.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:
        state_client_conf_file_data: dict = self.eval_parent_state(
            EnvState.state_client_conf_file_data.name
        )
        state_client_link_name_dir_rel_path_eval_finalized = (
            state_client_conf_file_data.get(
                ConfField.field_client_link_name_dir_rel_path.value,
            )
        )
        if state_client_link_name_dir_rel_path_eval_finalized is None:
            raise AssertionError(
                f"Field `{ConfField.field_client_link_name_dir_rel_path.value}` is [{state_client_link_name_dir_rel_path_eval_finalized}] - re-run with [{SyntaxArg.arg_mode_wizard}] to set it."
            )
        return state_client_link_name_dir_rel_path_eval_finalized


# noinspection PyPep8Naming
class Bootstrapper_state_client_conf_env_file_abs_path_eval_finalized(
    AbstractCachingStateNode[str]
):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_primer_ref_root_dir_abs_path_eval_finalized.name,
                EnvState.state_client_conf_env_dir_abs_path_eval_finalized.name,
                EnvState.state_client_link_name_dir_rel_path_eval_finalized.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_client_conf_env_file_abs_path_eval_finalized.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:

        state_primer_ref_root_dir_abs_path_eval_finalized = self.eval_parent_state(
            EnvState.state_primer_ref_root_dir_abs_path_eval_finalized.name
        )

        state_client_link_name_dir_rel_path_eval_finalized = self.eval_parent_state(
            EnvState.state_client_link_name_dir_rel_path_eval_finalized.name
        )

        state_client_conf_env_file_abs_path_eval_finalized = os.path.join(
            state_primer_ref_root_dir_abs_path_eval_finalized,
            state_client_link_name_dir_rel_path_eval_finalized,
            # TODO: Do not use default values directly - resolve it differently at the prev|next step based on the need:
            ConfConstClient.default_file_basename_leap_env,
        )
        state_client_conf_env_dir_abs_path_eval_finalized = self.eval_parent_state(
            EnvState.state_client_conf_env_dir_abs_path_eval_finalized.name
        )
        if not is_sub_path(
            state_client_conf_env_file_abs_path_eval_finalized,
            state_client_conf_env_dir_abs_path_eval_finalized,
        ):
            raise AssertionError(
                f"The config file path [{state_client_conf_env_file_abs_path_eval_finalized}] is not under the config dir path [{state_client_conf_env_dir_abs_path_eval_finalized}].",
            )
        return state_client_conf_env_file_abs_path_eval_finalized


# noinspection PyPep8Naming
class Bootstrapper_state_env_conf_file_data(AbstractCachingStateNode[dict]):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_client_conf_env_file_abs_path_eval_finalized.name,
            ],
            state_name=if_none(state_name, EnvState.state_env_conf_file_data.name),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:
        state_client_conf_env_file_abs_path_eval_finalized = self.eval_parent_state(
            EnvState.state_client_conf_env_file_abs_path_eval_finalized.name
        )
        file_data: dict
        if os.path.exists(state_client_conf_env_file_abs_path_eval_finalized):
            file_data = read_json_file(
                state_client_conf_env_file_abs_path_eval_finalized
            )
        else:
            raise AssertionError(
                error_on_missing_conf_file(
                    state_client_conf_env_file_abs_path_eval_finalized
                )
            )
        verify_conf_file_data(
            state_client_conf_env_file_abs_path_eval_finalized,
            file_data,
            ConfLeap.leap_env,
        )
        return file_data


# noinspection PyPep8Naming
class Wizard_state_env_conf_file_data(AbstractCachingStateNode[dict]):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        self.moved_state_name = rename_to_moved_state_name(
            EnvState.state_env_conf_file_data.name
        )
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_input_wizard_stage_arg_loaded.name,
                EnvState.state_client_conf_env_file_abs_path_eval_finalized.name,
                # UC_27_40_17_59.replace_by_new_and_use_old.md:
                # Depend on the moved state:
                self.moved_state_name,
            ],
            state_name=if_none(state_name, EnvState.state_env_conf_file_data.name),
            # Bootstrap manually to avoid touching `moved_state_node`:
            auto_boostrap_parents=False,
        )

        # UC_27_40_17_59.replace_by_new_and_use_old.md:
        # Register the moved state implementation:
        self.moved_state_node = Bootstrapper_state_env_conf_file_data(
            env_ctx,
            self.moved_state_name,
        )
        self.env_ctx.state_graph.register_node(self.moved_state_node)

    def _eval_state_once(
        self,
    ) -> ValueType:

        state_client_conf_env_file_abs_path_eval_finalized = self.eval_parent_state(
            EnvState.state_client_conf_env_file_abs_path_eval_finalized.name
        )

        # TODO: This creates a directory with `ConfConstClient.default_dir_rel_path_leap_env_link_name` instead of symlink.
        #       But this happens only if dependency
        #       `state_client_conf_env_file_abs_path_eval_finalized` -> `state_client_conf_env_dir_abs_path_eval_verified`
        #       was not executed (which is not possible outside of tests).
        file_data = wizard_conf_file(
            self,
            ConfLeap.leap_env,
            state_client_conf_env_file_abs_path_eval_finalized,
            default_file_data={
                # TODO: Do not use default values directly - resolve it differently at the prev|next step based on the need:
                ConfField.field_env_local_python_file_abs_path.value: ConfConstEnv.default_file_abs_path_python,
                # TODO: Do not use default values directly - resolve it differently at the prev|next step based on the need:
                ConfField.field_env_local_venv_dir_rel_path.value: ConfConstEnv.default_dir_rel_path_venv,
                ConfField.field_env_local_log_dir_rel_path.value: ConfConstEnv.default_dir_rel_path_log,
                ConfField.field_env_local_tmp_dir_rel_path.value: ConfConstEnv.default_dir_rel_path_tmp,
                ConfField.field_env_project_descriptors.value: ConfConstEnv.default_project_descriptors,
            },
        )

        # Finish the wizard because this is the final wizard state:
        self.env_ctx.mutable_state_input_wizard_stage_arg_loaded.set_curr_value(
            self, WizardStage.wizard_finished
        )

        return file_data


# noinspection PyPep8Naming
class Bootstrapper_state_env_local_python_file_abs_path_eval_finalized(
    AbstractCachingStateNode[str]
):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_env_conf_file_data.name,
                EnvState.state_primer_ref_root_dir_abs_path_eval_finalized.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_env_local_python_file_abs_path_eval_finalized.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:
        state_env_conf_file_data: dict = self.eval_parent_state(
            EnvState.state_env_conf_file_data.name
        )

        state_env_local_python_file_abs_path_eval_finalized = state_env_conf_file_data.get(
            ConfField.field_env_local_python_file_abs_path.value,
            # TODO: Do not use default values directly - resolve it differently at the prev|next step based on the need:
            ConfConstEnv.default_file_abs_path_python,
        )

        if not os.path.isabs(state_env_local_python_file_abs_path_eval_finalized):
            # TODO: Really? Do we really want to allow specifying `python` using rel path?
            #       Regardless, even if rel path, the `field_env_local_python_file_abs_path.value` should remove `abs` from the name then.
            state_env_local_python_file_abs_path_eval_finalized = os.path.join(
                self.eval_parent_state(
                    EnvState.state_primer_ref_root_dir_abs_path_eval_finalized.name
                ),
                state_env_local_python_file_abs_path_eval_finalized,
            )

        return state_env_local_python_file_abs_path_eval_finalized


# noinspection PyPep8Naming
class Bootstrapper_state_env_local_venv_dir_abs_path_eval_finalized(
    AbstractCachingStateNode[str]
):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_env_conf_file_data.name,
                EnvState.state_primer_ref_root_dir_abs_path_eval_finalized.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_env_local_venv_dir_abs_path_eval_finalized.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:
        state_env_conf_file_data: dict = self.eval_parent_state(
            EnvState.state_env_conf_file_data.name
        )

        state_env_local_venv_dir_abs_path_eval_finalized = state_env_conf_file_data.get(
            ConfField.field_env_local_venv_dir_rel_path.value,
            # TODO: Do not use default values directly - resolve it differently at the prev|next step based on the need:
            ConfConstEnv.default_dir_rel_path_venv,
        )

        if not os.path.isabs(state_env_local_venv_dir_abs_path_eval_finalized):
            state_primer_ref_root_dir_abs_path_eval_finalized = self.eval_parent_state(
                EnvState.state_primer_ref_root_dir_abs_path_eval_finalized.name
            )
            state_env_local_venv_dir_abs_path_eval_finalized = os.path.join(
                state_primer_ref_root_dir_abs_path_eval_finalized,
                state_env_local_venv_dir_abs_path_eval_finalized,
            )

        assert os.path.isabs(state_env_local_venv_dir_abs_path_eval_finalized)
        return state_env_local_venv_dir_abs_path_eval_finalized


# noinspection PyPep8Naming
class Bootstrapper_state_env_local_log_dir_abs_path_eval_finalized(
    AbstractCachingStateNode[str]
):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_env_conf_file_data.name,
                EnvState.state_primer_ref_root_dir_abs_path_eval_finalized.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_env_local_log_dir_abs_path_eval_finalized.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:
        state_env_conf_file_data: dict = self.eval_parent_state(
            EnvState.state_env_conf_file_data.name
        )

        field_env_local_log_dir_rel_path = state_env_conf_file_data.get(
            ConfField.field_env_local_log_dir_rel_path.value,
            ConfConstEnv.default_dir_rel_path_log,
        )

        state_primer_ref_root_dir_abs_path_eval_finalized: str = self.eval_parent_state(
            EnvState.state_primer_ref_root_dir_abs_path_eval_finalized.name
        )

        state_env_local_log_dir_abs_path_eval_finalized = os.path.join(
            state_primer_ref_root_dir_abs_path_eval_finalized,
            field_env_local_log_dir_rel_path,
        )
        state_env_local_log_dir_abs_path_eval_finalized = os.path.normpath(
            state_env_local_log_dir_abs_path_eval_finalized
        )

        assert os.path.isabs(state_env_local_log_dir_abs_path_eval_finalized)
        return state_env_local_log_dir_abs_path_eval_finalized


# noinspection PyPep8Naming
class Bootstrapper_state_env_local_tmp_dir_abs_path_eval_finalized(
    AbstractCachingStateNode[str]
):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_env_conf_file_data.name,
                EnvState.state_primer_ref_root_dir_abs_path_eval_finalized.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_env_local_tmp_dir_abs_path_eval_finalized.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:
        state_env_conf_file_data: dict = self.eval_parent_state(
            EnvState.state_env_conf_file_data.name
        )

        field_env_local_tmp_dir_rel_path = state_env_conf_file_data.get(
            ConfField.field_env_local_tmp_dir_rel_path.value,
            ConfConstEnv.default_dir_rel_path_tmp,
        )

        state_primer_ref_root_dir_abs_path_eval_finalized: str = self.eval_parent_state(
            EnvState.state_primer_ref_root_dir_abs_path_eval_finalized.name
        )

        state_env_local_tmp_dir_abs_path_eval_finalized = os.path.join(
            state_primer_ref_root_dir_abs_path_eval_finalized,
            field_env_local_tmp_dir_rel_path,
        )
        state_env_local_tmp_dir_abs_path_eval_finalized = os.path.normpath(
            state_env_local_tmp_dir_abs_path_eval_finalized
        )

        assert os.path.isabs(state_env_local_tmp_dir_abs_path_eval_finalized)
        return state_env_local_tmp_dir_abs_path_eval_finalized


# noinspection PyPep8Naming
class Bootstrapper_state_env_project_descriptors_eval_finalized(
    AbstractCachingStateNode[list]
):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_env_conf_file_data.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_env_project_descriptors_eval_finalized.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:
        state_env_conf_file_data: dict = self.eval_parent_state(
            EnvState.state_env_conf_file_data.name
        )

        project_descriptors: list[dict] = state_env_conf_file_data.get(
            ConfField.field_env_project_descriptors.value,
            ConfConstEnv.default_project_descriptors,
        )

        return project_descriptors


# noinspection PyPep8Naming
class Bootstrapper_state_default_file_log_handler_configured(
    AbstractCachingStateNode[logging.Handler]
):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_args_parsed.name,
                EnvState.state_env_local_log_dir_abs_path_eval_finalized.name,
                EnvState.state_input_stderr_log_level_eval_finalized.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_default_file_log_handler_configured.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:

        state_args_parsed: argparse.Namespace = self.eval_parent_state(
            EnvState.state_args_parsed.name
        )

        start_id: str = getattr(
            state_args_parsed,
            ParsedArg.name_start_id.value,
        )

        state_env_local_log_dir_abs_path_eval_finalized: str = self.eval_parent_state(
            EnvState.state_env_local_log_dir_abs_path_eval_finalized.name
        )

        state_input_stderr_log_level_eval_finalized: int = self.eval_parent_state(
            EnvState.state_input_stderr_log_level_eval_finalized.name
        )

        script_path = sys.argv[0]
        script_name = os.path.basename(script_path)

        file_log_name = f"{script_name}.{start_id}.log"
        # TODO: Configure MAX file log level in the config file (NOTE: the higher the level the fewer the log entries):
        file_log_level: int = logging.INFO
        # Increase the log level at most to what is used by stderr:
        if state_input_stderr_log_level_eval_finalized < file_log_level:
            file_log_level = state_input_stderr_log_level_eval_finalized

        log_file_abs_path = os.path.join(
            state_env_local_log_dir_abs_path_eval_finalized,
            file_log_name,
        )

        os.makedirs(state_env_local_log_dir_abs_path_eval_finalized, exist_ok=True)

        file_handler: logging.Handler = logging.FileHandler(log_file_abs_path)
        file_handler.addFilter(PythonExecutableFilter())

        file_formatter = RegularFormatter()

        file_handler.setLevel(file_log_level)
        file_handler.setFormatter(file_formatter)

        logger.addHandler(file_handler)

        return file_handler


# noinspection PyPep8Naming
class Bootstrapper_state_py_exec_required_reached(
    AbstractCachingStateNode[PythonExecutable]
):
    """
    Recursively runs this script inside the `python` interpreter required by the client.

    The `python` interpreter required by the client is saved into `field_env_local_python_file_abs_path`.
    """

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_input_wizard_stage_arg_loaded.name,
                EnvState.state_input_py_exec_var_loaded.name,
                EnvState.state_env_local_python_file_abs_path_eval_finalized.name,
                EnvState.state_env_local_venv_dir_abs_path_eval_finalized.name,
                EnvState.state_client_conf_env_file_abs_path_eval_finalized.name,
                EnvState.state_input_proto_code_file_abs_path_eval_finalized.name,
                EnvState.state_default_file_log_handler_configured.name,
                EnvState.state_env_local_tmp_dir_abs_path_eval_finalized.name,
                EnvState.state_args_parsed.name,
            ],
            state_name=if_none(
                state_name, EnvState.state_py_exec_required_reached.name
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:

        state_py_exec_required_reached: PythonExecutable

        # TODO: Unused, but plugged in to form complete DAG: consider adding intermediate state to plug it in:
        state_default_file_log_handler_configured = self.eval_parent_state(
            EnvState.state_default_file_log_handler_configured.name
        )

        # TODO: Unused, but plugged in to form complete DAG: consider adding intermediate state to plug it in:
        state_env_local_tmp_dir_abs_path_eval_finalized = self.eval_parent_state(
            EnvState.state_env_local_tmp_dir_abs_path_eval_finalized.name
        )

        state_args_parsed: argparse.Namespace = self.eval_parent_state(
            EnvState.state_args_parsed.name
        )

        start_id: str = getattr(
            state_args_parsed,
            ParsedArg.name_start_id.value,
        )

        state_input_py_exec_var_loaded: PythonExecutable = self.eval_parent_state(
            EnvState.state_input_py_exec_var_loaded.name
        )

        state_input_proto_code_file_abs_path_eval_finalized: str = (
            self.eval_parent_state(
                EnvState.state_input_proto_code_file_abs_path_eval_finalized.name
            )
        )

        state_env_local_python_file_abs_path_eval_finalized = self.eval_parent_state(
            EnvState.state_env_local_python_file_abs_path_eval_finalized.name
        )
        state_env_local_venv_dir_abs_path_eval_finalized = self.eval_parent_state(
            EnvState.state_env_local_venv_dir_abs_path_eval_finalized.name
        )

        assert not is_sub_path(
            state_env_local_python_file_abs_path_eval_finalized,
            state_env_local_venv_dir_abs_path_eval_finalized,
        ), f"Configured `python` [{state_env_local_python_file_abs_path_eval_finalized}] must be outside of configured `venv` [{state_env_local_venv_dir_abs_path_eval_finalized}]"

        path_to_curr_python = get_path_to_curr_python()
        logger.debug(f"path_to_curr_python: {path_to_curr_python}")

        # Do not do anything if beyond `PythonExecutable.py_exec_required`:
        if state_input_py_exec_var_loaded >= PythonExecutable.py_exec_required:
            return state_input_py_exec_var_loaded

        assert not is_sub_path(
            path_to_curr_python,
            state_env_local_venv_dir_abs_path_eval_finalized,
        ), f"Current `python` [{path_to_curr_python}] must be outside of the `venv` [{state_env_local_venv_dir_abs_path_eval_finalized}]."

        if path_to_curr_python != state_env_local_python_file_abs_path_eval_finalized:
            assert state_input_py_exec_var_loaded <= PythonExecutable.py_exec_arbitrary
            state_py_exec_required_reached = PythonExecutable.py_exec_arbitrary
            switch_python(
                curr_py_exec=state_input_py_exec_var_loaded,
                curr_python_path=path_to_curr_python,
                next_py_exec=PythonExecutable.py_exec_required,
                next_python_path=state_env_local_python_file_abs_path_eval_finalized,
                start_id=start_id,
                proto_code_abs_file_path=state_input_proto_code_file_abs_path_eval_finalized,
                wizard_stage=self.env_ctx.mutable_state_input_wizard_stage_arg_loaded.get_curr_value(
                    self,
                ),
            )
        else:
            assert state_input_py_exec_var_loaded <= PythonExecutable.py_exec_required
            state_py_exec_required_reached = PythonExecutable.py_exec_required

        return state_py_exec_required_reached


# noinspection PyPep8Naming
class Bootstrapper_state_reinstall_triggered(AbstractCachingStateNode[bool]):
    """
    Removes current `venv` dir and `constraints.txt` file (to trigger their re-creation subsequently).
    """

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_args_parsed.name,
                EnvState.state_env_local_venv_dir_abs_path_eval_finalized.name,
                EnvState.state_input_wizard_stage_arg_loaded.name,
                EnvState.state_client_conf_env_dir_abs_path_eval_finalized.name,
                EnvState.state_env_local_tmp_dir_abs_path_eval_finalized.name,
                EnvState.state_py_exec_required_reached.name,
                EnvState.state_input_proto_code_file_abs_path_eval_finalized.name,
            ],
            state_name=if_none(state_name, EnvState.state_reinstall_triggered.name),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:

        state_args_parsed: argparse.Namespace = self.eval_parent_state(
            EnvState.state_args_parsed.name
        )

        start_id: str = getattr(
            state_args_parsed,
            ParsedArg.name_start_id.value,
        )

        do_reinstall: bool = getattr(
            state_args_parsed,
            ParsedArg.name_reinstall.value,
        )

        state_py_exec_required_reached = self.eval_parent_state(
            EnvState.state_py_exec_required_reached.name
        )
        assert state_py_exec_required_reached >= PythonExecutable.py_exec_required

        state_input_proto_code_file_abs_path_eval_finalized: str = (
            self.eval_parent_state(
                EnvState.state_input_proto_code_file_abs_path_eval_finalized.name
            )
        )

        # Reinstall can only happen outside `venv`:
        if not (
            do_reinstall
            and state_py_exec_required_reached == PythonExecutable.py_exec_required
        ):
            return False

        state_env_local_venv_dir_abs_path_eval_finalized = self.eval_parent_state(
            EnvState.state_env_local_venv_dir_abs_path_eval_finalized.name
        )
        if os.path.exists(state_env_local_venv_dir_abs_path_eval_finalized):

            # Move old `venv` to temporary directory:

            state_env_local_tmp_dir_abs_path_eval_finalized = self.eval_parent_state(
                EnvState.state_env_local_tmp_dir_abs_path_eval_finalized.name
            )

            moved_venv_dir = os.path.join(
                state_env_local_tmp_dir_abs_path_eval_finalized,
                f"venv.before.{start_id}",
            )

            logger.info(
                f"moving `venv` dir from [{state_env_local_venv_dir_abs_path_eval_finalized}] to [{moved_venv_dir}]"
            )

            shutil.move(
                state_env_local_venv_dir_abs_path_eval_finalized, moved_venv_dir
            )

        state_client_conf_env_dir_abs_path_eval_finalized = self.eval_parent_state(
            EnvState.state_client_conf_env_dir_abs_path_eval_finalized.name
        )
        constraints_txt_path = os.path.join(
            state_client_conf_env_dir_abs_path_eval_finalized,
            ConfConstEnv.constraints_txt_basename,
        )
        if os.path.exists(constraints_txt_path):
            logger.info(f"removing version constraints file [{constraints_txt_path}]")
            os.remove(constraints_txt_path)

        return True


# noinspection PyPep8Naming
class Bootstrapper_state_py_exec_venv_reached(
    AbstractCachingStateNode[PythonExecutable]
):
    """
    Creates `venv` and switches to `python` from there.
    """

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_reinstall_triggered.name,
                EnvState.state_input_wizard_stage_arg_loaded.name,
                EnvState.state_input_py_exec_var_loaded.name,
                EnvState.state_env_local_python_file_abs_path_eval_finalized.name,
                EnvState.state_env_local_venv_dir_abs_path_eval_finalized.name,
                EnvState.state_client_conf_env_file_abs_path_eval_finalized.name,
                EnvState.state_input_proto_code_file_abs_path_eval_finalized.name,
                EnvState.state_args_parsed.name,
            ],
            state_name=if_none(state_name, EnvState.state_py_exec_venv_reached.name),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:

        state_py_exec_venv_reached: PythonExecutable

        state_args_parsed: argparse.Namespace = self.eval_parent_state(
            EnvState.state_args_parsed.name
        )

        start_id: str = getattr(
            state_args_parsed,
            ParsedArg.name_start_id.value,
        )

        state_reinstall_triggered: bool = self.eval_parent_state(
            EnvState.state_reinstall_triggered.name
        )

        state_input_py_exec_var_loaded: PythonExecutable = self.eval_parent_state(
            EnvState.state_input_py_exec_var_loaded.name
        )

        state_input_proto_code_file_abs_path_eval_finalized: str = (
            self.eval_parent_state(
                EnvState.state_input_proto_code_file_abs_path_eval_finalized.name
            )
        )

        state_env_local_python_file_abs_path_eval_finalized = self.eval_parent_state(
            EnvState.state_env_local_python_file_abs_path_eval_finalized.name
        )
        state_env_local_venv_dir_abs_path_eval_finalized = self.eval_parent_state(
            EnvState.state_env_local_venv_dir_abs_path_eval_finalized.name
        )

        venv_path_to_python = os.path.join(
            state_env_local_venv_dir_abs_path_eval_finalized,
            ConfConstGeneral.file_rel_path_venv_python,
        )
        path_to_curr_python = get_path_to_curr_python()
        logger.debug(f"path_to_curr_python: {path_to_curr_python}")

        # Do not do anything if beyond `PythonExecutable.py_exec_venv`:
        if state_input_py_exec_var_loaded >= PythonExecutable.py_exec_venv:
            return state_input_py_exec_var_loaded

        assert not is_sub_path(
            path_to_curr_python,
            state_env_local_venv_dir_abs_path_eval_finalized,
        ), f"Current `python` [{path_to_curr_python}] must be outside of `venv` [{state_env_local_venv_dir_abs_path_eval_finalized}]."
        assert (
            path_to_curr_python == state_env_local_python_file_abs_path_eval_finalized
        ), f"Current `python` [{path_to_curr_python}] must match the required one [{state_env_local_python_file_abs_path_eval_finalized}]."

        assert state_input_py_exec_var_loaded <= PythonExecutable.py_exec_required
        state_py_exec_venv_reached = PythonExecutable.py_exec_required
        if not os.path.exists(state_env_local_venv_dir_abs_path_eval_finalized):
            logger.info(
                f"creating `venv` [{state_env_local_venv_dir_abs_path_eval_finalized}]"
            )
            venv.create(
                state_env_local_venv_dir_abs_path_eval_finalized,
                with_pip=True,
            )
        else:
            logger.info(
                f"reusing existing `venv` [{state_env_local_venv_dir_abs_path_eval_finalized}]"
            )
        switch_python(
            curr_py_exec=state_input_py_exec_var_loaded,
            curr_python_path=state_env_local_python_file_abs_path_eval_finalized,
            next_py_exec=PythonExecutable.py_exec_venv,
            next_python_path=venv_path_to_python,
            start_id=start_id,
            proto_code_abs_file_path=state_input_proto_code_file_abs_path_eval_finalized,
            wizard_stage=self.env_ctx.mutable_state_input_wizard_stage_arg_loaded.get_curr_value(
                self,
            ),
        )

        return state_py_exec_venv_reached


# noinspection PyPep8Naming
class Bootstrapper_state_protoprimer_package_installed(AbstractCachingStateNode[bool]):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_args_parsed.name,
                EnvState.state_input_do_install_var_loaded.name,
                EnvState.state_py_exec_venv_reached.name,
                EnvState.state_primer_ref_root_dir_abs_path_eval_finalized.name,
                EnvState.state_client_conf_env_dir_abs_path_eval_finalized.name,
                EnvState.state_env_project_descriptors_eval_finalized.name,
            ],
            state_name=if_none(
                state_name, EnvState.state_protoprimer_package_installed.name
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:

        state_input_do_install_var_loaded: bool = self.eval_parent_state(
            EnvState.state_input_do_install_var_loaded.name
        )

        state_args_parsed: argparse.Namespace = self.eval_parent_state(
            EnvState.state_args_parsed.name
        )

        state_py_exec_venv_reached: PythonExecutable = self.eval_parent_state(
            EnvState.state_py_exec_venv_reached.name
        )
        assert state_py_exec_venv_reached >= PythonExecutable.py_exec_venv

        state_primer_ref_root_dir_abs_path_eval_finalized: str = self.eval_parent_state(
            EnvState.state_primer_ref_root_dir_abs_path_eval_finalized.name
        )

        state_client_conf_env_dir_abs_path_eval_finalized: str = self.eval_parent_state(
            EnvState.state_client_conf_env_dir_abs_path_eval_finalized.name
        )

        state_env_project_descriptors_eval_finalized: list[dict] = (
            self.eval_parent_state(
                EnvState.state_env_project_descriptors_eval_finalized.name
            )
        )

        do_reinstall: bool = getattr(
            state_args_parsed,
            ParsedArg.name_reinstall.value,
        )

        do_install: bool = (
            state_py_exec_venv_reached == PythonExecutable.py_exec_venv
            and (do_reinstall or state_input_do_install_var_loaded)
        )

        if not do_install:
            return False

        constraints_txt_path = os.path.join(
            state_client_conf_env_dir_abs_path_eval_finalized,
            ConfConstEnv.constraints_txt_basename,
        )
        if not os.path.exists(constraints_txt_path):
            logger.info(f"creating empty constraints file [{constraints_txt_path}]")
            write_text_file(constraints_txt_path, "")

        if len(state_env_project_descriptors_eval_finalized) == 0:
            logger.warning(
                f"{ValueName.value_project_descriptors.value} is empty - nothing to install"
            )
            return True

        # pre-validate:
        for env_project_descriptor in state_env_project_descriptors_eval_finalized:
            # FT_46_37_27_11.editable_install.md

            field_env_build_root_dir_rel_path = os.path.join(
                state_primer_ref_root_dir_abs_path_eval_finalized,
                env_project_descriptor[
                    ConfField.field_env_build_root_dir_rel_path.value
                ],
            )
            assert os.path.isfile(
                os.path.join(
                    field_env_build_root_dir_rel_path,
                    ConfConstClient.default_pyproject_toml_basename,
                )
            )

        # install:
        install_editable_project(
            state_primer_ref_root_dir_abs_path_eval_finalized,
            state_env_project_descriptors_eval_finalized,
            constraints_txt_path,
        )

        return True


# noinspection PyPep8Naming
class Bootstrapper_state_version_constraints_generated(AbstractCachingStateNode[bool]):
    """
    Implements UC_44_82_07_30.requirements_lock.md.
    """

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_protoprimer_package_installed.name,
                EnvState.state_client_conf_env_dir_abs_path_eval_finalized.name,
            ],
            state_name=if_none(
                state_name, EnvState.state_version_constraints_generated.name
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:
        state_protoprimer_package_installed: bool = self.eval_parent_state(
            EnvState.state_protoprimer_package_installed.name
        )

        if not state_protoprimer_package_installed:
            return False

        state_client_conf_env_dir_abs_path_eval_finalized: str = self.eval_parent_state(
            EnvState.state_client_conf_env_dir_abs_path_eval_finalized.name
        )

        constraints_txt_path = os.path.join(
            state_client_conf_env_dir_abs_path_eval_finalized,
            ConfConstEnv.constraints_txt_basename,
        )
        logger.info(f"generating version constraints file [{constraints_txt_path}]")
        with open(constraints_txt_path, "w") as f:
            subprocess.check_call(
                [
                    get_path_to_curr_python(),
                    "-m",
                    "pip",
                    "freeze",
                    "--exclude-editable",
                ],
                stdout=f,
            )

        return True


# noinspection PyPep8Naming
class Bootstrapper_state_py_exec_updated_protoprimer_package_reached(
    AbstractCachingStateNode[PythonExecutable]
):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_input_wizard_stage_arg_loaded.name,
                EnvState.state_input_py_exec_var_loaded.name,
                EnvState.state_input_proto_code_file_abs_path_eval_finalized.name,
                EnvState.state_version_constraints_generated.name,
                EnvState.state_args_parsed.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_py_exec_updated_protoprimer_package_reached.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:

        state_py_exec_updated_protoprimer_package_reached: PythonExecutable

        state_input_py_exec_var_loaded: PythonExecutable = self.eval_parent_state(
            EnvState.state_input_py_exec_var_loaded.name
        )

        state_input_proto_code_file_abs_path_eval_finalized: str = (
            self.eval_parent_state(
                EnvState.state_input_proto_code_file_abs_path_eval_finalized.name
            )
        )

        state_version_constraints_generated: bool = self.eval_parent_state(
            EnvState.state_version_constraints_generated.name
        )

        if (
            state_input_py_exec_var_loaded.value
            < PythonExecutable.py_exec_updated_protoprimer_package.value
        ):
            venv_path_to_python = get_path_to_curr_python()

            state_args_parsed: argparse.Namespace = self.eval_parent_state(
                EnvState.state_args_parsed.name
            )

            start_id: str = getattr(
                state_args_parsed,
                ParsedArg.name_start_id.value,
            )

            state_py_exec_updated_protoprimer_package_reached = (
                PythonExecutable.py_exec_updated_protoprimer_package
            )
            # TODO: maybe add this reason to `switch_python` as an arg?
            logger.debug(
                f"restarting current `python` interpreter [{venv_path_to_python}] to make [{EnvState.state_protoprimer_package_installed.name}] effective"
            )
            switch_python(
                curr_py_exec=state_input_py_exec_var_loaded,
                curr_python_path=venv_path_to_python,
                next_py_exec=PythonExecutable.py_exec_updated_protoprimer_package,
                next_python_path=venv_path_to_python,
                start_id=start_id,
                proto_code_abs_file_path=state_input_proto_code_file_abs_path_eval_finalized,
                wizard_stage=self.env_ctx.mutable_state_input_wizard_stage_arg_loaded.get_curr_value(
                    self,
                ),
            )
        else:
            # Successfully reached the end goal:
            state_py_exec_updated_protoprimer_package_reached = (
                state_input_py_exec_var_loaded
            )

        return state_py_exec_updated_protoprimer_package_reached


# noinspection PyPep8Naming
class Bootstrapper_state_proto_code_updated(AbstractCachingStateNode[bool]):
    """
    TODO: UC_52_87_82_92.conditional_auto_update.md
    """

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_py_exec_updated_protoprimer_package_reached.name,
                EnvState.state_input_proto_code_file_abs_path_eval_finalized.name,
            ],
            state_name=if_none(state_name, EnvState.state_proto_code_updated.name),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:
        state_py_exec_updated_protoprimer_package_reached: PythonExecutable = (
            self.eval_parent_state(
                EnvState.state_py_exec_updated_protoprimer_package_reached.name
            )
        )
        assert (
            state_py_exec_updated_protoprimer_package_reached
            >= PythonExecutable.py_exec_updated_protoprimer_package
        )

        # TODO: optimize: run this logic only when `PythonExecutable.py_exec_updated_protoprimer_package`

        state_input_proto_code_file_abs_path_eval_finalized = self.eval_parent_state(
            EnvState.state_input_proto_code_file_abs_path_eval_finalized.name
        )
        assert os.path.isabs(state_input_proto_code_file_abs_path_eval_finalized)
        assert not os.path.islink(state_input_proto_code_file_abs_path_eval_finalized)
        assert os.path.isfile(state_input_proto_code_file_abs_path_eval_finalized)

        assert is_venv()
        import protoprimer

        # Use generator from an immutable (source) `primer_kernel`
        # instead of current local (target) `proto_code` module to avoid:
        # generated code inside generated code inside generated code ...
        generated_content_single_header: str = (
            protoprimer.primer_kernel.ConfConstGeneral.func_get_proto_code_generated_boilerplate_single_header(
                protoprimer.primer_kernel
            )
        )
        generated_content_multiple_body: str = (
            protoprimer.primer_kernel.ConfConstGeneral.func_get_proto_code_generated_boilerplate_multiple_body(
                protoprimer.primer_kernel
            )
        )

        primer_kernel_abs_path = os.path.abspath(protoprimer.primer_kernel.__file__)
        primer_kernel_text: str = read_text_file(primer_kernel_abs_path)

        # Update body:
        proto_code_text_periodic = insert_every_n_lines(
            input_text=primer_kernel_text,
            insert_text=generated_content_multiple_body,
            every_n=20,
        )

        # Update header:
        file_lines = proto_code_text_periodic.splitlines()
        file_lines.insert(1, generated_content_single_header)
        proto_code_text = "\n".join(file_lines)

        logger.debug(
            f"writing `primer_kernel_abs_path` [{primer_kernel_abs_path}] over `state_input_proto_code_file_abs_path_eval_finalized` [{state_input_proto_code_file_abs_path_eval_finalized}]"
        )
        write_text_file(
            file_path=state_input_proto_code_file_abs_path_eval_finalized,
            file_data=proto_code_text,
        )

        # TODO: optimize: return true if content changed:

        return True


# noinspection PyPep8Naming
class Bootstrapper_state_py_exec_updated_proto_code(
    AbstractCachingStateNode[PythonExecutable]
):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_input_wizard_stage_arg_loaded.name,
                EnvState.state_input_py_exec_var_loaded.name,
                EnvState.state_proto_code_updated.name,
                EnvState.state_input_proto_code_file_abs_path_eval_finalized.name,
                EnvState.state_args_parsed.name,
            ],
            state_name=if_none(
                state_name, EnvState.state_py_exec_updated_proto_code.name
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:

        state_py_exec_updated_proto_code: PythonExecutable

        state_input_py_exec_var_loaded: PythonExecutable = self.eval_parent_state(
            EnvState.state_input_py_exec_var_loaded.name
        )

        state_input_proto_code_file_abs_path_eval_finalized: str = (
            self.eval_parent_state(
                EnvState.state_input_proto_code_file_abs_path_eval_finalized.name
            )
        )

        state_proto_code_updated: bool = self.eval_parent_state(
            EnvState.state_proto_code_updated.name
        )
        assert state_proto_code_updated

        venv_path_to_python = get_path_to_curr_python()

        if (
            state_input_py_exec_var_loaded.value
            < PythonExecutable.py_exec_updated_proto_code.value
        ):

            state_args_parsed: argparse.Namespace = self.eval_parent_state(
                EnvState.state_args_parsed.name
            )

            start_id: str = getattr(
                state_args_parsed,
                ParsedArg.name_start_id.value,
            )

            state_py_exec_updated_proto_code = (
                PythonExecutable.py_exec_updated_proto_code
            )
            # TODO: maybe add this reason to `switch_python` as an arg?
            logger.debug(
                f"restarting current `python` interpreter [{venv_path_to_python}] to make [{EnvState.state_proto_code_updated.name}] effective"
            )
            switch_python(
                curr_py_exec=state_input_py_exec_var_loaded,
                curr_python_path=venv_path_to_python,
                next_py_exec=PythonExecutable.py_exec_updated_proto_code,
                next_python_path=venv_path_to_python,
                start_id=start_id,
                proto_code_abs_file_path=state_input_proto_code_file_abs_path_eval_finalized,
                wizard_stage=self.env_ctx.mutable_state_input_wizard_stage_arg_loaded.get_curr_value(
                    self,
                ),
            )
        else:
            # Successfully reached the end goal:
            state_py_exec_updated_proto_code = state_input_py_exec_var_loaded

        return state_py_exec_updated_proto_code


# noinspection PyPep8Naming
class Bootstrapper_state_command_executed(AbstractCachingStateNode[int]):
    """
    If `ParsedArg.name_command`, this state replaces the current process with a shell executing the given command.
    """

    def __init__(
        self,
        env_ctx: EnvContext,
        parent_states: list[str] | None = None,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=if_none(
                parent_states,
                [
                    EnvState.state_args_parsed.name,
                    EnvState.state_default_stderr_log_handler_configured.name,
                    EnvState.state_py_exec_updated_proto_code.name,
                ],
            ),
            state_name=if_none(state_name, EnvState.state_command_executed.name),
        )
        self.shell_args: list[str] = []
        # TODO: get path automatically (or by config) - this will not work for everyone:
        self.shell_abs_path: str = "/usr/bin/bash"
        self.start_shell: bool = False

    def _eval_state_once(
        self,
    ) -> ValueType:

        state_default_stderr_log_handler_configured: logging.Handler = (
            self.eval_parent_state(
                EnvState.state_default_stderr_log_handler_configured.name
            )
        )

        state_py_exec_updated_proto_code: PythonExecutable = self.eval_parent_state(
            EnvState.state_py_exec_updated_proto_code.name
        )
        assert (
            state_py_exec_updated_proto_code
            >= PythonExecutable.py_exec_updated_proto_code
        )

        state_args_parsed: argparse.Namespace = self.eval_parent_state(
            EnvState.state_args_parsed.name
        )

        command_line: str = getattr(
            state_args_parsed,
            ParsedArg.name_command.value,
        )

        self._prepare_shell_env()

        if command_line is not None:
            self.shell_args.extend(
                [
                    "-c",
                    command_line,
                ]
            )
            self.start_shell = True

        if self.start_shell:
            print_delegate_line(
                self.shell_args,
                state_default_stderr_log_handler_configured,
            )

            os.execv(
                self.shell_abs_path,
                self.shell_args,
            )
        else:
            # Otherwise, exit_code is 0:
            return 0

    def _prepare_shell_env(self):
        shell_basename: str = os.path.basename(self.shell_abs_path)
        self.shell_args: list[str] = [
            shell_basename,
        ]


class WizardState(enum.Enum):
    """
    These states replace some of the `EnvState` (named the same way) during `RunMode.mode_wizard`.
    """

    state_proto_conf_file_data = Wizard_state_proto_conf_file_data

    state_client_conf_file_data = Wizard_state_client_conf_file_data

    state_env_conf_file_data = Wizard_state_env_conf_file_data


class EnvState(enum.Enum):
    """
    Environment states to be reached during the bootstrap process.

    NOTE: Only `str` names of the enum items are supposed to be used (any value is ignored).
    The value of `AbstractCachingStateNode` assigned is the default implementation for the state,
    and the only reason it is assigned is purely for the quick navigation across the source code in the IDE.

    FT_68_54_41_96.state_dependency.md
    """

    # TODO: Rename Bootstrapper -> Primer or something else (to be different from Wizard):

    state_input_stderr_log_level_var_loaded = (
        Bootstrapper_state_input_stderr_log_level_var_loaded
    )

    state_input_do_install_var_loaded = Bootstrapper_state_input_do_install_var_loaded

    state_default_stderr_log_handler_configured = (
        Bootstrapper_state_default_stderr_log_handler_configured
    )

    state_args_parsed = Bootstrapper_state_args_parsed

    state_input_wizard_stage_arg_loaded = (
        Bootstrapper_state_input_wizard_stage_arg_loaded
    )

    state_input_stderr_log_level_eval_finalized = (
        Bootstrapper_state_input_stderr_log_level_eval_finalized
    )

    state_input_run_mode_arg_loaded = Bootstrapper_state_input_run_mode_arg_loaded

    state_input_final_state_eval_finalized = (
        Bootstrapper_state_input_final_state_eval_finalized
    )

    # Special case: triggers everything:
    state_run_mode_executed = Bootstrapper_state_run_mode_executed

    state_input_py_exec_var_loaded = Bootstrapper_state_input_py_exec_var_loaded

    state_py_exec_arbitrary_reached = Bootstrapper_state_py_exec_arbitrary_reached

    state_input_proto_code_file_abs_path_eval_finalized = (
        Bootstrapper_state_input_proto_code_file_abs_path_eval_finalized
    )

    state_input_proto_code_dir_abs_path_eval_finalized = (
        Bootstrapper_state_input_proto_code_dir_abs_path_eval_finalized
    )

    state_input_proto_conf_primer_file_abs_path_eval_finalized = (
        Bootstrapper_state_input_proto_conf_primer_file_abs_path_eval_finalized
    )

    # The state is wizard-able by `Wizard_state_proto_conf_file_data`:
    state_proto_conf_file_data = Bootstrapper_state_proto_conf_file_data

    state_primer_ref_root_dir_abs_path_eval_finalized = (
        Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized
    )

    state_primer_conf_client_file_abs_path_eval_finalized = (
        Bootstrapper_state_primer_conf_client_file_abs_path_eval_finalized
    )

    # The state is wizard-able by `Wizard_state_client_conf_file_data`:
    state_client_conf_file_data = Bootstrapper_state_client_conf_file_data

    state_client_local_env_dir_rel_path_eval_finalized = (
        Bootstrapper_state_client_local_env_dir_rel_path_eval_finalized
    )

    state_client_conf_env_dir_abs_path_eval_finalized = (
        Bootstrapper_state_client_conf_env_dir_abs_path_eval_finalized
    )

    state_client_link_name_dir_rel_path_eval_finalized = (
        Bootstrapper_state_client_link_name_dir_rel_path_eval_finalized
    )

    state_client_conf_env_file_abs_path_eval_finalized = (
        Bootstrapper_state_client_conf_env_file_abs_path_eval_finalized
    )

    # The state is wizard-able by `Wizard_state_env_conf_file_data`:
    state_env_conf_file_data = Bootstrapper_state_env_conf_file_data

    # TODO: not env but global leap_client one:
    # state_env_log_level

    # TODO: rename: `local_python` -> `required_python`:
    state_env_local_python_file_abs_path_eval_finalized = (
        Bootstrapper_state_env_local_python_file_abs_path_eval_finalized
    )

    # TODO: log, tmp, venv, ... dirs should better be configured at client level:
    state_env_local_venv_dir_abs_path_eval_finalized = (
        Bootstrapper_state_env_local_venv_dir_abs_path_eval_finalized
    )

    # TODO: log, tmp, venv, ... dirs should better be configured at client level:
    state_env_local_log_dir_abs_path_eval_finalized = (
        Bootstrapper_state_env_local_log_dir_abs_path_eval_finalized
    )

    # TODO: log, tmp, venv, ... dirs should better be configured at client level:
    state_env_local_tmp_dir_abs_path_eval_finalized = (
        Bootstrapper_state_env_local_tmp_dir_abs_path_eval_finalized
    )

    state_env_project_descriptors_eval_finalized = (
        Bootstrapper_state_env_project_descriptors_eval_finalized
    )

    state_default_file_log_handler_configured = (
        Bootstrapper_state_default_file_log_handler_configured
    )

    state_py_exec_required_reached = Bootstrapper_state_py_exec_required_reached

    state_reinstall_triggered = Bootstrapper_state_reinstall_triggered

    state_py_exec_venv_reached = Bootstrapper_state_py_exec_venv_reached

    # TODO: rename to "client" (or "ref"?): `client_project_descriptors_installed`:
    state_protoprimer_package_installed = (
        Bootstrapper_state_protoprimer_package_installed
    )

    state_version_constraints_generated = (
        Bootstrapper_state_version_constraints_generated
    )

    # TODO: rename - "reached" sounds weird (and makes no sense):
    state_py_exec_updated_protoprimer_package_reached = (
        Bootstrapper_state_py_exec_updated_protoprimer_package_reached
    )

    # TODO: rename according to the final name:
    state_proto_code_updated = Bootstrapper_state_proto_code_updated

    state_py_exec_updated_proto_code = Bootstrapper_state_py_exec_updated_proto_code

    state_command_executed = Bootstrapper_state_command_executed


# TODO: Convert this to Enum?
class TargetState:
    """
    Special `EnvState`-s.
    """

    # The final state before switching to `PrimerRuntime.runtime_neo`:
    target_full_proto_bootstrap: str = EnvState.state_command_executed.name

    # A special state which triggers execution in the specific `RunMode`:
    target_run_mode_executed: str = EnvState.state_run_mode_executed.name

    # Used for `EnvState.state_status_line_printed` to report exit code.
    target_stderr_log_handler: str = (
        EnvState.state_default_stderr_log_handler_configured.name
    )


class StateGraph:
    """
    It is a graph, which must be a DAG.
    """

    def __init__(
        self,
    ):
        self.state_nodes: dict[str, StateNode] = {}

    def register_node(
        self,
        state_node: StateNode,
        replace_existing: bool = False,
    ) -> StateNode | None:
        state_name: str = state_node.get_state_name()
        if state_name in self.state_nodes:
            if replace_existing:
                existing_node = self.state_nodes[state_name]
                self.state_nodes[state_name] = state_node
                return existing_node
            else:
                raise AssertionError(
                    f"[{StateNode.__name__}] for [{state_name}] is already registered."
                )
        else:
            self.state_nodes[state_name] = state_node
            return None

    def get_state_node(
        self,
        state_name: str,
    ) -> StateNode | None:
        return self.state_nodes[state_name]

    def eval_state(
        self,
        state_name: str,
    ) -> Any:
        try:
            state_node = self.state_nodes[state_name]
        except KeyError:
            logger.error(f"`state_name` [{state_name}] is not registered.")
            raise
        return state_node.eval_own_state()


class MutableValue(Generic[ValueType]):
    """
    A mutable value which must be evaluated (initialized) via one of the `StateNode`-s before it can be used.

    This class provides an N-to-1 mechanism where N x `StateNode`-s update 1 x named `MutableValue`.

    Immutable values produced by `StateNode`-s cannot be changed -
    once evaluated, these values stay the same.
    Unlike `StateNode` values, `MutableValue` can evolve.

    NOTE: The issue with `MutableValue`-s is that the order of reading/writing them is important.
    To avoid defects, always read them last (after evaluation of all parent `StateNode` states).
    It is not required to bootstrap to the latest `StateNode` updating the given `MutableValue`
    because some of these `StateNode`-s may not be (transitive) parents.
    But, if the current `StateNode` depends on parents updating that `MutableValue`,
    read it after evaluation of all parent states.
    """

    def __init__(
        self,
        state_name: str,
    ):
        # TODO: It should not be called state_name and should be disassociated from states in DAG.
        #       It should be modeled as a value which is changed by multiple states
        #       and (depending on the current state in DAG) should be accessed after those states on
        #       the path to the current one have already been evaluated.
        self.state_name = state_name
        self.curr_value: ValueType | None = None

    def get_curr_value(
        self,
        state_node: StateNode,
    ) -> ValueType:

        # This ensures that the `StateNode` using that `MutableValue`
        # declares `state_name` as a dependency:
        init_value = state_node.eval_parent_state(self.state_name)

        if self.curr_value is None:
            self.curr_value = init_value

        logger.debug(
            f"`{self.__class__.__name__}` [{self.state_name}] `curr_value` after get [{self.curr_value}] in [{state_node.get_state_name()}]"
        )
        return self.curr_value

    def set_curr_value(
        self,
        state_node: StateNode | None,
        curr_value: ValueType,
    ) -> None:
        # TODO: Shell we also ensure that the `StateNode` using that `MutableValue` has necessary dependencies on write?

        if self.curr_value is None:
            raise AssertionError(
                f"`{MutableValue.__name__}` [{self.state_name}] cannot be set as it is not initialized yet."
            )
        state_name: str | None = None
        self.curr_value = curr_value
        logger.debug(
            f"`{self.__class__.__name__}` [{self.state_name}] `curr_value` after set [{self.curr_value}] in [{state_node.get_state_name()}]"
        )


class EnvContext:

    def __init__(
        self,
    ):
        self.state_graph: StateGraph = StateGraph()

        # TODO: Do not set it on Context - use bootstrap-able values:
        # TODO: Find "Universal Sink":
        self.final_state: str = TargetState.target_full_proto_bootstrap

        self.mutable_state_input_wizard_stage_arg_loaded: MutableValue[WizardStage] = (
            MutableValue(
                EnvState.state_input_wizard_stage_arg_loaded.name,
            )
        )

        self._build_default_graph()

    def _build_default_graph(self):
        """
        Registers all defined `EnvState`-s.
        """
        for env_state in EnvState:
            self.state_graph.register_node(env_state.value(self))

    def print_exit_line(
        self,
        exit_code: int,
    ) -> None:
        """
        Print a color-coded status message to stderr.
        """
        assert type(exit_code) is int, "`exit_code` must be an `int`"

        color_success = (
            f"{TermColor.back_dark_green.value}{TermColor.fore_dark_black.value}"
        )
        color_failure = (
            f"{TermColor.back_dark_red.value}{TermColor.fore_bright_white.value}"
        )
        color_reset = TermColor.reset_style.value

        state_default_stderr_log_handler_configured: logging.Handler = (
            self.state_graph.eval_state(
                EnvState.state_default_stderr_log_handler_configured.name
            )
        )

        is_reportable: bool
        if exit_code == 0:
            color_status = color_success
            status_name = "SUCCESS"
            is_reportable = (
                state_default_stderr_log_handler_configured.level <= logging.INFO
            )
        else:
            color_status = color_failure
            status_name = "FAILURE"
            is_reportable = (
                state_default_stderr_log_handler_configured.level <= logging.CRITICAL
            )

        if is_reportable:
            print(
                f"{color_status}{status_name}{color_reset} [{exit_code}]: {get_path_to_curr_python()} {get_script_command_line()}",
                file=sys.stderr,
                flush=True,
            )


class PythonExecutableFilter(logging.Filter):
    """
    This filter sets the value of `EnvVar.var_PROTOPRIMER_PY_EXEC` for each log entry.
    """

    def filter(self, record):
        record.py_exec_name = os.getenv(
            EnvVar.var_PROTOPRIMER_PY_EXEC.value,
            None,
        )
        return True


class RegularFormatter(logging.Formatter):
    """
    Custom formatter with the proper timestamp.
    """

    def __init__(
        self,
    ):
        # noinspection SpellCheckingInspection
        super().__init__(
            fmt="%(asctime)s %(process)d %(levelname)s %(py_exec_name)s %(filename)s:%(lineno)d %(message)s",
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


class ColorFormatter(RegularFormatter):
    """
    Custom formatter with color based on log level.
    """

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


def rename_to_moved_state_name(state_name: str) -> str:
    """
    See UC_27_40_17_59.replace_by_new_and_use_old.md
    """
    return f"_{state_name}"


def error_on_missing_conf_file(
    file_abs_path: str,
) -> str:
    raise AssertionError(
        f"File [{file_abs_path}] does not exists - re-run with [{SyntaxArg.arg_mode_wizard}] to create it."
    )


def wizard_confirm_single_value(
    state_node: StateNode,
    wizard_meta: FieldWizardMeta,
    file_data: dict,
    sub_ordinal_n: int,
    sub_size: int,
    total_ordinal_n: int,
    total_size: int,
) -> None:
    """
    Wizard individual field provided by `FieldWizardMeta`.
    """

    while True:
        print("---")
        print(f"Total progress: {total_ordinal_n}/{total_size}")
        print(f"[{wizard_meta.field_leap.name}] progress: {sub_ordinal_n}/{sub_size}")
        print(
            f"{TermColor.field_name.value}Field: {wizard_meta.field_name}{TermColor.reset_style.value}"
        )
        print(
            f"{TermColor.field_description.value}Description: {wizard_meta.field_help(wizard_meta, state_node, file_data)}{TermColor.reset_style.value}"
        )

        field_warning: str | None = wizard_meta.warn_if_not_wizard_able(
            wizard_meta,
            state_node,
            file_data,
        )
        if field_warning is not None:
            print(field_warning)
            while True:
                user_confirmation = input(f"Acknowledge this (a) >").lower().strip()

                if user_confirmation == "a":
                    print(f"Continuing...")
                    # break the inner and the outer loops:
                    return
                else:
                    # continue the inner loop
                    continue

        curr_param_value = wizard_meta.read_value(
            wizard_meta,
            state_node,
            file_data,
        )

        print(
            f"Enter blank to keep the current value [{curr_param_value}] or provide a new value:"
        )
        new_param_value = input(f"[{curr_param_value}] >").strip()

        if new_param_value == "":
            # blank keeps the current value:
            new_param_value = curr_param_value

        review_text: str | None = wizard_meta.review_value(
            wizard_meta,
            state_node,
            file_data,
            new_param_value,
        )
        if review_text is not None:
            print(
                f"{TermColor.field_review.value}{review_text}{TermColor.reset_style.value}"
            )

        validation_error = wizard_meta.validate_value(
            wizard_meta, state_node, file_data, new_param_value
        )
        if validation_error is not None:
            print(
                f"{TermColor.error_text.value}{validation_error}{TermColor.reset_style.value}"
            )
            print(f"Failing...")
            continue

        while True:

            user_confirmation = (
                input(
                    f"Confirm the value [{new_param_value}] (enter blank to skip, or y/n) >"
                )
                .lower()
                .strip()
            )

            if user_confirmation == "y":
                print(f"Confirming...")
                curr_param_value = new_param_value
                # value has been changed - write `new_param_value`:
                wizard_meta.write_value(
                    wizard_meta,
                    state_node,
                    file_data,
                    new_param_value,
                )
                # break the inner and the outer loops:
                return
            elif user_confirmation == "":
                print(f"Skipping...")
                # TODO: It is not necessary to write.
                #       But at the moment, this is a workaround to in case like
                #       `WizardField.field_env_build_root_dir_rel_path` when the value read
                #       might be a synthesized default (and the file still requires to be rendered correctly).
                # value is not changed - write `curr_param_value`:
                wizard_meta.write_value(
                    wizard_meta,
                    state_node,
                    file_data,
                    curr_param_value,
                )
                # break the inner and the outer loops:
                return
            elif user_confirmation == "n":
                print(f"Retrying...")
                # break the inner loop to retry the outer:
                break
            else:
                continue


def wizard_conf_file(
    state_node: StateNode,
    conf_leap: ConfLeap,
    conf_abs_path: str,
    # TODO: Instead of providing entire file, populate `FieldWizardMeta` how to compute default value:
    default_file_data: dict,
) -> dict:
    """
    A wrapper over `wizard_conf_leap` to persist the file data.
    """

    file_data: dict
    if os.path.exists(conf_abs_path):
        file_data = read_json_file(conf_abs_path)
    else:
        file_data = default_file_data

    verify_conf_file_data(
        conf_abs_path,
        file_data,
        conf_leap,
    )

    wizard_stage: WizardStage = (
        state_node.env_ctx.mutable_state_input_wizard_stage_arg_loaded.get_curr_value(
            state_node,
        )
    )

    if wizard_stage == WizardStage.wizard_started:
        wizard_conf_leap(
            state_node,
            conf_leap,
            conf_abs_path,
            file_data,
        )
        os.makedirs(
            os.path.dirname(conf_abs_path),
            exist_ok=True,
        )
        write_json_file(
            conf_abs_path,
            file_data,
        )

    return file_data


def wizard_conf_leap(
    state_node: StateNode,
    conf_leap: ConfLeap,
    conf_abs_path: str,
    file_data: dict,
) -> None:
    """
    Wizard through every field for the given `ConfLeap`.
    """

    enumerated_conf_leap_fields = WizardField.enumerate_conf_leap_fields(conf_leap)
    total_size = len(WizardField)
    sub_size = len(enumerated_conf_leap_fields)

    while True:

        print("===")
        print(f"File path: {conf_abs_path}")
        print(f"[{conf_leap.name}] summary before:")
        wizard_print_summary(file_data, conf_leap)

        # Wizard fields:
        for sub_ordinal_i, (total_ordinal_i, wizard_field) in enumerate(
            enumerated_conf_leap_fields
        ):
            wizard_confirm_single_value(
                state_node,
                wizard_field.value,
                file_data,
                sub_ordinal_i + 1,
                sub_size,
                total_ordinal_i + 1,
                total_size,
            )

        print("===")
        print(f"File path: {conf_abs_path}")
        print(f"[{conf_leap.name}] summary after:")
        wizard_print_summary(file_data, conf_leap)

        # Confirm fields together:
        while True:
            user_confirmation = input(f"Confirm the values (y/n) >").lower().strip()

            if user_confirmation == "y":
                print(f"Confirming...")
                # break the inner and the outer loops:
                return
            elif user_confirmation == "":
                # continue the inner loop
                continue
            elif user_confirmation == "n":
                print(f"Retrying...")
                # break the inner loop to retry the outer:
                break
            else:
                continue


def wizard_print_summary(
    file_data,
    conf_leap: ConfLeap,
) -> None:

    enumerated_conf_leap_fields = WizardField.enumerate_conf_leap_fields(conf_leap)

    # Construct data for specific `conf_leap` only:
    summary_data = {}
    for total_ordinal_i, wizard_field in enumerated_conf_leap_fields:
        wizard_meta = wizard_field.value
        if wizard_meta.root_ancestor_field not in file_data:
            raise AssertionError(
                f"missing field_name [{wizard_meta.field_name}] in field_data [{file_data}] with root_ancestor_field [{wizard_meta.root_ancestor_field}]"
            )
        summary_data[wizard_meta.root_ancestor_field] = file_data[
            wizard_meta.root_ancestor_field
        ]

    print(json.dumps(summary_data, indent=4))


def verify_conf_file_data(
    file_path: str,
    file_data: dict,
    conf_leap: ConfLeap,
) -> None:
    """
    Verifies that the config file data contains all expected fields and no extra fields.
    """
    expected_fields = {
        wizard_field.value.root_ancestor_field
        for _, wizard_field in WizardField.enumerate_conf_leap_fields(conf_leap)
    }
    actual_fields = set(file_data.keys())

    missing_fields = expected_fields - actual_fields
    extra_fields = actual_fields - expected_fields

    for field_name in missing_fields:
        logger.warning(f"missing field [{field_name}] in config file [{file_path}]")

    for field_name in extra_fields:
        logger.warning(f"extra field [{field_name}] in config file [{file_path}]")


def switch_python(
    curr_py_exec: PythonExecutable,
    curr_python_path: str,
    next_py_exec: PythonExecutable,
    next_python_path: str,
    start_id: str,
    proto_code_abs_file_path: str | None,
    wizard_stage: WizardStage,
    required_environ: dict | None = None,
):
    logger.info(
        f"switching from current `python` interpreter [{curr_python_path}][{curr_py_exec.name}] to [{next_python_path}][{next_py_exec.name}] with `{ParsedArg.name_proto_code.value}`[{proto_code_abs_file_path}]"
        "\n"
        "\n"
        f"{'=' * 40}"
        "\n"
    )
    # TODO: Do not add args if they have been parsed and already have the same value:
    exec_argv: list[str] = [
        next_python_path,
        *sys.argv,
        # ---
    ]

    if SyntaxArg.arg_start_id not in sys.argv:
        exec_argv.extend(
            [
                SyntaxArg.arg_start_id,
                start_id,
            ]
        )

    # Once `SyntaxArg.arg_proto_code_abs_file_path` is specified, it is never changed (no need to override):
    if (proto_code_abs_file_path is not None) and (
        SyntaxArg.arg_proto_code_abs_file_path not in exec_argv
    ):
        exec_argv.extend(
            [
                SyntaxArg.arg_proto_code_abs_file_path,
                proto_code_abs_file_path,
            ]
        )

    if wizard_stage != WizardStage.wizard_started:
        exec_argv.extend(
            [
                SyntaxArg.arg_wizard_stage,
                wizard_stage.value,
            ]
        )

    if required_environ is None:
        required_environ = os.environ.copy()

    required_environ[EnvVar.var_PROTOPRIMER_PY_EXEC.value] = next_py_exec.name

    logger.info(f"exec_argv: {exec_argv}")
    os.execve(
        path=next_python_path,
        argv=exec_argv,
        env=required_environ,
    )


def print_delegate_line(
    arg_list: list[str],
    stderr_log_handler: logging.Handler,
) -> None:

    color_delegate = (
        f"{TermColor.back_dark_blue.value}{TermColor.fore_bright_white.value}"
    )
    color_reset = TermColor.reset_style.value

    is_reportable: bool = stderr_log_handler.level <= logging.INFO
    if is_reportable:
        command_line = get_shell_command_line(arg_list)
        print(
            f"{color_delegate}DELEGATE{color_reset}: {command_line}",
            file=sys.stderr,
            flush=True,
        )


def get_file_name_timestamp():
    """
    Generate a timestamp acceptable to be embedded into a filename.
    """

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    # Format: "YYYY_MM_DD_HH_MM_SSZ"
    file_timestamp = now_utc.strftime("%Y_%m_%d_%H_%M_%S") + "Z"
    return file_timestamp


def get_default_start_id():
    return f"{get_file_name_timestamp()}.{os.getpid()}"


def create_temp_file():
    # TODO: avoid generating new temp file (use configured location):
    temp_file = tempfile.NamedTemporaryFile(
        mode="w+t",
        encoding="utf-8",
        delete=False,
    )
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
    return get_shell_command_line(sys.argv)


def get_shell_command_line(arg_list: list[str]):
    command_line = " ".join(shlex.quote(arg_item) for arg_item in arg_list)
    return command_line


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
        file_obj.write("\n")


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
        # This extra banner fixes the issue of fighting `pre-commit` plugins
        # when the previous new line is a trailing one
        # (trailing line is normally removed by `pre-commit`):
        f"{insert_text}"
        + "\n"
    )


def install_editable_project(
    ref_root_dir_abs_path: str,
    project_descriptors: list[dict],
    constraints_txt_path: str,
):
    """
    Install each project from the `project_descriptors`.

    The assumption is that they use `pyproject.toml`.

    The result is equivalent of:
    ```sh
    path/to/python -m pip --editable path/to/project/a --editable path/to/project/b --editable path/to/project/c ...
    ```

    FT_46_37_27_11.editable_install.md
    """

    editable_project_install_args = []
    for project_descriptor in project_descriptors:
        project_build_root_dir_rel_path = project_descriptor[
            ConfField.field_env_build_root_dir_rel_path.value
        ]
        project_build_root_dir_abs_path = os.path.join(
            ref_root_dir_abs_path,
            project_build_root_dir_rel_path,
        )

        install_extras: list[str]
        if ConfField.field_env_install_extras.value in project_descriptor:
            install_extras = project_descriptor[
                ConfField.field_env_install_extras.value
            ]
        else:
            install_extras = []

        editable_project_install_args.append("--editable")
        if len(install_extras) > 0:
            editable_project_install_args.append(
                f"{project_build_root_dir_abs_path}[{','.join(install_extras)}]"
            )
        else:
            editable_project_install_args.append(f"{project_build_root_dir_abs_path}")

    sub_proc_args = [
        get_path_to_curr_python(),
        "-m",
        "pip",
        "install",
        "--constraint",
        constraints_txt_path,
    ]

    sub_proc_args.extend(editable_project_install_args)

    logger.info(f"installing projects: {' '.join(sub_proc_args)}")

    subprocess.check_call(sub_proc_args)


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


def if_none(
    given_value: ValueType | None,
    default_value: ValueType,
) -> ValueType:
    if given_value is None:
        return default_value
    else:
        return given_value


def is_venv() -> bool:
    # TODO: assert VIRTUAL_ENV or not assert?
    if sys.prefix != sys.base_prefix:
        # assert os.environ["VIRTUAL_ENV"]
        return True
    else:
        # assert not os.environ["VIRTUAL_ENV"]
        return False


def log_python_context(log_level: int = logging.INFO):
    logger.log(
        log_level,
        f"`{ConfConstInput.ext_env_var_VIRTUAL_ENV}`: {os.environ.get(ConfConstInput.ext_env_var_VIRTUAL_ENV, None)}",
    )
    logger.log(
        log_level,
        f"`{ConfConstInput.ext_env_var_PATH}`: {os.environ.get(ConfConstInput.ext_env_var_PATH, None)}",
    )
    logger.log(
        log_level,
        f"`{ConfConstInput.ext_env_var_PYTHONPATH}`: {os.environ.get(ConfConstInput.ext_env_var_PYTHONPATH, None)}",
    )
    logger.log(
        log_level,
        f"`sys.path`: {sys.path}",
    )
    logger.log(
        log_level,
        f"`sys.prefix`: {sys.prefix}",
    )
    logger.log(
        log_level,
        f"`sys.base_prefix`: {sys.base_prefix}",
    )
    logger.log(
        log_level,
        f"`sys.executable`: {sys.executable}",
    )


def warn_if_non_venv_package_installed():
    """
    Implements UC_88_09_19_74.no_installation_outside_venv.md:
    warns if the `protoprimer` is a package installed (outside `venv`).
    """
    assert not is_venv()

    try:
        pip_show_output = subprocess.check_output(
            [
                sys.executable,
                "-m",
                "pip",
                "show",
                ConfConstGeneral.name_protoprimer_package,
            ],
            text=True,
            stderr=subprocess.PIPE,
        )

        package_location: str | None = None
        for output_line in pip_show_output.splitlines():
            if output_line.startswith("Location:"):
                package_location = output_line.split(":", 1)[1].strip()
                break

        if package_location:
            log_python_context()
            # TODO: Figure out why `test_plain_proto_code_in_wizard_mode.py` complains here:
            logger.warning(
                f"The `{ConfConstGeneral.name_protoprimer_package}` package is installed outside of `venv`."
            )

    except subprocess.CalledProcessError:
        # `pip show` returns non-zero exit code if package is not found.
        # This is the expected case.
        pass


def delegate_to_venv(
    # TODO: TODO_28_48_19_20.api_to_traverse_config_when_primed.md:
    #       See usage - find a way to automatically provide it given the path to the `proto_kernel`.
    ref_root_abs_path: str,
) -> bool:
    """
    This is a helper function to delegate script execution to a `python` from `venv`.

    It is supposed to be used in FT_75_87_82_46 entry scripts.
    The entry script must know how to compute the path to `ref_root_path`
    (e.g., it must know its path within the client dir structure).

    The function fails if `venv` is not created - the user must trigger the bootstrap manually.

    :return: `False` if already inside `venv`, otherwise start itself inside `venv`.
    """

    if not is_venv():

        venv_bin = os.path.join(
            ref_root_abs_path,
            # TODO: This might be passed as arg to the func (that being a default):
            ConfConstEnv.default_dir_rel_path_venv,
            ConfConstGeneral.file_rel_path_venv_bin,
        )
        venv_python = os.path.join(
            ref_root_abs_path,
            # TODO: This might be passed as arg to the func (that being a default):
            ConfConstEnv.default_dir_rel_path_venv,
            ConfConstGeneral.file_rel_path_venv_python,
        )

        if not os.path.exists(venv_python):
            raise AssertionError(
                f"`{venv_python}` does not exist - has `venv` been bootstrapped?"
            )

        # Equivalent of `./venv/bin/activate` to configure `PATH` env var:
        os.environ[ConfConstInput.ext_env_var_PATH] = (
            venv_bin + os.pathsep + os.environ.get(ConfConstInput.ext_env_var_PATH, "")
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


def run_main(
    neo_main_module: str,
    neo_main_function: str,
):
    """
    Implements FT_14_52_73_23.primer_runtime.md transition
    from `PrimerRuntime.runtime_proto` to `PrimerRuntime.runtime_neo`.
    If `ImportError` occurs (when `venv` is not ready), it falls back to running `main` from `proto_kernel`.
    """
    try:
        # `PrimerRuntime.runtime_neo`:
        custom_module = importlib.import_module(neo_main_module)
        selected_main = getattr(custom_module, neo_main_function)
    except ImportError:
        py_exec = PythonExecutable[
            os.getenv(
                EnvVar.var_PROTOPRIMER_PY_EXEC.value,
                ConfConstInput.default_PROTOPRIMER_PY_EXEC,
            )
        ]
        if py_exec.value >= PythonExecutable.py_exec_updated_client_package.value:
            raise AssertionError(
                f"Failed to import `{neo_main_module}` with `{EnvVar.var_PROTOPRIMER_PY_EXEC.value}` [{py_exec.name}]."
                f"Does install process contain `{neo_main_module}` or has it as a (transitive) dependency?"
            )
        # `PrimerRuntime.runtime_proto`:
        selected_main = main

    selected_main()


if __name__ == "__main__":
    main()
