"""
This file configures `pytest` for this directory.

Tests here are skipped unless `--commit_name` is given (the option is registered once, in
`test_slow_integrated/conftest.py`): they are enabled only by the `compat` CI job, not by the
`py[min]`/`py[med]`/`py[max]` jobs.

Every test here that generates an entry script (imported from `test_contract_compatibility`)
gets it from the old `wrap` of `--commit_name`; the `proto_kernel.py` and the `venv` stay current.

FT_78_72_23_04.backward_compatibility.md
"""

import pathlib

import pytest

from local_contract_compatibility.compat_mode_test_condition import (
    commit_name,
    old_proto_kernel_abs_path,
    old_wrap_in_use,
    repo_dir_abs_path,
    skip_unless_commit_name,
)


def pytest_collection_modifyitems(config, items):
    skip_unless_commit_name(
        pathlib.Path(__file__).parent,
        config,
        items,
    )


@pytest.fixture(autouse=True)
def use_old_wrap(old_wrap_in_use):
    yield
