"""
This file configures `pytest` for this directory.
"""

import os

from local_test.case_condition import skip_test_slow_integrated


def pytest_collection_modifyitems(config, items):

    skip_test_slow_integrated(
        os.path.dirname(__file__),
        config,
        items,
    )
