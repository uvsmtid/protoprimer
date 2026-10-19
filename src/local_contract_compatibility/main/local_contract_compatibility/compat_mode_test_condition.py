from __future__ import annotations

import pathlib
import subprocess

import pytest


def skip_unless_commit_name(
    parent_dir_abs_path: pathlib.Path,
    config,
    items,
) -> None:
    """
    Skips all collected tests under `parent_dir_abs_path` unless `--commit_name` was given
    (the option itself is registered once, in `test_slow_integrated/conftest.py`).

    Enabled only by the `compat` CI job, not by the `py[min]`/`py[med]`/`py[max]` jobs.

    FT_78_72_23_04.backward_compatibility.md
    """

    if config.getoption("--commit_name"):
        return

    skip_marker = pytest.mark.skip(
        reason=f"Tests under `{parent_dir_abs_path.name}` are skipped by default. Run with `--commit_name <baseline>` to enable.",
    )
    resolved_parent_path = parent_dir_abs_path.resolve()
    for pytest_item in items:
        test_path = pytest_item.path if hasattr(pytest_item, "path") else pathlib.Path(pytest_item.fspath)
        resolved_test_path = pathlib.Path(test_path).resolve()
        if resolved_parent_path == resolved_test_path or resolved_parent_path in resolved_test_path.parents:
            pytest_item.add_marker(skip_marker)


@pytest.fixture
def commit_name(request) -> str:
    return request.config.getoption("--commit_name")


@pytest.fixture
def repo_dir_abs_path() -> pathlib.Path:
    return pathlib.Path(
        subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=str(pathlib.Path(__file__).parent),
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    )
