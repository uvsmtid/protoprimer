import os
from unittest.mock import patch

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    _get_shell_driver,
    ShellDriverBash,
    ShellDriverSh,
    ShellDriverZsh,
    ShellType,
)


def test_relationship():
    assert_test_module_name_embeds_str(ShellDriverSh.__name__)


@pytest.mark.parametrize(
    "shell_path, driver_type",
    [
        ("/bin/sh", ShellDriverSh),
        ("/usr/bin/sh", ShellDriverSh),
        ("/bin/bash", ShellDriverBash),
        ("/bin/zsh", ShellDriverZsh),
    ],
)
def test_get_shell_driver(shell_path, driver_type):
    with patch.dict(os.environ, {"SHELL": shell_path}, clear=True):
        driver = _get_shell_driver("/fake/cache", activate_venv=False)

    assert isinstance(driver, driver_type)
    assert driver.shell_abs_path == shell_path
    assert driver.activate_venv is False


@pytest.mark.parametrize("command_line", [None, "printf '%s\\n' hello"])
@patch("os.execve")
def test_run_shell(mock_execve, fs, command_line):
    driver = ShellDriverSh(
        shell_abs_path="/bin/sh",
        shell_env_vars={"KEEP": "value", "ENV": "/old/init"},
        cache_dir_abs_path="/fake/cache with spaces",
    )

    driver.run_shell(True, command_line, "/fake/venv")

    expected_args = ["/bin/sh", "-i"]
    if command_line is not None:
        expected_args.extend(["-c", command_line])
    mock_execve.assert_called_once_with(
        "/bin/sh",
        expected_args,
        {"KEEP": "value", "ENV": "/fake/cache with spaces/sh/.shrc"},
    )
    assert driver.get_type() == ShellType.shell_sh


@pytest.mark.parametrize("activate_venv", [True, False])
def test_write_init_file(fs, activate_venv):
    driver = ShellDriverSh(
        shell_abs_path="/bin/sh",
        shell_env_vars={},
        cache_dir_abs_path="/fake/cache",
        activate_venv=activate_venv,
    )

    driver.write_init_file("/fake/venv with spaces")

    with open(driver.get_init_file_abs_path()) as init_file:
        assert (
            init_file.read()
            == f"""
# Load user settings if available:
test -f "$HOME/.shrc" && . "$HOME/.shrc" || true
# Activate `venv`:
if [ "{str(activate_venv).lower()}" = "true" ]
then
    . '/fake/venv with spaces/bin/activate'
fi
"""
        )
