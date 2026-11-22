from __future__ import annotations

import argparse
import logging
import os
import subprocess
import sys

from protoprimer.primer_kernel import _ConfDst

logger = logging.getLogger()

rcfile_rel_path = os.path.join(".", _ConfDst.dst_global.value, "coveragerc.ini")

# Default tests (when neither `--all_tests` nor `--tests_file` nor `test_paths` is given):
default_test_dir_rel_paths = [
    os.path.join(".", "src", "metaprimer", "test"),
    os.path.join(".", "src", "protoprimer", "test"),
]


def read_tests_file(tests_file_path: str) -> list[str]:
    """
    One path per line, empty lines and lines starting with `#` are skipped.
    """
    with open(tests_file_path, encoding="utf-8") as tests_file:
        return [line.strip() for line in tests_file if line.strip() and not line.strip().startswith("#")]


def run_coverage(
    sub_command: str,
    *sub_command_args: str,
) -> int:
    # The current `python` (from `venv`): cross-platform, no `shell`, no `PATH` lookup
    # (`--rcfile` goes right after the sub-command: the rest may be args of the program run by `coverage run`):
    return subprocess.run(
        [sys.executable, "-m", "coverage", sub_command, f"--rcfile={rcfile_rel_path}", *sub_command_args],
    ).returncode


def custom_main():
    """
    See also:
    .github/actions/test_env_posix/action.yaml
    .github/actions/test_env_windows/action.yaml
    """

    parsed_args = init_arg_parser().parse_args()

    if parsed_args.all_tests:
        test_paths = []
    else:
        test_paths = list(parsed_args.test_paths)
        if parsed_args.tests_file:
            test_paths += read_tests_file(parsed_args.tests_file)
        if not test_paths:
            test_paths = default_test_dir_rel_paths

    exit_code = run_coverage("erase")
    if exit_code != 0:
        sys.exit(exit_code)

    exit_code = run_coverage("run", "--module", "pytest", *test_paths)
    if exit_code != 0:
        # Do not report coverage of failed tests:
        sys.exit(exit_code)

    exit_code = run_coverage("combine")
    if exit_code != 0:
        sys.exit(exit_code)

    if parsed_args.lcov_file:
        # Partial runs (some jobs run a subset of tests) must not fail on `fail_under` (the combined coverage is checked elsewhere):
        sys.exit(run_coverage("lcov", "--fail-under=0", "-o", parsed_args.lcov_file))

    sys.exit(run_coverage("report"))


def init_arg_parser():

    arg_parser = argparse.ArgumentParser(
        description="Report coverage.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    arg_parser.add_argument(
        "--all_tests",
        action="store_true",
        help="Run `pytest` without paths (all tests under the current dir).",
    )
    arg_parser.add_argument(
        "--tests_file",
        help="File with test paths: one per line, empty lines and lines starting with `#` are skipped.",
    )
    arg_parser.add_argument(
        "--lcov_file",
        help="Write `lcov` report to this file (instead of `report`) - the format for parallel upload to `coveralls.io`.",
    )
    arg_parser.add_argument(
        "test_paths",
        nargs="*",
        help="Test paths to run.",
    )
    return arg_parser


if __name__ == "__main__":
    custom_main()
