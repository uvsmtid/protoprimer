from __future__ import annotations

import os
import pathlib
import subprocess
import sys

from local_contract_compatibility.mode_id import ModeId


def get_handoff_test_dir_rel_path(
    package_name: str,
    mode_id: ModeId,
) -> pathlib.Path:
    return pathlib.Path("src") / package_name / "test" / f"test_{package_name}" / "test_slow_integrated" / f"test_{mode_id.value}"


def run_pytest_for_mode(
    mode_id: ModeId,
    python_abs_path: pathlib.Path | str,
    cwd_abs_path: pathlib.Path,
    test_dir_rel_paths: list[pathlib.Path],
    commit_name: str,
    commit_id: str | None,
    pytest_args: list[str],
) -> int:
    """
    Runs `pytest` for `mode_id` and reports the failure message (the same for all modes).

    FT_78_72_23_04.backward_compatibility.md
    """

    # `CI` is required, otherwise `test_slow_integrated` tests are skipped:
    sub_env = dict(os.environ)
    sub_env["CI"] = "true"
    exit_code = subprocess.run(
        [str(python_abs_path), "-m", "pytest", "-p", "no:cacheprovider"] + [str(test_dir_rel_path) for test_dir_rel_path in test_dir_rel_paths] + pytest_args,
        cwd=str(cwd_abs_path),
        env=sub_env,
    ).returncode

    if exit_code != 0:
        commit_id_suffix = f" ({commit_id})" if commit_id else ""
        print(
            f"FAILED: mode [{mode_id.value}], commit name [{commit_name}]{commit_id_suffix}: the changes break backward compatibility tests in the baseline - possible actions:\n*   fix changes to comply\n*   update the baseline",
            file=sys.stderr,
        )
    return exit_code


def run_handoff_mode_tests(
    mode_id: ModeId,
    repo_dir_abs_path: pathlib.Path,
    package_name: str,
    commit_name: str,
    pytest_args: list[str],
) -> int:
    """
    Runs the tests of a handoff mode in the current tree (the old part comes from `commit_name`, see `--commit_name`).
    """

    test_dir_rel_path = get_handoff_test_dir_rel_path(package_name, mode_id)
    if not (repo_dir_abs_path / test_dir_rel_path).is_dir():
        raise AssertionError(f"[{test_dir_rel_path}] does not exist")

    return run_pytest_for_mode(
        mode_id,
        sys.executable,
        repo_dir_abs_path,
        [test_dir_rel_path],
        commit_name,
        None,
        ["--commit_name", commit_name] + pytest_args,
    )
