import os
from contextlib import contextmanager
from unittest import mock


@contextmanager
def mock_and_restore_environ():
    """
    Automatically revert `os.environ` to its original state.
    """
    with mock.patch.dict(os.environ):
        yield
