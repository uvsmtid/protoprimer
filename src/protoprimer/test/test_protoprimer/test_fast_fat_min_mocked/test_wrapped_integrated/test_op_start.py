import pathlib

from pyfakefs.fake_filesystem import FakeFilesystem

from local_test.fat_mocked_helper import fat_mock_wrapper
from local_test.name_assertion import (
    assert_test_func_name_embeds_str,
    assert_test_module_name_embeds_another_module_name,
)
from test_protoprimer.test_slow_integrated import test_op_start


def test_relationship():
    assert_test_module_name_embeds_another_module_name(test_op_start.__name__)


def test_start_command_execution(fs: FakeFilesystem):

    assert_test_func_name_embeds_str(test_op_start.test_start_command_execution.__name__)

    mock_test_dir = fs.create_dir("/mock_test_dir")

    with fat_mock_wrapper(fs, proc_mock_run_stdout="Hello, world!"):
        test_op_start.test_start_command_execution(pathlib.Path(mock_test_dir.path))
