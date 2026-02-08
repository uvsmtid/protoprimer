import os

import pytest

from local_test.case_condition import (
    set_protoprimer_debug_log_level,
    skip_test_slow_integrated,
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
