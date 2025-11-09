#!/usr/bin/env python3
import argparse

# The script creates a new `squashed_branch_name` from the current `source_branch_name`
# by squashing with all the comments against common ancestor with `target_branch`
# (e.g., first commit common with `origin/main`).
#
# The idea is to have a single script with no args to squash everything.

from local_repo.sub_proc_util import (
    get_command_code,
    get_command_output,
)


def main():

    parsed_args = init_arg_parser().parse_args()

    target_branch: str = "origin/main"
    squashed_tag: str = "SQUASHED"
    exit_code: int

    source_branch_name: str = get_command_output(f"git rev-parse --abbrev-ref HEAD")

    if not source_branch_name or source_branch_name == "HEAD":
        raise RuntimeError(
            f"Could not determine branch name. Are you in a detached HEAD state?"
        )

    # Fail on uncommitted changes:
    get_command_code(f"git diff --exit-code")
    get_command_code(f"git diff --exit-code --cached")
    get_command_code(f"git add .")
    exit_code = get_command_code(f"git diff --exit-code HEAD --", fail_on_error=False)
    if exit_code != 0:
        raise RuntimeError(f"Uncommitted changes")

    # Fail if `squashed_tag` is already present in the branch name:
    if squashed_tag in source_branch_name:
        raise RuntimeError(
            f"`squashed_tag` [{squashed_tag}] is already part of the `source_branch_name` [{source_branch_name}]"
        )

    # Fail if the previously squashed branch still exists (it has to be removed manually):
    existing_branches: str = get_command_output(
        f"git for-each-ref --format='%(refname:short)' refs/heads/"
    )
    squash_branch_prefix = f"{source_branch_name}.{squashed_tag}"
    if squash_branch_prefix in existing_branches:
        raise RuntimeError(
            f"A branch prefixed with [{squash_branch_prefix}] already exists. Please remove it manually."
        )

    # Abbreviated commit id:
    git_short_commit = get_command_output(f"git rev-parse --short HEAD")

    # Name squashed branch with clear tag and abbreviated commit id:
    squashed_branch_name = f"{source_branch_name}.{squashed_tag}.{git_short_commit}"

    # Find a common ancestor between source branch and target branch
    # (basically, this is where the source branch was branched off from the trunk):
    git_base_commit = get_command_output(f"git merge-base HEAD {target_branch}")

    # Use separate branch to squash:
    get_command_code(f"git checkout -b {squashed_branch_name} HEAD")

    # Squash by staging for commit:
    get_command_code(f"git reset --soft {git_base_commit}")

    # Use the branch name as the commit message:
    get_command_code(f'git commit -m "{source_branch_name}"')

    # Fetch before force-push:
    get_command_code(f"git fetch")

    # Push:
    get_command_code(f'git push -f origin "HEAD:{source_branch_name}"')

    # Set the remote target branch named after the source branch:
    get_command_code(f'git branch --set-upstream-to="origin/{source_branch_name}"')

    # Clean up:
    get_command_code(f"git checkout {source_branch_name}")
    get_command_code(f"git branch -D {squashed_branch_name}")


def init_arg_parser():

    arg_parser = argparse.ArgumentParser(
        description=(
            "Squash commits of the current branch against the target branch and "
            "push that commit to the remote as the current branch. "
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    return arg_parser


if __name__ == "__main__":
    main()
