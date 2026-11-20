import pathlib

from pyfakefs.fake_filesystem import FakeFilesystem

from local_test.fat_mocked_helper import fat_mock_wrapper
from local_test.name_assertion import (
    assert_test_module_name_embeds_another_module_name,
)
from test_protoprimer.test_slow_integrated.test_contract_compatibility import test_op_reset


def test_relationship():
    assert_test_module_name_embeds_another_module_name(test_op_reset.__name__)


def test_overwrites_persisted_env(fs: FakeFilesystem):
    mock_test_dir = fs.create_dir("/mock_test_dir")

    with fat_mock_wrapper(fs):
        test_op_reset.test_op_reset_overwrites_persisted_env(pathlib.Path(mock_test_dir.path))


def test_with_env_selector_overwrites_persisted_env(fs: FakeFilesystem):
    mock_test_dir = fs.create_dir("/mock_test_dir")

    with fat_mock_wrapper(fs):
        test_op_reset.test_op_reset_with_env_selector_overwrites_persisted_env(pathlib.Path(mock_test_dir.path))


def test_with_env_arg_overrides_env_selector(fs: FakeFilesystem):
    mock_test_dir = fs.create_dir("/mock_test_dir")

    with fat_mock_wrapper(fs):
        test_op_reset.test_op_reset_with_env_arg_overrides_env_selector(pathlib.Path(mock_test_dir.path))
