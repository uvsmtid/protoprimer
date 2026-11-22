from __future__ import annotations

import os
import pathlib
import subprocess
import sys

from local_contract_compatibility.mode_id import ModeId
from protoprimer.primer_kernel import _ConfDst


def get_handoff_test_dir_rel_path(
    package_name: str,
    mode_id: ModeId,
) -> pathlib.Path:
    return pathlib.Path("src") / package_name / "test" / f"test_{package_name}" / "test_slow_integrated" / f"test_{mode_id.value}"


# TODO: TODO_29_67_72_68.combine_coverage_across_jobs.md: set to a dir to collect coverage of the current code (opt-in).
coverage_dir_env_var = "PROTOPRIMER_COVERAGE_DIR"

# The code which is measured (the same as `source` in `coveragerc.ini`, but absolute: `cwd` is not the repo for old tests):
coverage_source_dir_rel_paths = [
    "src/metaprimer/main",
    "src/protoprimer/main",
]


def get_coverage_command_args(
    repo_dir_abs_path: pathlib.Path,
) -> list[str]:
    return [
        "-m",
        "coverage",
        "run",
        f"--rcfile={repo_dir_abs_path / _ConfDst.dst_global.value / 'coveragerc.ini'}",
        "--source=" + ",".join(str(repo_dir_abs_path / source_dir_rel_path) for source_dir_rel_path in coverage_source_dir_rel_paths),
    ]


def run_pytest_for_mode(
    mode_id: ModeId,
    python_abs_path: pathlib.Path | str,
    cwd_abs_path: pathlib.Path,
    test_dir_rel_paths: list[pathlib.Path],
    commit_name: str,
    commit_id: str | None,
    pytest_args: list[str],
    repo_dir_abs_path: pathlib.Path | None = None,
) -> int:
    """
    Runs `pytest` for `mode_id` and reports the failure message (the same for all modes).

    FT_78_72_23_04.backward_compatibility.md
    """

    # `CI` is required, otherwise `test_slow_integrated` tests are skipped:
    sub_env = dict(os.environ)
    sub_env["CI"] = "true"

    # Opt-in: measure the current code (`repo_dir_abs_path`) while the old tests run against it:
    coverage_dir = os.environ.get(coverage_dir_env_var)
    if coverage_dir and repo_dir_abs_path is not None:
        # `parallel = true`: each process adds its own suffix to this base name:
        sub_env["COVERAGE_FILE"] = str(pathlib.Path(coverage_dir).resolve() / f".coverage.{mode_id.value}")
        runner_args = get_coverage_command_args(repo_dir_abs_path) + ["--module", "pytest"]
    else:
        runner_args = ["-m", "pytest"]

    exit_code = subprocess.run(
        [str(python_abs_path)] + runner_args + ["-p", "no:cacheprovider"] + [str(test_dir_rel_path) for test_dir_rel_path in test_dir_rel_paths] + pytest_args,
        cwd=str(cwd_abs_path),
        env=sub_env,
    ).returncode

    if exit_code != 0:
        commit_id_suffix = f" ({commit_id})" if commit_id else ""
        print(
            f"FAILED: mode [{mode_id.value}], commit name [{commit_name}]{commit_id_suffix}: the changes break backward compatibility tests in the baseline - possible actions:\n*   fix changes to comply\n*   update the baseline",
            file=sys.stderr,
        )
    return exit_code


def run_handoff_mode_tests(
    mode_id: ModeId,
    repo_dir_abs_path: pathlib.Path,
    package_name: str,
    commit_name: str,
    pytest_args: list[str],
) -> int:
    """
    Runs the tests of a handoff mode in the current tree (the old part comes from `commit_name`, see `--commit_name`).
    """

    test_dir_rel_path = get_handoff_test_dir_rel_path(package_name, mode_id)
    if not (repo_dir_abs_path / test_dir_rel_path).is_dir():
        raise AssertionError(f"[{test_dir_rel_path}] does not exist")

    return run_pytest_for_mode(
        mode_id,
        sys.executable,
        repo_dir_abs_path,
        [test_dir_rel_path],
        commit_name,
        None,
        ["--commit_name", commit_name] + pytest_args,
        repo_dir_abs_path=repo_dir_abs_path,
    )
