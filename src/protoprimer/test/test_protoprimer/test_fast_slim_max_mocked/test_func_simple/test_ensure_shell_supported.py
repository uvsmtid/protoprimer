import re
from unittest.mock import patch

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    _ensure_shell_supported,
    _TargetPlatform,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        _ensure_shell_supported.__name__,
    )


@pytest.mark.parametrize(
    "target_platform",
    [
        _TargetPlatform.platform_linux,
        _TargetPlatform.platform_darwin,
        _TargetPlatform.platform_freebsd,
    ],
)
def test_posix_platform_is_supported(target_platform):
    with patch(f"{primer_kernel.__name__}._get_target_platform", return_value=target_platform):
        _ensure_shell_supported("/fake/venv")


def test_windows_platform_fails_with_abs_path_to_venv():
    # given:
    venv_abs_path = "C:\\fake\\venv"

    with patch(f"{primer_kernel.__name__}._get_target_platform", return_value=_TargetPlatform.platform_windows):
        # when:
        with pytest.raises(NotImplementedError) as exc_info:
            _ensure_shell_supported(venv_abs_path)

    # then: the user can activate `venv` manually
    error_message = str(exc_info.value)
    assert f"[{venv_abs_path}]" in error_message
    assert re.search(r"\[.*activate.*\]", error_message)
