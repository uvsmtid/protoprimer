import pathlib

from pyfakefs.fake_filesystem import FakeFilesystem

from local_test.fat_mocked_helper import fat_mock_wrapper
from local_test.name_assertion import (
    assert_test_module_name_embeds_another_module_name,
)
from test_protoprimer.test_slow_integrated import (
    test_mode_eval,
)


def test_relationship():
    assert_test_module_name_embeds_another_module_name(test_mode_eval.__name__)


def test_min_layout(fs: FakeFilesystem):
    mock_test_dir = fs.create_dir("/mock_test_dir")

    with fat_mock_wrapper(fs):
        test_mode_eval.test_mode_eval_with_min_layout(pathlib.Path(mock_test_dir.path))


def test_max_layout(fs: FakeFilesystem):
    mock_test_dir = fs.create_dir("/mock_test_dir")

    with fat_mock_wrapper(fs):
        test_mode_eval.test_mode_eval_with_max_layout(pathlib.Path(mock_test_dir.path))
