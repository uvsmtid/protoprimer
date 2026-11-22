from __future__ import annotations

import argparse
import contextlib
import glob
import logging
import os
import pathlib
import subprocess
import sys
import sysconfig

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


@contextlib.contextmanager
def installed_coverage_hook(
    repo_dir_abs_path: pathlib.Path,
):
    """
    Installs the coverage hook as `sitecustomize.py` into the stdlib dir of the current `python` (shared by `venv`-s):
    it starts `coverage` in every `python` process (the tests start many) - `PYTHONPATH` is ignored by isolated `-I` mode.

    Yields `True` if installed (it is removed on exit), `False` otherwise (never overwrites an existing `sitecustomize.py`).
    """

    # Not imported at the top: `local_repo` does not depend on `local_test` otherwise:
    from local_test.coverage_conf import (
        get_coverage_hook_script,
        get_rcfile_abs_path,
        read_source_dir_rel_paths,
    )

    stdlib_dir_path = pathlib.Path(sysconfig.get_paths()["stdlib"])
    hook_file_path = stdlib_dir_path / "sitecustomize.py"
    if hook_file_path.exists():
        logger.warning(f"[{hook_file_path}] already exists: subprocesses are not measured")
        yield False
        return

    try:
        hook_file_path.write_text(
            get_coverage_hook_script(
                config_file=str(get_rcfile_abs_path(repo_dir_abs_path)),
                source_dir_paths=[str(repo_dir_abs_path / source_dir_rel_path) for source_dir_rel_path in read_source_dir_rel_paths(repo_dir_abs_path)],
            )
        )
    except OSError as os_error:
        logger.warning(f"cannot write [{hook_file_path}] ({os_error}): subprocesses are not measured")
        yield False
        return

    try:
        yield True
    finally:
        hook_file_path.unlink()
        for pyc_file_path in glob.glob(str(stdlib_dir_path / "__pycache__" / "sitecustomize.*.pyc")):
            os.remove(pyc_file_path)


def run_pytest_with_subprocess_coverage(
    test_paths: list[str],
) -> int:
    """
    Runs plain `pytest` (not `coverage run`): the hook measures every `python` process including this one.

    Falls back to `coverage run` (the process of `pytest` only) if the hook cannot be installed.
    """

    repo_dir_abs_path = pathlib.Path.cwd()
    with installed_coverage_hook(repo_dir_abs_path) as is_installed:
        if not is_installed:
            return run_coverage("run", "--module", "pytest", *test_paths)
        sub_env = dict(os.environ)
        # Absolute: subprocesses start in other current dirs (`parallel = true` adds a suffix per process):
        sub_env["COVERAGE_FILE"] = str(repo_dir_abs_path / ".coverage")
        return subprocess.run([sys.executable, "-m", "pytest", *test_paths], env=sub_env).returncode


def custom_main():
    """
    See also:
    FT_47_61_24_68.combined_coverage.md
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

    if parsed_args.subprocesses:
        exit_code = run_pytest_with_subprocess_coverage(test_paths)
    else:
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
        "--subprocesses",
        action="store_true",
        help="Also measure `python` subprocesses of tests (a hook is installed into the stdlib of the current `python` while `pytest` runs).",
    )
    arg_parser.add_argument(
        "test_paths",
        nargs="*",
        help="Test paths to run.",
    )
    return arg_parser


if __name__ == "__main__":
    custom_main()
