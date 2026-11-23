import os

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from local_test.path_helper import abs_path
from protoprimer.primer_kernel import (
    _compose_env_dir_abs_path,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        _compose_env_dir_abs_path.__name__,
    )


def test_abs_path_is_returned_as_is(fs):
    # given:
    fs.create_dir(abs_path("/ref_root"))

    # when:
    result = _compose_env_dir_abs_path(abs_path("/any/abs/path"), abs_path("/ref_root"))

    # then: not even checked for existence
    assert result == abs_path("/any/abs/path")


def test_rel_path_is_resolved_against_ref_root(fs):
    # given:
    fs.create_dir(abs_path("/ref_root/my_env"))
    fs.create_dir(abs_path("/elsewhere"))
    os.chdir(abs_path("/elsewhere"))

    # when:
    result = _compose_env_dir_abs_path("my_env", abs_path("/ref_root"))

    # then:
    assert result == abs_path("/ref_root/my_env")


def test_ref_root_is_preferred_over_curr_dir(fs):
    # given: the same rel path exists under both
    fs.create_dir(abs_path("/ref_root/my_env"))
    fs.create_dir(abs_path("/elsewhere/my_env"))
    os.chdir(abs_path("/elsewhere"))

    # when:
    result = _compose_env_dir_abs_path("my_env", abs_path("/ref_root"))

    # then:
    assert result == abs_path("/ref_root/my_env")


def test_rel_path_is_resolved_against_curr_dir_last(fs):
    # given: the rel path exists only under curr dir
    fs.create_dir(abs_path("/ref_root"))
    fs.create_dir(abs_path("/elsewhere/my_env"))
    os.chdir(abs_path("/elsewhere"))

    # when:
    result = _compose_env_dir_abs_path("my_env", abs_path("/ref_root"))

    # then:
    assert result == abs_path("/elsewhere/my_env")


def test_failure_when_rel_path_exists_nowhere(fs):
    # given:
    fs.create_dir(abs_path("/ref_root"))
    os.chdir(abs_path("/ref_root"))

    # when:
    with pytest.raises(AssertionError) as exc_info:
        _compose_env_dir_abs_path("missing_env", abs_path("/ref_root"))

    # then:
    assert "is relative to neither" in str(exc_info.value)
