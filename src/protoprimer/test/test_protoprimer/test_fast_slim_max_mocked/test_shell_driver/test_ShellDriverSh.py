import os
from unittest.mock import patch

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    _get_shell_driver,
    ShellDriverSh,
    ShellType,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        ShellDriverSh.__name__,
    )


def test_get_type():
    driver = ShellDriverSh(
        shell_abs_path="/bin/sh",
        shell_env_vars={},
        cache_dir_abs_path="/fake/cache",
    )
    assert driver.get_type() == ShellType.shell_sh
    assert driver.get_init_file_basename() == ".shrc"


@pytest.mark.parametrize("bash_path", [None, "/bin/bash"])
@patch.dict(os.environ, {}, clear=True)
@patch("shutil.which")
@patch("protoprimer.primer_kernel.logger.warning")
def test_get_shell_driver_no_shell_env_no_bash(mock_warning, mock_which, bash_path):
    mock_which.return_value = bash_path

    driver = _get_shell_driver("/fake/cache", activate_venv=False)

    mock_which.assert_not_called()
    mock_warning.assert_called_once_with("env var `SHELL` is not set - assuming `/bin/sh` as default")
    assert isinstance(driver, ShellDriverSh)
    assert driver.shell_abs_path == "/bin/sh"
    assert driver.activate_venv is False


@pytest.mark.parametrize("shell_path", ["/bin/sh", "/usr/bin/sh"])
def test_get_shell_driver_sh(shell_path):
    with patch.dict(os.environ, {"SHELL": shell_path}, clear=True):
        driver = _get_shell_driver("/fake/cache")

    assert isinstance(driver, ShellDriverSh)
    assert driver.shell_abs_path == shell_path


@pytest.mark.parametrize("has_command", [False, True])
def test_configure_interactive_shell(has_command):
    driver = ShellDriverSh(
        shell_abs_path="/bin/sh",
        shell_env_vars={"EXISTING": "value", "ENV": "/old/init"},
        cache_dir_abs_path="/fake/cache",
    )

    driver.configure_interactive_shell(has_command)

    assert driver.shell_args == ["/bin/sh"]
    assert driver.shell_env_vars == {
        "EXISTING": "value",
        "ENV": "/fake/cache/sh/.shrc",
    }


@pytest.mark.parametrize("activate_venv", [False, True])
@patch("protoprimer.primer_kernel.write_text_file")
def test_write_init_file(mock_write_text_file, fs, activate_venv):
    driver = ShellDriverSh(
        shell_abs_path="/bin/sh",
        shell_env_vars={},
        cache_dir_abs_path="/fake/cache",
        activate_venv=activate_venv,
    )

    driver.write_init_file("/fake/venv with spaces")

    mock_write_text_file.assert_called_once_with(
        "/fake/cache/sh/.shrc",
        f"""
# Load user settings if available:
test -f "$HOME/.shrc" && . "$HOME/.shrc" || true
# Activate `venv`:
if [ "{str(activate_venv).lower()}" = "true" ]
then
    . '/fake/venv with spaces/bin/activate'
fi
""",
    )


@pytest.mark.parametrize("command_line", [None, "printf '%s' hello"])
@patch("os.execve")
@patch.object(ShellDriverSh, "write_init_file")
def test_run_shell(mock_write, mock_execve, command_line):
    driver = ShellDriverSh(
        shell_abs_path="/bin/sh",
        shell_env_vars={"EXISTING": "value"},
        cache_dir_abs_path="/fake/cache",
    )

    driver.run_shell(True, command_line, "/fake/venv")

    expected_args = ["/bin/sh", "-i"]
    if command_line is not None:
        expected_args.extend(["-c", command_line])
    mock_write.assert_called_once_with("/fake/venv")
    mock_execve.assert_called_once_with(
        "/bin/sh",
        expected_args,
        {"EXISTING": "value", "ENV": "/fake/cache/sh/.shrc"},
    )
