import pathlib
import subprocess

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
        worktree = tmp_path / commit_id / "worktree"
        if worktree.exists():
            remove_worktree(repo_dir, worktree)
