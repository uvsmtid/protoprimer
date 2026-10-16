import os
import subprocess
from unittest.mock import patch

import pytest

from protoprimer.primer_kernel import (
    _get_shell_driver,
    ShellDriverBash,
    ShellDriverSh,
    ShellDriverZsh,
    ShellType,
)


@pytest.mark.parametrize("shell", ["/bin/sh", "/usr/bin/sh"])
def test_get_shell_driver_sh(shell):
    with patch.dict(os.environ, {"SHELL": shell}, clear=True):
        driver = _get_shell_driver("/fake/cache")
    assert isinstance(driver, ShellDriverSh)
    assert driver.shell_abs_path == shell
    assert driver.get_type() == ShellType.shell_sh


@pytest.mark.parametrize("shell, driver_type", [("bash", ShellDriverBash), ("zsh", ShellDriverZsh)])
def test_get_shell_driver_existing_shells(shell, driver_type):
    with patch.dict(os.environ, {"SHELL": "/bin/" + shell}, clear=True):
        assert isinstance(_get_shell_driver("/fake/cache"), driver_type)


@patch("os.execve")
def test_run_shell_command_and_env(mock_execve, tmp_path):
    driver = ShellDriverSh("/bin/sh", {"KEEP": "value", "ENV": "/old/init"}, str(tmp_path))
    driver.run_shell(False, "printf ok", "/venv with spaces")
    mock_execve.assert_called_once_with(
        "/bin/sh",
        ["/bin/sh", "-i", "-c", "printf ok"],
        {"KEEP": "value", "ENV": str(tmp_path / "sh" / ".shrc")},
    )
    assert ". '/venv with spaces/bin/activate'" in (tmp_path / "sh" / ".shrc").read_text()


@pytest.mark.parametrize("activate", [True, False])
def test_sh_interactive_init_applied(tmp_path, activate):
    # Execute the actual generated init file in /bin/sh, without inherited
    # VIRTUAL_ENV or ENV values that could make a broken init look successful.
    user_home = tmp_path / "user home"
    user_home.mkdir()
    (user_home / ".shrc").write_text("export USER_INIT_PROBE=user-settings-loaded\n")
    venv_path = tmp_path / "venv's directory"
    (venv_path / "bin").mkdir(parents=True)
    (venv_path / "bin" / "activate").write_text("export ACTIVATION_PROBE=venv-loaded\n")
    with patch.dict(os.environ, {"SHELL": "/bin/sh", "HOME": str(user_home)}, clear=True):
        driver = _get_shell_driver(str(tmp_path / "cache"), activate_venv=activate)
    driver.write_init_file(str(venv_path))
    driver.configure_interactive_shell(True)
    result = subprocess.run(
        [driver.shell_abs_path, "-i", "-c", 'printf "%s|%s" "$USER_INIT_PROBE" "$ACTIVATION_PROBE"'],
        env=driver.shell_env_vars,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == "user-settings-loaded|" + ("venv-loaded" if activate else "")
