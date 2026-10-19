from __future__ import annotations

import os
import pathlib
import subprocess
import sys

from local_contract_compatibility.mode_id import ModeId

# Old `local_*` packages which are installed from the baseline worktree (when present there):
old_local_package_names = [
    "local_test",
    "local_repo",
    "local_doc",
]


# Perimeter dirs (under `test_<package_name>`) which have their own `test_contract_compatibility` dir:
contract_perimeter_dir_names = [
    "test_slow_integrated",
    "test_fast_not_mocked",
]


def get_contract_test_dir_rel_paths(package_name: str) -> list[pathlib.Path]:
    return [pathlib.Path("src") / package_name / "test" / f"test_{package_name}" / perimeter_dir_name / "test_contract_compatibility" for perimeter_dir_name in contract_perimeter_dir_names]


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
    contract_test_dir_rel_paths: list[pathlib.Path] | None = None,
) -> int:
    """
    Runs the contract tests of the old `commit_name` (from its `git worktree`) against the current `package_name`.

    Only the dirs which exist in the old `commit_name` are run (older ones may lack some), at least one must exist.

    FT_78_72_23_04.backward_compatibility.md
    """

    commit_id = resolve_commit_id(repo_dir_abs_path, commit_name)
    commit_dir_abs_path = scratch_dir_abs_path / commit_id
    worktree_abs_path = commit_dir_abs_path / "worktree"
    ensure_worktree(repo_dir_abs_path, commit_id, worktree_abs_path)
    venv_python_abs_path = ensure_venv(repo_dir_abs_path, package_name, worktree_abs_path, commit_dir_abs_path / "venv")

    if contract_test_dir_rel_paths is None:
        contract_test_dir_rel_paths = get_contract_test_dir_rel_paths(package_name)
    existing_dir_rel_paths = [dir_rel_path for dir_rel_path in contract_test_dir_rel_paths if (worktree_abs_path / dir_rel_path).is_dir()]
    if not existing_dir_rel_paths:
        raise AssertionError(f"commit name [{commit_name}] ({commit_id}) has none of [{', '.join(str(dir_rel_path) for dir_rel_path in contract_test_dir_rel_paths)}]")

    # `CI` is required, otherwise `test_slow_integrated` tests are skipped:
    sub_env = dict(os.environ)
    sub_env["CI"] = "true"
    exit_code = subprocess.run(
        [str(venv_python_abs_path), "-m", "pytest", "-p", "no:cacheprovider"] + [str(dir_rel_path) for dir_rel_path in existing_dir_rel_paths] + pytest_args,
        cwd=str(worktree_abs_path),
        env=sub_env,
    ).returncode

    if exit_code != 0:
        print(
            f"FAILED: mode [{ModeId.old_tests_on_new_changes.value}], commit name [{commit_name}] ({commit_id}): " f"the changes break backward compatibility tests in the baseline - possible actions: " f"[A] fix changes to comply [B] update the baseline",
            file=sys.stderr,
        )
    return exit_code
