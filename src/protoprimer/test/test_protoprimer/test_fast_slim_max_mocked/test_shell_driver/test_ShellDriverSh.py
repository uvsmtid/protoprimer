import os
from unittest.mock import patch

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    _get_shell_driver,
    ShellDriverBash,
    ShellDriverSh,
    ShellType,
)


def test_relationship():
    assert_test_module_name_embeds_str(ShellDriverSh.__name__)


def test_get_type():
    driver = ShellDriverSh("/bin/sh", {}, "/fake/cache")
    assert driver.get_type() == ShellType.shell_sh


def test_get_init_file_basename():
    driver = ShellDriverSh("/bin/sh", {}, "/fake/cache")
    assert driver.get_init_file_basename() == ".shrc"


@pytest.mark.parametrize("has_command", [False, True])
def test_configure_interactive_shell(has_command):
    driver = ShellDriverSh("/bin/sh", {"KEEP": "value"}, "/fake/cache with spaces")
    driver.configure_interactive_shell(has_command)
    assert driver.shell_args == ["/bin/sh"]
    assert driver.shell_env_vars == {
        "KEEP": "value",
        "ENV": "/fake/cache with spaces/sh/.shrc",
    }


@pytest.mark.parametrize("shell_path", ["/bin/sh", "/usr/bin/sh"])
def test_get_shell_driver_sh(shell_path):
    with patch.dict(os.environ, {"SHELL": shell_path}, clear=True):
        driver = _get_shell_driver("/fake/cache", activate_venv=False)
    assert isinstance(driver, ShellDriverSh)
    assert driver.shell_abs_path == shell_path
    assert driver.activate_venv is False


def test_get_shell_driver_bash():
    with patch.dict(os.environ, {"SHELL": "/bin/bash"}, clear=True):
        driver = _get_shell_driver("/fake/cache")
    assert isinstance(driver, ShellDriverBash)
    assert driver.shell_abs_path == "/bin/bash"


@patch("os.execve")
@patch.object(ShellDriverSh, "write_init_file")
def test_run_shell(mock_write, mock_execve):
    driver = ShellDriverSh("/bin/sh", {"KEEP": "value"}, "/fake/cache")
    driver.run_shell(False, "printf '%s' ready", "/fake/venv")
    mock_write.assert_called_once_with("/fake/venv")
    mock_execve.assert_called_once_with(
        "/bin/sh",
        ["/bin/sh", "-i", "-c", "printf '%s' ready"],
        {"KEEP": "value", "ENV": "/fake/cache/sh/.shrc"},
    )


def test_write_init_file(tmp_path):
    driver = ShellDriverSh("/bin/sh", {}, str(tmp_path / "cache"))
    driver.write_init_file("/fake/venv with 'quotes'")
    with open(driver.get_init_file_abs_path()) as handle:
        content = handle.read()
    assert "source " not in content
    assert ". /fake/venv" not in content
    assert ". '/fake/venv with '" in content
