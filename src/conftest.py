import pytest
import os
from unittest import mock


@pytest.fixture(autouse=True)
def mock_and_restore_env_vars():
    """
    Automatically revert `os.environ` to its original state after every single test case.
    """
    with mock.patch.dict(os.environ):
        yield
