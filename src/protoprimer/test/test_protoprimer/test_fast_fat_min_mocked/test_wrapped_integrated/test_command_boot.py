import pathlib

from pyfakefs.fake_filesystem import FakeFilesystem

from local_test.fat_mocked_helper import fat_mock_wrapper
from local_test.name_assertion import (
    assert_test_module_name_embeds_another_module_name,
)
from test_protoprimer.test_slow_integrated import test_command_boot


def test_relationship():
    assert_test_module_name_embeds_another_module_name(test_command_boot.__name__)


def test_wrapped_boot_in_mock_env(fs: FakeFilesystem):
    mock_test_dir = fs.create_dir("/mock_test_dir")

    with fat_mock_wrapper(fs):
        test_command_boot.test_command_boot(pathlib.Path(mock_test_dir.path))
