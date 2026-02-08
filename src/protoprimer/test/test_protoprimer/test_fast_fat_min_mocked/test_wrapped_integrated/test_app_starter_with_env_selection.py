import pathlib

from pyfakefs.fake_filesystem import FakeFilesystem

from local_test.fat_mocked_helper import fat_mock_wrapper
from local_test.name_assertion import (
    assert_test_func_name_embeds_str,
    assert_test_module_name_embeds_another_module_name,
)
from test_protoprimer.test_slow_integrated import test_app_starter_with_env_selection


def test_relationship():
    assert_test_module_name_embeds_another_module_name(
        test_app_starter_with_env_selection.__name__
    )


def test_app_starter_from_env_default(fs: FakeFilesystem):

    assert_test_func_name_embeds_str(
        test_app_starter_with_env_selection.test_app_starter_from_env_default.__name__
    )

    mock_test_dir = fs.create_dir("/mock_test_dir")

    with fat_mock_wrapper(fs, proc_mock_run_stdout="Hello, world!"):
        test_app_starter_with_env_selection.test_app_starter_from_env_default(
            pathlib.Path(mock_test_dir.path)
        )


def test_app_started_from_env_special(fs: FakeFilesystem):

    assert_test_func_name_embeds_str(
        test_app_starter_with_env_selection.test_app_started_from_env_special.__name__
    )

    mock_test_dir = fs.create_dir("/mock_test_dir")

    with fat_mock_wrapper(fs, proc_mock_run_stdout="Hello, world!"):
        test_app_starter_with_env_selection.test_app_started_from_env_special(
            pathlib.Path(mock_test_dir.path)
        )


def test_app_started_with_symlink_to_env_special_but_config_to_env_common(
    fs: FakeFilesystem,
):

    assert_test_func_name_embeds_str(
        test_app_starter_with_env_selection.test_app_started_with_symlink_to_env_special_but_config_to_env_common.__name__
    )

    mock_test_dir = fs.create_dir("/mock_test_dir")

    with fat_mock_wrapper(fs, proc_mock_run_stdout="Hello, world!"):
        test_app_starter_with_env_selection.test_app_started_with_symlink_to_env_special_but_config_to_env_common(
            pathlib.Path(mock_test_dir.path)
        )
