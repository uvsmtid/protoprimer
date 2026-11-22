from __future__ import annotations

import argparse
import json
import logging
import os
import pathlib
import re
import subprocess
import sys
import time

logger = logging.getLogger()


def get_workflow_file_rel_path(
    workflow_name: str,
) -> str:
    return f".github/workflows/{workflow_name}.yaml"


# A step which uploads a coverage part to `coveralls.io` (not `parallel-finished: true` of the closing step):
parallel_upload_pattern = re.compile(r"^\s*parallel:\s*true\s*$")

# A workflow may upload via a local action: `uses: ./.github/actions/<name>`:
local_action_pattern = re.compile(r"^\s*(?:-\s*)?uses:\s*\./\.github/actions/([\w.-]+)\s*$")


def has_parallel_upload(
    yaml_text: str,
    action_names_with_upload: set[str],
) -> bool:
    for line in yaml_text.splitlines():
        if line.strip().startswith("#"):
            continue
        if parallel_upload_pattern.match(line):
            return True
        local_action_match = local_action_pattern.match(line)
        if local_action_match and local_action_match.group(1) in action_names_with_upload:
            return True
    return False


def find_uploading_workflow_names(
    repo_dir_path: pathlib.Path,
) -> list[str]:
    """
    Workflows (`.github/workflows/<name>.yaml`) which upload coverage as parallel parts, directly or via a local action.
    """

    actions_dir_path = repo_dir_path / ".github" / "actions"
    action_names_with_upload = {action_file_path.parent.name for action_file_path in actions_dir_path.glob("*/action.yaml") if has_parallel_upload(action_file_path.read_text(encoding="utf-8"), set())}
    return sorted(workflow_file_path.stem for workflow_file_path in (repo_dir_path / ".github" / "workflows").glob("*.yaml") if has_parallel_upload(workflow_file_path.read_text(encoding="utf-8"), action_names_with_upload))


def get_workflow_runs(
    repo: str,
    commit_sha: str,
) -> list[dict]:
    """
    Runs of all workflows triggered by `push` for the commit (needs `gh` and `GH_TOKEN`).
    """

    api_output = subprocess.run(
        ["gh", "api", f"repos/{repo}/actions/runs?head_sha={commit_sha}&event=push&per_page=100"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return json.loads(api_output)["workflow_runs"]


def find_not_ready(
    workflow_runs: list[dict],
    workflow_names: list[str],
) -> dict[str, str]:
    """
    Maps a workflow name to the reason it is not ready (no entry means ready).

    A workflow is ready when at least one run exists (it may be not created yet)
    and all its runs (re-runs included) are completed.
    """

    not_ready: dict[str, str] = {}
    for workflow_name in workflow_names:
        file_rel_path = get_workflow_file_rel_path(workflow_name)
        statuses = [workflow_run["status"] for workflow_run in workflow_runs if workflow_run["path"] == file_rel_path]
        if not statuses:
            not_ready[workflow_name] = "no runs yet"
        elif any(status != "completed" for status in statuses):
            not_ready[workflow_name] = "not completed"
    return not_ready


def wait_for_workflow_runs(
    repo: str,
    commit_sha: str,
    workflow_names: list[str],
    timeout_sec: float,
    poll_sec: float,
) -> bool:
    """
    Returns `True` when all `workflow_names` are ready, `False` on timeout.
    """

    deadline = time.monotonic() + timeout_sec
    while True:
        not_ready = find_not_ready(get_workflow_runs(repo, commit_sha), workflow_names)
        for workflow_name in workflow_names:
            logger.info(f"{workflow_name}: {not_ready.get(workflow_name, 'completed')}")
        if not not_ready:
            return True
        if time.monotonic() >= deadline:
            logger.error(f"timed out waiting for workflows: {sorted(not_ready)}")
            return False
        time.sleep(poll_sec)


def custom_main():
    """
    See also:
    FT_47_61_24_68.combined_coverage.md
    .github/workflows/cover_finish.yaml
    """

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    parsed_args = init_arg_parser().parse_args()

    workflow_names = parsed_args.workflow_names or find_uploading_workflow_names(pathlib.Path(parsed_args.repo_dir))
    if not workflow_names:
        raise AssertionError(f"no workflows with parallel coverage upload found in [{parsed_args.repo_dir}]")
    logger.info(f"workflows to wait for: {workflow_names}")

    is_ready = wait_for_workflow_runs(
        parsed_args.repo,
        parsed_args.commit_sha,
        workflow_names,
        parsed_args.timeout_minutes * 60,
        parsed_args.poll_seconds,
    )
    sys.exit(0 if is_ready else 1)


def init_arg_parser():

    arg_parser = argparse.ArgumentParser(
        description="Wait until all workflows (by `.github/workflows/<name>.yaml`) have completed runs for the commit pushed.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    arg_parser.add_argument(
        "--repo",
        default=os.environ.get("GITHUB_REPOSITORY"),
        help="`<owner>/<name>`.",
    )
    arg_parser.add_argument(
        "--commit_sha",
        default=os.environ.get("GITHUB_SHA"),
        help="Commit the workflows run for.",
    )
    arg_parser.add_argument(
        "--timeout_minutes",
        type=float,
        default=40,
    )
    arg_parser.add_argument(
        "--poll_seconds",
        type=float,
        default=30,
    )
    arg_parser.add_argument(
        "--repo_dir",
        default=".",
        help="Repo root to find the workflows in (used when no `workflow_names` are given).",
    )
    arg_parser.add_argument(
        "workflow_names",
        nargs="*",
        help="Workflow file names without the `.yaml` extension (default: all which upload coverage as parallel parts).",
    )
    return arg_parser


if __name__ == "__main__":
    custom_main()
