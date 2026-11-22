import pytest

from local_test import coverage_conf
from local_test.coverage_conf import (
    get_rcfile_abs_path,
    read_source_dir_rel_paths,
)
from local_test.invoke_condition_helper import get_repo_root_abs_path
from local_test.name_assertion import assert_test_module_name_embeds_another_module_name


def test_relationship():
    assert_test_module_name_embeds_another_module_name(coverage_conf.__name__)


def test_read_source_dir_rel_paths(tmp_path):

    # given:

    rcfile_abs_path = get_rcfile_abs_path(tmp_path)
    rcfile_abs_path.parent.mkdir()
    rcfile_abs_path.write_text("[run]\n# comment\nsource =\n    src/a/main/\n    src/b/main\n\nbranch = true\n")

    # then:

    assert read_source_dir_rel_paths(tmp_path) == ["src/a/main", "src/b/main"]


def test_read_source_dir_rel_paths_fails_loudly_without_rcfile(tmp_path):

    with pytest.raises(FileNotFoundError):
        read_source_dir_rel_paths(tmp_path)


def test_read_source_dir_rel_paths_of_this_repo():

    # when:

    source_dir_rel_paths = read_source_dir_rel_paths(get_repo_root_abs_path())

    # then: the measured code exists
    assert source_dir_rel_paths
    for source_dir_rel_path in source_dir_rel_paths:
        assert (get_repo_root_abs_path() / source_dir_rel_path).is_dir()
