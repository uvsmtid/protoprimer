import os

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    _compose_symlink_target,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        _compose_symlink_target.__name__,
    )


def test_symlink_in_ref_root():
    # when:
    result = _compose_symlink_target("/ref_root", "dst/env", "/ref_root/lconf")

    # then:
    assert result == os.path.join("dst", "env")


def test_nested_symlink_target_is_relative_to_symlink_parent_dir():
    # when:
    result = _compose_symlink_target("/ref_root", "conf/dst/env", "/ref_root/conf/lconf")

    # then: not relative to `ref_root`
    assert result == os.path.join("dst", "env")


def test_target_is_normalized():
    # when:
    result = _compose_symlink_target("/ref_root", "dst/./env/", "/ref_root/lconf")

    # then:
    assert result == os.path.join("dst", "env")


def test_target_outside_symlink_parent_dir_goes_up():
    # when:
    result = _compose_symlink_target("/ref_root", "dst/env", "/ref_root/conf/lconf")

    # then:
    assert result == os.path.join("..", "dst", "env")
