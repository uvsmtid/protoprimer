import pathlib

from pyfakefs.fake_filesystem import FakeFilesystem

from local_test.fat_mocked_helper import fat_mock_wrapper
from local_test.version_gate import (
    before_version,
    since_version,
)
from local_test.name_assertion import (
    assert_test_func_name_embeds_str,
    assert_test_module_name_embeds_another_module_name,
)
from test_protoprimer.test_slow_integrated.test_contract_compatibility import test_boot_env_with_env_selection


def test_relationship():
    assert_test_module_name_embeds_another_module_name(test_boot_env_with_env_selection.__name__)


def test_boot_env_with_env_selection_default_to_special(fs: FakeFilesystem):

    assert_test_func_name_embeds_str(test_boot_env_with_env_selection.test_boot_env_with_env_selection_default_to_special.__name__)

    mock_test_dir = fs.create_dir("/mock_test_dir")

    with fat_mock_wrapper(fs):
        test_boot_env_with_env_selection.test_boot_env_with_env_selection_default_to_special(pathlib.Path(mock_test_dir.path))


def test_boot_env_with_env_selection_special_to_default(fs: FakeFilesystem):

    assert_test_func_name_embeds_str(test_boot_env_with_env_selection.test_boot_env_with_env_selection_special_to_default.__name__)

    mock_test_dir = fs.create_dir("/mock_test_dir")

    with fat_mock_wrapper(fs):
        test_boot_env_with_env_selection.test_boot_env_with_env_selection_special_to_default(pathlib.Path(mock_test_dir.path))


@before_version("0.15.0")
def test_boot_env_with_symlink_to_env_special_but_config_to_env_common_fails(
    fs: FakeFilesystem,
):

    assert_test_func_name_embeds_str(test_boot_env_with_env_selection.test_boot_env_with_symlink_to_env_special_but_config_to_env_common_fails.__name__)

    mock_test_dir = fs.create_dir("/mock_test_dir")

    with fat_mock_wrapper(fs):
        test_boot_env_with_env_selection.test_boot_env_with_symlink_to_env_special_but_config_to_env_common_fails(pathlib.Path(mock_test_dir.path))


@since_version("0.15.0")
def test_boot_env_with_symlink_to_env_special_but_config_to_env_common_uses_persisted(
    fs: FakeFilesystem,
):

    assert_test_func_name_embeds_str(test_boot_env_with_env_selection.test_boot_env_with_symlink_to_env_special_but_config_to_env_common_uses_persisted.__name__)

    mock_test_dir = fs.create_dir("/mock_test_dir")

    with fat_mock_wrapper(fs):
        test_boot_env_with_env_selection.test_boot_env_with_symlink_to_env_special_but_config_to_env_common_uses_persisted(pathlib.Path(mock_test_dir.path))


def test_boot_env_with_env_mismatching_persisted_env_fails(fs: FakeFilesystem):

    assert_test_func_name_embeds_str(test_boot_env_with_env_selection.test_boot_env_with_env_mismatching_persisted_env_fails.__name__)

    mock_test_dir = fs.create_dir("/mock_test_dir")

    with fat_mock_wrapper(fs):
        test_boot_env_with_env_selection.test_boot_env_with_env_mismatching_persisted_env_fails(pathlib.Path(mock_test_dir.path))


def test_boot_env_without_env_selection_uses_global_conf_dir(fs: FakeFilesystem):

    assert_test_func_name_embeds_str(test_boot_env_with_env_selection.test_boot_env_without_env_selection_uses_global_conf_dir.__name__)

    mock_test_dir = fs.create_dir("/mock_test_dir")

    with fat_mock_wrapper(fs):
        test_boot_env_with_env_selection.test_boot_env_without_env_selection_uses_global_conf_dir(pathlib.Path(mock_test_dir.path))


@since_version("0.15.0")
def test_boot_env_with_env_selector_overrides_default_env(fs: FakeFilesystem):

    assert_test_func_name_embeds_str(test_boot_env_with_env_selection.test_boot_env_with_env_selector_overrides_default_env.__name__)

    mock_test_dir = fs.create_dir("/mock_test_dir")

    with fat_mock_wrapper(fs):
        test_boot_env_with_env_selection.test_boot_env_with_env_selector_overrides_default_env(pathlib.Path(mock_test_dir.path))


@since_version("0.15.0")
def test_boot_env_with_env_arg_overrides_env_selector(fs: FakeFilesystem):

    assert_test_func_name_embeds_str(test_boot_env_with_env_selection.test_boot_env_with_env_arg_overrides_env_selector.__name__)

    mock_test_dir = fs.create_dir("/mock_test_dir")

    with fat_mock_wrapper(fs):
        test_boot_env_with_env_selection.test_boot_env_with_env_arg_overrides_env_selector(pathlib.Path(mock_test_dir.path))


@since_version("0.15.0")
def test_boot_env_with_env_selector_returning_none_uses_default_env(fs: FakeFilesystem):

    assert_test_func_name_embeds_str(test_boot_env_with_env_selection.test_boot_env_with_env_selector_returning_none_uses_default_env.__name__)

    mock_test_dir = fs.create_dir("/mock_test_dir")

    with fat_mock_wrapper(fs):
        test_boot_env_with_env_selection.test_boot_env_with_env_selector_returning_none_uses_default_env(pathlib.Path(mock_test_dir.path))


@since_version("0.15.0")
def test_boot_env_with_env_selector_matching_persisted_env_is_repeatable(fs: FakeFilesystem):

    assert_test_func_name_embeds_str(test_boot_env_with_env_selection.test_boot_env_with_env_selector_matching_persisted_env_is_repeatable.__name__)

    mock_test_dir = fs.create_dir("/mock_test_dir")

    with fat_mock_wrapper(fs):
        test_boot_env_with_env_selection.test_boot_env_with_env_selector_matching_persisted_env_is_repeatable(pathlib.Path(mock_test_dir.path))


@since_version("0.15.0")
def test_boot_env_with_env_selector_mismatching_persisted_env_fails(fs: FakeFilesystem):

    assert_test_func_name_embeds_str(test_boot_env_with_env_selection.test_boot_env_with_env_selector_mismatching_persisted_env_fails.__name__)

    mock_test_dir = fs.create_dir("/mock_test_dir")

    with fat_mock_wrapper(fs):
        test_boot_env_with_env_selection.test_boot_env_with_env_selector_mismatching_persisted_env_fails(pathlib.Path(mock_test_dir.path))
