import os
from unittest.mock import patch

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    _ConfConstGeneral,
    _create_symlink_to_dir,
    _remove_symlink_to_dir,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        _remove_symlink_to_dir.__name__,
    )


def test_symlink_is_removed_but_target_is_kept(fs):
    # given:
    fs.create_dir("/ref_root/dst/env")
    _create_symlink_to_dir("/ref_root/lconf", "dst/env")

    # when:
    _remove_symlink_to_dir("/ref_root/lconf")

    # then:
    assert not os.path.lexists("/ref_root/lconf")
    assert os.path.isdir("/ref_root/dst/env")


@patch.object(_ConfConstGeneral, "is_os_windows", False)
@patch("protoprimer.primer_kernel.os.rmdir")
@patch("protoprimer.primer_kernel.os.remove")
def test_posix_uses_remove(mock_remove, mock_rmdir):
    # when:
    _remove_symlink_to_dir("/ref_root/lconf")

    # then:
    mock_remove.assert_called_once_with("/ref_root/lconf")
    mock_rmdir.assert_not_called()


@patch.object(_ConfConstGeneral, "is_os_windows", True)
@patch("protoprimer.primer_kernel.os.rmdir")
@patch("protoprimer.primer_kernel.os.remove")
def test_windows_uses_rmdir(mock_remove, mock_rmdir):
    # when:
    _remove_symlink_to_dir("/ref_root/lconf")

    # then:
    mock_rmdir.assert_called_once_with("/ref_root/lconf")
    mock_remove.assert_not_called()
