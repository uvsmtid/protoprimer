from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
import time

logger = logging.getLogger()


def get_workflow_file_rel_path(
    workflow_name: str,
) -> str:
    return f".github/workflows/{workflow_name}.yaml"


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
    .github/workflows/cover_finish.yaml
    """

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    parsed_args = init_arg_parser().parse_args()

    is_ready = wait_for_workflow_runs(
        parsed_args.repo,
        parsed_args.commit_sha,
        parsed_args.workflow_names,
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
        "workflow_names",
        nargs="+",
        help="Workflow file names without the `.yaml` extension.",
    )
    return arg_parser


if __name__ == "__main__":
    custom_main()
