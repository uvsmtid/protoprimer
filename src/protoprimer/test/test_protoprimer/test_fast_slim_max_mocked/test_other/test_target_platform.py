from unittest.mock import patch

import pytest
from protoprimer.primer_kernel import (
    _get_target_platform,
    _TargetPlatform,
)


@pytest.mark.parametrize(
    "sys_platform, expected_platform",
    [
        ("linux", _TargetPlatform.platform_linux),
        ("darwin", _TargetPlatform.platform_darwin),
        ("freebsd14", _TargetPlatform.platform_freebsd),
        ("win32", _TargetPlatform.platform_windows),
    ],
)
def test_get_target_platform(sys_platform, expected_platform):
    # given:
    with patch("sys.platform", sys_platform):
        # when:
        target_platform = _get_target_platform()
    # then:
    assert target_platform == expected_platform


def test_get_target_platform_unsupported():
    # given:
    with patch("sys.platform", "openbsd7"):
        # when/then:
        with pytest.raises(ValueError):
            _get_target_platform()


@pytest.mark.parametrize(
    "target_platform, expected_is_posix",
    [
        (_TargetPlatform.platform_linux, True),
        (_TargetPlatform.platform_darwin, True),
        (_TargetPlatform.platform_freebsd, True),
        (_TargetPlatform.platform_windows, False),
    ],
)
def test_is_posix(target_platform, expected_is_posix):
    assert target_platform.is_posix() == expected_is_posix
