from __future__ import annotations

import os
import pathlib
import subprocess
import sys

mode_id = "old_tests_on_new_changes"

# Old `local_*` packages which are installed from the baseline worktree (when present there):
old_local_package_names = [
    "local_test",
    "local_repo",
    "local_doc",
]


def get_contract_test_dir_rel_path(package_name: str) -> pathlib.Path:
    return pathlib.Path("src") / package_name / "test" / f"test_{package_name}" / "test_slow_integrated" / "test_contract_compatibility"


def resolve_commit_id(
    repo_dir_abs_path: pathlib.Path,
    commit_name: str,
) -> str:
    return subprocess.run(
        ["git", "rev-parse", "--verify", f"{commit_name}^{{commit}}"],
        cwd=str(repo_dir_abs_path),
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def ensure_worktree(
    repo_dir_abs_path: pathlib.Path,
    commit_id: str,
    worktree_abs_path: pathlib.Path,
) -> None:
    if worktree_abs_path.exists():
        return
    subprocess.run(
        ["git", "worktree", "add", "--detach", str(worktree_abs_path), commit_id],
        cwd=str(repo_dir_abs_path),
        check=True,
    )


def remove_worktree(
    repo_dir_abs_path: pathlib.Path,
    worktree_abs_path: pathlib.Path,
) -> None:
    subprocess.run(
        ["git", "worktree", "remove", "--force", str(worktree_abs_path)],
        cwd=str(repo_dir_abs_path),
        check=True,
    )


def ensure_venv(
    repo_dir_abs_path: pathlib.Path,
    package_name: str,
    worktree_abs_path: pathlib.Path,
    venv_abs_path: pathlib.Path,
) -> pathlib.Path:
    """
    Creates `venv` with the old `local_*` packages (from the worktree) and the current `protoprimer` (editable).
    """

    venv_python_abs_path = venv_abs_path / "bin" / "python"
    if venv_python_abs_path.exists():
        return venv_python_abs_path

    subprocess.run([sys.executable, "-m", "venv", str(venv_abs_path)], check=True)
    install_args = [
        str(worktree_abs_path / "src" / package_name)
        for package_name in old_local_package_names
        if (worktree_abs_path / "src" / package_name).exists()
        #
    ]
    install_args += ["-e", f"{repo_dir_abs_path / 'src' / package_name}[test]"]
    subprocess.run([str(venv_python_abs_path), "-m", "pip", "install", "-q"] + install_args, check=True)
    return venv_python_abs_path


def run_old_tests_on_new_changes(
    repo_dir_abs_path: pathlib.Path,
    package_name: str,
    commit_name: str,
    scratch_dir_abs_path: pathlib.Path,
    pytest_args: list[str],
) -> int:
    """
    Runs the contract tests of the old `commit_name` (from its `git worktree`) against the current `package_name`.
    """

    commit_id = resolve_commit_id(repo_dir_abs_path, commit_name)
    commit_dir_abs_path = scratch_dir_abs_path / commit_id
    worktree_abs_path = commit_dir_abs_path / "worktree"
    ensure_worktree(repo_dir_abs_path, commit_id, worktree_abs_path)
    venv_python_abs_path = ensure_venv(repo_dir_abs_path, package_name, worktree_abs_path, commit_dir_abs_path / "venv")

    contract_test_dir_rel_path = get_contract_test_dir_rel_path(package_name)
    if not (worktree_abs_path / contract_test_dir_rel_path).is_dir():
        raise AssertionError(f"commit name [{commit_name}] ({commit_id}) has no [{contract_test_dir_rel_path}]")

    # `CI` is required, otherwise `test_slow_integrated` tests are skipped:
    sub_env = dict(os.environ)
    sub_env["CI"] = "true"
    exit_code = subprocess.run(
        [str(venv_python_abs_path), "-m", "pytest", "-p", "no:cacheprovider", str(contract_test_dir_rel_path)] + pytest_args,
        cwd=str(worktree_abs_path),
        env=sub_env,
    ).returncode

    if exit_code != 0:
        print(
            f"FAILED: mode [{mode_id}], category [{contract_test_dir_rel_path.name}], commit name [{commit_name}] ({commit_id}): " f"the changes break backward compatibility tests in the baseline - possible actions: " f"[A] fix changes to comply [B] update the baseline",
            file=sys.stderr,
        )
    return exit_code
