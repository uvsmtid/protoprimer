import os
import shlex
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


@pytest.mark.parametrize("bash_path", [None, "/bin/bash"])
@patch.dict(os.environ, {}, clear=True)
@patch("shutil.which")
@patch("protoprimer.primer_kernel.logger.warning")
def test_get_shell_driver_no_shell_env(mock_warning, mock_which, bash_path):
    mock_which.return_value = bash_path

    driver = _get_shell_driver("/fake/cache", activate_venv=False)

    assert isinstance(driver, ShellDriverSh)
    assert driver.shell_abs_path == "/bin/sh"
    assert driver.activate_venv is False
    mock_which.assert_not_called()
    mock_warning.assert_called_once_with("env var `SHELL` is not set - assuming `/bin/sh` as default")


@pytest.mark.parametrize("shell_path", ["/bin/sh", "/usr/bin/sh"])
def test_get_shell_driver_sh(shell_path):
    with patch.dict(os.environ, {"SHELL": shell_path}, clear=True):
        driver = _get_shell_driver("/fake/cache")

    assert isinstance(driver, ShellDriverSh)
    assert driver.shell_abs_path == shell_path
    assert driver.get_type() == ShellType.shell_sh
    assert driver.get_init_file_basename() == ".shrc"


def test_get_shell_driver_bash():
    with patch.dict(os.environ, {"SHELL": "/bin/bash"}, clear=True):
        driver = _get_shell_driver("/fake/cache")

    assert isinstance(driver, ShellDriverBash)
    assert driver.shell_abs_path == "/bin/bash"


@pytest.mark.parametrize("command_line", [None, "exit 42"])
@patch("os.execve")
def test_run_shell(mock_execve, fs, command_line):
    driver = ShellDriverSh(
        shell_abs_path="/bin/sh",
        shell_env_vars={"ENV": "/old/init", "KEEP": "value"},
        cache_dir_abs_path="/fake/cache dir",
    )

    driver.run_shell(True, command_line, "/fake/venv")

    expected_args = ["/bin/sh", "-i"]
    if command_line is not None:
        expected_args.extend(["-c", command_line])
    mock_execve.assert_called_once_with(
        "/bin/sh",
        expected_args,
        {"ENV": "/fake/cache dir/sh/.shrc", "KEEP": "value"},
    )
    assert os.path.isfile(driver.get_init_file_abs_path())


def test_write_init_file_quotes_activation_path(fs):
    driver = ShellDriverSh(
        shell_abs_path="/bin/sh",
        shell_env_vars={},
        cache_dir_abs_path="/fake/cache",
    )
    venv_path = "/fake/venv with 'quotes' and ; metacharacters"

    driver.write_init_file(venv_path)

    with open(driver.get_init_file_abs_path()) as init_file:
        init_text = init_file.read()
    assert f"    . {shlex.quote(venv_path + '/bin/activate')}\n" in init_text
    assert "source " not in init_text
