import os
from unittest.mock import patch

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel


def test_relationship():
    assert_test_module_name_embeds_str(primer_kernel.ShellDriverSh.__name__)


@pytest.mark.parametrize("shell_path", [None, "/bin/sh", "/usr/bin/sh"])
def test_get_shell_driver(shell_path):
    # given:

    env = {"KEEP": "value"}
    if shell_path is not None:
        env["SHELL"] = shell_path
    # when:

    with patch.dict(os.environ, env, clear=True), patch("shutil.which") as mock_which:
        driver = primer_kernel._get_shell_driver("/fake/cache", activate_venv=False)
        assert dict(os.environ) == env

    # then:

    assert isinstance(driver, primer_kernel.ShellDriverSh)
    assert driver.shell_abs_path == (shell_path or "/bin/sh")
    assert driver.activate_venv is False
    assert driver.shell_env_vars == env
    mock_which.assert_not_called()


@pytest.mark.parametrize("shell_name", ["bash", "zsh"])
def test_get_shell_driver_existing_shells(shell_name):
    with patch.dict(os.environ, {"SHELL": f"/bin/{shell_name}"}, clear=True):
        driver = primer_kernel._get_shell_driver("/fake/cache")
    assert driver.get_type().value == shell_name
    assert driver.shell_abs_path == f"/bin/{shell_name}"


@pytest.mark.parametrize("shell_path", ["/bin/fish", ""])
def test_get_shell_driver_unknown_shell(shell_path):
    with patch.dict(os.environ, {"SHELL": shell_path}, clear=True):
        with pytest.raises(ValueError, match="unknown value"):
            primer_kernel._get_shell_driver("/fake/cache")


@pytest.mark.parametrize("command_line", [None, "printf '%s\\n' hello"])
def test_run_shell(fs, command_line):
    # given:

    driver = primer_kernel.ShellDriverSh(
        shell_abs_path="/bin/sh",
        shell_env_vars={"KEEP": "value", "ENV": "/old/init"},
        cache_dir_abs_path="/fake/cache with spaces",
    )

    # when:

    with patch("os.execve") as mock_execve:
        driver.run_shell(True, command_line, "/fake/venv")
    # then:

    expected_args = ["/bin/sh", "-i"]
    if command_line is not None:
        expected_args.extend(["-c", command_line])
    mock_execve.assert_called_once_with(
        "/bin/sh",
        expected_args,
        {"KEEP": "value", "ENV": "/fake/cache with spaces/sh/.shrc"},
    )
    assert driver.get_type() == primer_kernel.ShellType.shell_sh


@pytest.mark.parametrize("activate_venv", [True, False])
def test_write_init_file(fs, activate_venv):
    # given:

    driver = primer_kernel.ShellDriverSh(
        shell_abs_path="/bin/sh",
        shell_env_vars={},
        cache_dir_abs_path="/fake/cache",
        activate_venv=activate_venv,
    )

    # when:

    driver.write_init_file("/fake/venv with spaces")

    # then:

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
