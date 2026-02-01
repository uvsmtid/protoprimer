import pytest
from local_test.mock_environ import mock_and_restore_environ


@pytest.fixture(autouse=True)
def mock_and_restore_env_vars():
    with mock_and_restore_environ():
        yield
