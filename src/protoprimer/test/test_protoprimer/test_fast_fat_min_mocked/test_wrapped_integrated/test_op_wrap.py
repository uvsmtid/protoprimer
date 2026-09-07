import pathlib

from pyfakefs.fake_filesystem import FakeFilesystem

from local_test.fat_mocked_helper import fat_mock_wrapper
from local_test.name_assertion import (
    assert_test_func_name_embeds_str,
    assert_test_module_name_embeds_another_module_name,
)
from test_protoprimer.test_slow_integrated import test_op_wrap


def test_relationship():
    assert_test_module_name_embeds_another_module_name(test_op_wrap.__name__)


def test_wrap_boot_env(fs: FakeFilesystem):

    assert_test_func_name_embeds_str(test_op_wrap.test_wrap_boot_env.__name__)

    mock_test_dir = fs.create_dir("/mock_test_dir")

    with fat_mock_wrapper(fs):
        test_op_wrap.test_wrap_boot_env(pathlib.Path(mock_test_dir.path))


def test_wrap_start_app(fs: FakeFilesystem):

    assert_test_func_name_embeds_str(test_op_wrap.test_wrap_start_app.__name__)

    mock_test_dir = fs.create_dir("/mock_test_dir")

    with fat_mock_wrapper(fs):
        test_op_wrap.test_wrap_start_app(pathlib.Path(mock_test_dir.path))
