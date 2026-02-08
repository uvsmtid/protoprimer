from __future__ import annotations

import argparse
import os
import pathlib
import sys
from contextlib import contextmanager

import pytest

from local_test.mock_environ import mock_and_restore_environ
from protoprimer.primer_kernel import (
    EnvVar,
    str_to_bool,
)

integ_env_var = "CI"


def any_to_bool(v) -> bool:
    """
    Checks if integration tests enabled = if the `CI` environment variable is set to `true`.
    """

    if v is None:
        return False
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        if len(v) == 0:
            return False
        else:
            return str_to_bool(v)
    raise argparse.ArgumentTypeError(
        f"Unable to convert type [{type(v)}] to [{bool.__name__}]."
    )


is_integ_run = any_to_bool(os.environ.get(integ_env_var))


def skip_test_slow_integrated(
    parent_dir_abs_path: str,
    pytest_config,
    pytest_items,
):
    """
    Skips all collected tests in this directory and its sub-directories if integration tests are not enabled.

    See: FT_83_60_72_19.test_perimeter.md / test_slow_integrated
    """

    reason_text = (
        f"Tests under `{parent_dir_abs_path}` skipped by default. "
        f"Run with environment variable `{integ_env_var}` set to `true` to enable. "
    )

    if not is_integ_run:

        skip_int_marker = pytest.mark.skip(reason=reason_text)

        for pytest_item in pytest_items:

            test_path: pathlib.Path
            if hasattr(pytest_item, "path"):
                test_path = pytest_item.path
            else:
                # legacy:
                test_path = pathlib.Path(pytest_item.fspath)

            if str(test_path.resolve()).startswith(
                str(pathlib.Path(parent_dir_abs_path).resolve())
            ):
                pytest_item.add_marker(skip_int_marker)


@contextmanager
def set_protoprimer_debug_log_level():
    """
    Set debug level (especially for `app_starter` which cannot take args for `protoprimer`).
    """
    with mock_and_restore_environ():
        os.environ[EnvVar.var_PROTOPRIMER_STDERR_LOG_LEVEL.value] = "debug"
        yield


def is_min_python():
    """
    See: FT_84_11_73_28.supported_python_versions.md

    TODO: TODO_18_22_12_97.run_all_tests_under_min_python.md: there should not be such condition.
    """
    # 3.8 = min python 3.7 + 0.1:
    return sys.version_info < (3, 8)


requires_max_python = pytest.mark.skipif(
    is_min_python(),
    reason="The test is disabled for min python version (see FT_84_11_73_28.supported_python_versions.md).",
)
