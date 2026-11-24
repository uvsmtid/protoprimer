from __future__ import annotations

import os
import pathlib
import subprocess
import sys

from local_contract_compatibility.mode_id import ModeId
from local_contract_compatibility.run_mode_tests import run_pytest_for_mode
from local_test.coverage_conf import coverage_dir_env_var
from local_test.venv_path_helper import compose_venv_python_abs_path

# Old `local_*` packages which are installed from the baseline worktree (all must be present there):
old_local_package_names = [
    "local_test",
    "local_repo",
    "local_doc",
    "local_config_schema",
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
    """
    Resolves `commit_name` (id, tag, local branch) to a commit id.

    A branch which exists only on the remote (e.g. a fresh `actions/checkout` has no local branches)
    is resolved as `origin/<commit_name>`.
    """

    for candidate_name in [commit_name, f"origin/{commit_name}"]:
        resolved = subprocess.run(
            ["git", "rev-parse", "--verify", f"{candidate_name}^{{commit}}"],
            cwd=str(repo_dir_abs_path),
            capture_output=True,
            text=True,
        )
        if resolved.returncode == 0:
            return resolved.stdout.strip()
    raise ValueError(f"commit name [{commit_name}] is neither a local commit name nor [origin/{commit_name}]")


def ensure_worktree(
    repo_dir_abs_path: pathlib.Path,
    commit_id: str,
    worktree_abs_path: pathlib.Path,
) -> None:
    if worktree_abs_path.exists():
        return
    subprocess.run(
        # Windows limits the path length (the worktree is nested deep in the cache dir):
        ["git", "-c", "core.longpaths=true", "worktree", "add", "--detach", str(worktree_abs_path), commit_id],
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

    venv_python_abs_path = pathlib.Path(compose_venv_python_abs_path(str(venv_abs_path)))
    if venv_python_abs_path.exists():
        return venv_python_abs_path

    subprocess.run([sys.executable, "-m", "venv", str(venv_abs_path)], check=True)
    missing_package_names = [old_package_name for old_package_name in old_local_package_names if not (worktree_abs_path / "src" / old_package_name).is_dir()]
    if missing_package_names:
        raise AssertionError(f"worktree [{worktree_abs_path}] has no [{', '.join(missing_package_names)}]: the baseline is not established")
    install_args = [str(worktree_abs_path / "src" / old_package_name) for old_package_name in old_local_package_names]
    install_args += ["-e", f"{repo_dir_abs_path / 'src' / package_name}[test]"]
    # FT_47_61_24_68.combined_coverage.md: `coverage` is needed to measure the current code:
    if os.environ.get(coverage_dir_env_var):
        install_args += ["coverage"]
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

    Every contract dir must exist in the old `commit_name`, otherwise the baseline is not established (fails).

    FT_78_72_23_04.backward_compatibility.md
    """

    commit_id = resolve_commit_id(repo_dir_abs_path, commit_name)
    commit_dir_abs_path = scratch_dir_abs_path / commit_id
    worktree_abs_path = commit_dir_abs_path / "worktree"
    ensure_worktree(repo_dir_abs_path, commit_id, worktree_abs_path)

    if contract_test_dir_rel_paths is None:
        contract_test_dir_rel_paths = get_contract_test_dir_rel_paths(package_name)
    missing_dir_rel_paths = [dir_rel_path for dir_rel_path in contract_test_dir_rel_paths if not (worktree_abs_path / dir_rel_path).is_dir()]
    if missing_dir_rel_paths:
        raise AssertionError(f"commit name [{commit_name}] ({commit_id}) has no [{', '.join(str(dir_rel_path) for dir_rel_path in missing_dir_rel_paths)}]: the baseline is not established")

    venv_python_abs_path = ensure_venv(repo_dir_abs_path, package_name, worktree_abs_path, commit_dir_abs_path / "venv")

    return run_pytest_for_mode(
        ModeId.old_tests_on_new_changes,
        venv_python_abs_path,
        worktree_abs_path,
        contract_test_dir_rel_paths,
        commit_name,
        commit_id,
        pytest_args,
        repo_dir_abs_path=repo_dir_abs_path,
    )
