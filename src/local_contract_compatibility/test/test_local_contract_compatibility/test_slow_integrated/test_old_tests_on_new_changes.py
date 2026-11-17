import pathlib
import subprocess

import pytest

from local_contract_compatibility.old_tests_on_new_changes import (
    remove_worktree,
    resolve_commit_id,
    run_old_tests_on_new_changes,
)


def get_repo_dir() -> pathlib.Path:
    return pathlib.Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True).stdout.strip())


def test_old_tests_on_new_changes_for_head(tmp_path: pathlib.Path):
    """
    `HEAD` as the baseline runs the same tests as `new_tests_on_new_changes` (it cannot detect breaks).
    """

    # given:
    repo_dir = get_repo_dir()
    commit_id = resolve_commit_id(repo_dir, "HEAD")

    try:
        # when:
        exit_code = run_old_tests_on_new_changes(
            repo_dir,
            "protoprimer",
            "HEAD",
            tmp_path,
            # a light test only:
            ["-k", "test_plain_proto_kernel_help"],
        )

        # then:
        assert exit_code == 0
    finally:
        worktree_abs_path = tmp_path / commit_id / "worktree"
        if worktree_abs_path.exists():
            remove_worktree(repo_dir, worktree_abs_path)


def test_old_tests_on_new_changes_fails_on_missing_contract_dir(tmp_path: pathlib.Path):
    """
    A baseline without any of the contract dirs is not established: the runner fails (and builds no `venv`).
    """

    # given:
    repo_dir = get_repo_dir()
    commit_id = resolve_commit_id(repo_dir, "HEAD")

    try:
        # when/then:
        with pytest.raises(AssertionError, match="the baseline is not established"):
            run_old_tests_on_new_changes(
                repo_dir,
                "protoprimer",
                "HEAD",
                tmp_path,
                [],
                [pathlib.Path("no_such_contract_dir")],
            )
        assert not (tmp_path / commit_id / "venv").exists()
    finally:
        worktree_abs_path = tmp_path / commit_id / "worktree"
        if worktree_abs_path.exists():
            remove_worktree(repo_dir, worktree_abs_path)


def test_resolve_commit_id_falls_back_to_remote_branch(tmp_path: pathlib.Path):
    """
    A fresh `actions/checkout` has no local branches: only `origin/<name>`.
    """

    # given:
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()

    def git(*args: str) -> str:
        return subprocess.run(
            ["git", "-c", "user.name=test", "-c", "user.email=test@example.com", *args],
            cwd=str(repo_dir),
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

    git("init", "-q")
    git("commit", "-q", "--allow-empty", "-m", "first")
    commit_id = git("rev-parse", "HEAD")
    git("update-ref", "refs/remotes/origin/remote_only_branch", commit_id)

    # when/then:
    assert resolve_commit_id(repo_dir, "remote_only_branch") == commit_id
    assert resolve_commit_id(repo_dir, "HEAD") == commit_id

    with pytest.raises(ValueError):
        resolve_commit_id(repo_dir, "no_such_branch")
