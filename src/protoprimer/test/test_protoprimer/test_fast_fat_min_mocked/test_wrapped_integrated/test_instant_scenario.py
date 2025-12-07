import pathlib

from pyfakefs.fake_filesystem import FakeFilesystem

from local_test.fat_mocked_helper import fat_mock_wrapper
from local_test.name_assertion import (
    assert_test_module_name_embeds_another_module_name,
)
from test_protoprimer.test_slow_integrated import (
    test_instant_scenario,
)


def test_relationship():
    assert_test_module_name_embeds_another_module_name(test_instant_scenario.__name__)


def test_wrapped_prime_in_mock_env(fs: FakeFilesystem):
    mock_test_dir = fs.create_dir("/mock_test_dir")

    with fat_mock_wrapper(fs):
        test_instant_scenario.test_instant_scenario(pathlib.Path(mock_test_dir.path))
