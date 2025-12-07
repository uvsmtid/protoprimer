from __future__ import annotations

import argparse
import os
import pathlib

import pytest

from protoprimer.primer_kernel import str_to_bool

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

            if test_path.is_relative_to(parent_dir_abs_path):
                pytest_item.add_marker(skip_int_marker)
