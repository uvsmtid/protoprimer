import os

from local_test import tmp_dir_helper
from local_test.invoke_condition_helper import get_repo_root_abs_path
from local_test.name_assertion import assert_test_module_name_embeds_another_module_name


def test_relationship():
    assert_test_module_name_embeds_another_module_name(
        tmp_dir_helper.__name__,
    )


def test_get_tmp_dir_abs_path_is_tmp_under_repo_and_keeps_cwd():
    # given:
    repo_dir_abs_path = str(get_repo_root_abs_path())
    original_cwd = os.getcwd()

    # when:
    tmp_dir_abs_path = tmp_dir_helper.get_tmp_dir_abs_path(repo_dir_abs_path)

    # then:
    assert tmp_dir_abs_path == os.path.join(repo_dir_abs_path, "tmp")
    assert os.getcwd() == original_cwd
