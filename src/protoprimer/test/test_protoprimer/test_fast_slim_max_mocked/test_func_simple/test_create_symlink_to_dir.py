import os

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    _create_symlink_to_dir,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        _create_symlink_to_dir.__name__,
    )


def test_symlink_is_created_with_the_given_target(fs):
    # given:
    fs.create_dir("/ref_root/dst/env")

    # when:
    _create_symlink_to_dir("/ref_root/lconf", "dst/env")

    # then:
    assert os.path.islink("/ref_root/lconf")
    assert os.readlink("/ref_root/lconf") == "dst/env"
    assert os.path.isdir("/ref_root/lconf")


def test_failure_when_entry_already_exists(fs):
    # given:
    fs.create_dir("/ref_root/dst/env")
    fs.create_dir("/ref_root/lconf")

    # when:
    with pytest.raises(FileExistsError):
        _create_symlink_to_dir("/ref_root/lconf", "dst/env")

    # then: the existing entry is intact
    assert not os.path.islink("/ref_root/lconf")
