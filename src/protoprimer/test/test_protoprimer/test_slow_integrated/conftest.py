"""
This file configures `pytest` for this directory.
"""

import os

import pytest

from local_test.case_condition import (
    set_protoprimer_debug_log_level,
    skip_test_slow_integrated,
)


def pytest_addoption(parser):
    """
    Used by `test_old_proto_on_new_venv/` and `test_old_entry_on_new_proto/` (registered once here,
    since `pytest_addoption` cannot be added twice when the whole tree is collected together).

    FT_78_72_23_04.backward_compatibility.md
    """
    parser.addoption(
        "--commit_name",
        action="store",
        default=None,
        help="Baseline commit name for compat-mode tests (`old_proto_on_new_venv`/`old_entry_on_new_proto`).",
    )


def pytest_collection_modifyitems(config, items):

    skip_test_slow_integrated(
        os.path.dirname(__file__),
        config,
        items,
    )


@pytest.fixture(autouse=True)
def set_debug_log_level_to_test_slow_integrated():
    with set_protoprimer_debug_log_level():
        yield
