"""
This file configures `pytest` for this directory.

FT_64_09_03_66.invoke_condition.md
"""

import os

from local_test.invoke_condition_helper import skip_test_invoke_condition


def pytest_collection_modifyitems(config, items):

    skip_test_invoke_condition(
        os.path.dirname(__file__),
        config,
        items,
    )
