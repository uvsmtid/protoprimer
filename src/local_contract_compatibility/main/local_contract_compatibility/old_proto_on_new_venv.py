from __future__ import annotations

import pathlib
import subprocess

from local_contract_compatibility.mode_id import ModeId
from local_contract_compatibility.run_mode_tests import run_handoff_mode_tests


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


def run_old_proto_on_new_venv(
    repo_dir_abs_path: pathlib.Path,
    package_name: str,
    commit_name: str,
    pytest_args: list[str],
) -> int:
    """
    Runs the `old_proto_on_new_venv` tests: an old `proto_kernel.py` (of `commit_name`) against the current `venv`.
    """

    return run_handoff_mode_tests(
        ModeId.old_proto_on_new_venv,
        repo_dir_abs_path,
        package_name,
        commit_name,
        pytest_args,
    )
