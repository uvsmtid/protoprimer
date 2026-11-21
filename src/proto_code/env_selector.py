from __future__ import annotations

import os
import re
import sys

# GitHub job id `test_py_{level}_{platform}` selects env dir `dst/test_python_{level}_{platform}`:
github_job_pattern = re.compile(r"test_py_(min|med|max)_([a-z]+)")

# GitHub jobs which use a test env without being a `test_py_*` job:
github_job_env_dirs = {
    "verify_contract_compatibility": "dst/test_python_max_linux",
    "invoke_condition_scenarios": "dst/test_python_max_linux",
}

# FT_84_11_73_28.supported_python_versions.md:
tested_python_levels = {
    (3, 7): "min",
    (3, 11): "med",
    (3, 15): "max",
}

tested_platforms = {
    "linux": "linux",
    "darwin": "darwin",
    "win32": "windows",
}


def select_env_dir_rel_path() -> str | None:
    """
    Implements `_SelectorFunc.select_env_dir_rel_path` from `protoprimer.primer_kernel`.
    """

    # `GITHUB_JOB` is only set by GitHub Actions:
    github_job = os.environ.get("GITHUB_JOB")
    if github_job is not None:
        if github_job in github_job_env_dirs:
            return github_job_env_dirs[github_job]

        job_match = github_job_pattern.fullmatch(github_job)
        if job_match is None:
            # Other GitHub jobs (lint, doc, ...) do not use test envs:
            return None

        # The env dir is not checked for existence here: a missing dir should fail loudly (in the kernel):
        return f"dst/test_python_{job_match.group(1)}_{job_match.group(2)}"

    # Outside GitHub Actions, only an explicit `CI=true` (e.g. local `docker` run) selects a test env:
    if os.environ.get("CI") != "true":
        return None

    # This file is in `src/proto_code/`:
    ref_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    return select_env_dir_rel_path_by_host(sys.version_info, sys.platform, ref_root)


def select_env_dir_rel_path_by_host(
    version_info: tuple,
    platform: str,
    ref_root: str,
) -> str | None:

    level = tested_python_levels.get((version_info[0], version_info[1]))
    platform_name = tested_platforms.get(platform)
    if level is None or platform_name is None:
        return None

    env_dir_rel_path = f"dst/test_python_{level}_{platform_name}"

    # A host guess is not an explicit choice: no such env dir means nothing is selected:
    if not os.path.isdir(os.path.join(ref_root, env_dir_rel_path)):
        return None

    return env_dir_rel_path
