import os

import pytest

from local_test import repo_tree
from local_test.invoke_condition_helper import get_repo_root_abs_path
from local_test.name_assertion import assert_test_module_name_embeds_another_module_name


def test_relationship():
    assert_test_module_name_embeds_another_module_name(
        repo_tree.__name__,
    )


def test_changes_to_repo_root_and_restores_original_cwd(tmp_path, monkeypatch):
    # given:
    monkeypatch.chdir(tmp_path)
    original_cwd = os.getcwd()

    # when:
    with repo_tree.change_to_known_repo_path():
        # then (inside):
        assert os.getcwd() == str(get_repo_root_abs_path())

    # then (after): otherwise, relative `--ignore` paths of `pytest` stop working when used on import (collection):
    assert os.getcwd() == original_cwd


def test_restores_original_cwd_on_failure(tmp_path, monkeypatch):
    # given:
    monkeypatch.chdir(tmp_path)
    original_cwd = os.getcwd()

    # when:
    with pytest.raises(RuntimeError):
        with repo_tree.change_to_known_repo_path():
            raise RuntimeError("test failure")

    # then:
    assert os.getcwd() == original_cwd
