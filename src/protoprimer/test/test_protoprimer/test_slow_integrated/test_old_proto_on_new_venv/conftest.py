"""
This file configures `pytest` for this directory.

Tests here are skipped unless `--commit_name` is given (the option is registered once, in
`test_slow_integrated/conftest.py`): they are enabled only by the `compat` CI job, not by the
`py[min]`/`py[med]`/`py[max]` jobs.

FT_78_72_23_04.backward_compatibility.md
"""

import pathlib

from local_contract_compatibility.compat_mode_test_condition import (
    commit_name,
    repo_dir_abs_path,
    skip_unless_commit_name,
)


def pytest_collection_modifyitems(config, items):
    skip_unless_commit_name(
        pathlib.Path(__file__).parent,
        config,
        items,
    )
