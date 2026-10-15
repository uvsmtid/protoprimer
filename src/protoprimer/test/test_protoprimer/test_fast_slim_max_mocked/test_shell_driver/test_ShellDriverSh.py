import os
from unittest.mock import patch

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    ShellDriverSh,
    ShellType,
    _get_shell_driver,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        ShellDriverSh.__name__,
    )


def test_get_type():
    # given:
    driver = ShellDriverSh(
        shell_abs_path="/bin/sh",
        shell_env_vars={},
        cache_dir_abs_path="/fake/cache",
    )
    # when:
    shell_type = driver.get_type()
    # then:
    assert shell_type == ShellType.shell_sh


def test_get_init_file_basename():
    # given:
    driver = ShellDriverSh(
        shell_abs_path="/bin/sh",
        shell_env_vars={},
        cache_dir_abs_path="/fake/cache",
    )
    # when:
    basename = driver.get_init_file_basename()
    # then:
    assert basename == ".shrc"


def test_configure_interactive_shell(fs):
    # given:
    fs.create_dir("/fake/cache/sh")
    driver = ShellDriverSh(
        shell_abs_path="/bin/sh",
        shell_env_vars={},
        cache_dir_abs_path="/fake/cache",
    )
    # when:
    driver.configure_interactive_shell(False)
    # then:
    # POSIX sh uses ENV var instead of --init-file flag:
    expected_env = os.path.join("/fake/cache", "sh", ".shrc")
    assert driver.shell_env_vars == {"ENV": expected_env}
    # No --init-file flag should be added:
    assert driver.shell_args == ["/bin/sh"]


def test_configure_interactive_shell_with_command(fs):
    # given:
    fs.create_dir("/fake/cache/sh")
    driver = ShellDriverSh(
        shell_abs_path="/bin/sh",
        shell_env_vars={},
        cache_dir_abs_path="/fake/cache",
    )
    # when:
    driver.configure_interactive_shell(True)
    # then:
    # ENV var should still be set:
    expected_env = os.path.join("/fake/cache", "sh", ".shrc")
    assert driver.shell_env_vars == {"ENV": expected_env}
    assert driver.shell_args == ["/bin/sh"]


@patch.dict(os.environ, {}, clear=True)
@patch("protoprimer.primer_kernel.logger.warning")
def test_get_shell_driver_no_shell_env(mock_warning):
    # when:
    driver = _get_shell_driver("/fake/cache")

    # then:
    mock_warning.assert_called_once_with(
        "env var `SHELL` is not set - assuming `/bin/sh` as default"
    )
    assert isinstance(driver, ShellDriverSh)
    assert driver.shell_abs_path == "/bin/sh"


@patch.dict(os.environ, {"SHELL": "/bin/sh"}, clear=True)
def test_get_shell_driver_sh():
    # when:
    driver = _get_shell_driver("/fake/cache")

    # then:
    assert isinstance(driver, ShellDriverSh)
    assert driver.shell_abs_path == "/bin/sh"


def test_get_shell_driver_unknown_shell():
    # given:
    with patch.dict(os.environ, {"SHELL": "/bin/fish"}, clear=True):
        # when/then:
        with pytest.raises(ValueError) as excinfo:
            _get_shell_driver("/fake/cache")
        assert "env var `SHELL` has unknown value [/bin/fish]" in str(excinfo.value)


@patch.dict(os.environ, {"SHELL": "/bin/bash"}, clear=True)
def test_get_shell_driver_bash_unchanged():
    # when:
    driver = _get_shell_driver("/fake/cache")

    # then:
    from protoprimer.primer_kernel import ShellDriverBash

    assert isinstance(driver, ShellDriverBash)
    assert driver.shell_abs_path == "/bin/bash"


@patch.dict(os.environ, {"SHELL": "/bin/zsh"}, clear=True)
def test_get_shell_driver_zsh_unchanged():
    # when:
    driver = _get_shell_driver("/fake/cache")

    # then:
    from protoprimer.primer_kernel import ShellDriverZsh

    assert isinstance(driver, ShellDriverZsh)
    assert driver.shell_abs_path == "/bin/zsh"
