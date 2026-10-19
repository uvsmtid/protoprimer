from __future__ import annotations

import os
import pathlib
import subprocess
import sys

from local_contract_compatibility.mode_id import ModeId


def get_old_proto_kernel_rel_path() -> pathlib.Path:
    # The client-repo copy (with its generated boilerplate), not `primer_kernel.py`:
    # `old_tests_on_new_changes`/`create_plain_proto_kernel` only need a plain copy,
    # but `old_proto_on_new_venv` replays an actual historical `proto_kernel.py`.
    return pathlib.Path("src/proto_code/proto_kernel.py")


def extract_old_proto_kernel(
    repo_dir_abs_path: pathlib.Path,
    commit_name: str,
    dest_file_abs_path: pathlib.Path,
) -> pathlib.Path:
    """
    Overwrites `dest_file_abs_path` with `commit_name`'s committed `proto_kernel.py` via `git show`
    (no `git worktree` is needed for this mode, unlike `old_tests_on_new_changes`).
    """

    old_content = subprocess.run(
        ["git", "show", f"{commit_name}:{get_old_proto_kernel_rel_path()}"],
        cwd=str(repo_dir_abs_path),
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    dest_file_abs_path.write_text(old_content)
    return dest_file_abs_path


def get_test_dir_rel_path(package_name: str) -> pathlib.Path:
    return pathlib.Path("src") / package_name / "test" / f"test_{package_name}" / "test_slow_integrated" / "test_old_proto_on_new_venv"


def run_old_proto_on_new_venv(
    repo_dir_abs_path: pathlib.Path,
    package_name: str,
    commit_name: str,
    pytest_args: list[str],
) -> int:
    """
    Runs the `old_proto_on_new_venv` tests: an old `proto_kernel.py` (of `commit_name`) against the current `venv`.
    """

    test_dir_rel_path = get_test_dir_rel_path(package_name)
    if not (repo_dir_abs_path / test_dir_rel_path).is_dir():
        raise AssertionError(f"[{test_dir_rel_path}] does not exist")

    # `CI` is required, otherwise `test_slow_integrated` tests are skipped:
    sub_env = dict(os.environ)
    sub_env["CI"] = "true"
    exit_code = subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", str(test_dir_rel_path), "--commit_name", commit_name] + pytest_args,
        cwd=str(repo_dir_abs_path),
        env=sub_env,
    ).returncode

    if exit_code != 0:
        print(
            f"FAILED: mode [{ModeId.old_proto_on_new_venv.value}], commit name [{commit_name}]: " f"the changes break backward compatibility tests in the baseline - possible actions: " f"[A] fix changes to comply [B] update the baseline",
            file=sys.stderr,
        )
    return exit_code
