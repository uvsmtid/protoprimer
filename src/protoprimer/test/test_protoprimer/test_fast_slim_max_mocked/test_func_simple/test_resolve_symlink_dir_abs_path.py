import os

from local_test.name_assertion import assert_test_module_name_embeds_str
from local_test.path_helper import abs_path
from protoprimer.primer_kernel import (
    _resolve_symlink_dir_abs_path,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        _resolve_symlink_dir_abs_path.__name__,
    )


def test_rel_target_is_resolved_against_symlink_parent_dir(fs):
    # given:
    fs.create_dir(abs_path("/ref_root/conf/dst/env"))
    fs.create_symlink(abs_path("/ref_root/conf/lconf"), "dst/env")
    os.chdir("/")

    # when:
    result = _resolve_symlink_dir_abs_path(abs_path("/ref_root/conf/lconf"))

    # then: independent of curr dir
    assert result == abs_path("/ref_root/conf/dst/env")


def test_abs_target_is_returned_as_is(fs):
    # given:
    fs.create_dir(abs_path("/ref_root/dst/env"))
    fs.create_symlink(abs_path("/ref_root/lconf"), abs_path("/ref_root/dst/env"))

    # when:
    result = _resolve_symlink_dir_abs_path(abs_path("/ref_root/lconf"))

    # then:
    assert result == abs_path("/ref_root/dst/env")


def test_result_is_normalized(fs):
    # given:
    fs.create_dir(abs_path("/ref_root/dst/env"))
    fs.create_dir(abs_path("/ref_root/conf"))
    fs.create_symlink(abs_path("/ref_root/conf/lconf"), "../dst/env")

    # when:
    result = _resolve_symlink_dir_abs_path(abs_path("/ref_root/conf/lconf"))

    # then:
    assert result == abs_path("/ref_root/dst/env")


def test_result_is_not_the_symlink_path(fs):
    # given:
    fs.create_dir(abs_path("/ref_root/dst/env"))
    fs.create_symlink(abs_path("/ref_root/lconf"), "dst/env")

    # when:
    result = _resolve_symlink_dir_abs_path(abs_path("/ref_root/lconf"))

    # then:
    assert result != abs_path("/ref_root/lconf")
