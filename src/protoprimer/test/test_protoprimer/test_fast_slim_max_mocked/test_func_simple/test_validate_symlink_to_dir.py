import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    _validate_symlink_to_dir,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        _validate_symlink_to_dir.__name__,
    )


def test_symlink_to_dir_is_valid(fs):
    # given:
    fs.create_dir("/ref_root/dst/env")
    fs.create_symlink("/ref_root/lconf", "dst/env")

    # when:
    _validate_symlink_to_dir("/ref_root/lconf")

    # then: no exception


def test_failure_when_entry_is_a_real_dir(fs):
    # given:
    fs.create_dir("/ref_root/lconf")

    # when:
    with pytest.raises(AssertionError) as exc_info:
        _validate_symlink_to_dir("/ref_root/lconf")

    # then:
    assert "is not a symlink" in str(exc_info.value)


def test_failure_when_entry_is_a_real_file(fs):
    # given:
    fs.create_file("/ref_root/lconf")

    # when:
    with pytest.raises(AssertionError) as exc_info:
        _validate_symlink_to_dir("/ref_root/lconf")

    # then:
    assert "is not a symlink" in str(exc_info.value)


def test_failure_when_entry_is_missing(fs):
    # given:
    fs.create_dir("/ref_root")

    # when:
    with pytest.raises(AssertionError) as exc_info:
        _validate_symlink_to_dir("/ref_root/lconf")

    # then:
    assert "is not a symlink" in str(exc_info.value)


def test_failure_when_symlink_points_to_a_file(fs):
    # given:
    fs.create_file("/ref_root/some_file")
    fs.create_symlink("/ref_root/lconf", "some_file")

    # when:
    with pytest.raises(AssertionError) as exc_info:
        _validate_symlink_to_dir("/ref_root/lconf")

    # then:
    assert "is not a directory" in str(exc_info.value)


def test_failure_when_symlink_is_dangling(fs):
    # given:
    fs.create_dir("/ref_root")
    fs.create_symlink("/ref_root/lconf", "missing_dir")

    # when:
    with pytest.raises(AssertionError) as exc_info:
        _validate_symlink_to_dir("/ref_root/lconf")

    # then:
    assert "is not a directory" in str(exc_info.value)
