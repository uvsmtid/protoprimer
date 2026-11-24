import os

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from local_test.path_helper import abs_path
from protoprimer.primer_kernel import (
    _compose_env_dir_rel_path,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        _compose_env_dir_rel_path.__name__,
    )


def test_rel_path_is_normalized(fs):
    # given:
    fs.create_dir(abs_path("/ref_root/dst/my_env"))
    os.chdir(abs_path("/"))

    # when:
    result = _compose_env_dir_rel_path("dst/./my_env/", abs_path("/ref_root"))

    # then:
    assert result == os.path.join("dst", "my_env")


def test_abs_path_inside_ref_root_becomes_rel_path(fs):
    # given:
    fs.create_dir(abs_path("/ref_root/dst/my_env"))

    # when:
    result = _compose_env_dir_rel_path(abs_path("/ref_root/dst/my_env"), abs_path("/ref_root"))

    # then:
    assert result == os.path.join("dst", "my_env")


def test_curr_dir_rel_path_is_relative_to_ref_root_in_result(fs):
    # given: the dir is only found relative to curr dir (a sub dir of `ref_root`)
    fs.create_dir(abs_path("/ref_root/subdir/my_env"))
    os.chdir(abs_path("/ref_root/subdir"))

    # when:
    result = _compose_env_dir_rel_path("my_env", abs_path("/ref_root"))

    # then:
    assert result == os.path.join("subdir", "my_env")


def test_symlink_to_dir_is_accepted_by_its_own_name(fs):
    # given:
    fs.create_dir(abs_path("/ref_root/valid_dir"))
    fs.create_symlink(abs_path("/ref_root/symlink_to_dir"), "valid_dir")

    # when:
    result = _compose_env_dir_rel_path(abs_path("/ref_root/symlink_to_dir"), abs_path("/ref_root"))

    # then:
    assert result == "symlink_to_dir"


def test_failure_when_path_is_not_a_dir(fs):
    # given:
    fs.create_dir(abs_path("/ref_root"))
    fs.create_file(abs_path("/ref_root/not_a_dir"))

    # when:
    with pytest.raises(AssertionError) as exc_info:
        _compose_env_dir_rel_path(abs_path("/ref_root/not_a_dir"), abs_path("/ref_root"))

    # then:
    assert "must be a dir" in str(exc_info.value)


def test_failure_when_path_is_outside_ref_root(fs):
    # given:
    fs.create_dir(abs_path("/ref_root"))
    fs.create_dir(abs_path("/outside/my_env"))

    # when:
    with pytest.raises(AssertionError) as exc_info:
        _compose_env_dir_rel_path(abs_path("/outside/my_env"), abs_path("/ref_root"))

    # then:
    assert "is not under" in str(exc_info.value)
