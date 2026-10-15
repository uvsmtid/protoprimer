import os
import shlex
from unittest.mock import patch

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    _get_shell_driver,
    EnvVar,
    ShellDriverBash,
    ShellDriverSh,
    ShellDriverZsh,
    ShellType,
)


def test_relationship():
    assert_test_module_name_embeds_str(ShellDriverSh.__name__)


@patch.dict(os.environ, {}, clear=True)
@patch("shutil.which")
@patch("protoprimer.primer_kernel.logger.warning")
@pytest.mark.parametrize("bash_path", [None, "/bin/bash"])
def test_get_shell_driver_no_shell_env(
    mock_warning,
    mock_which,
    bash_path,
):
    # given:

    mock_which.return_value = bash_path

    # when:

    shell_driver = _get_shell_driver("/fake/cache")

    # then:

    assert shell_driver.get_type().value == "sh"
    assert isinstance(shell_driver, ShellDriverSh)
    assert shell_driver.shell_abs_path == "/bin/sh"
    mock_which.assert_not_called()
    mock_warning.assert_called_once_with("env var `SHELL` is not set - falling back to `/bin/sh`")


@pytest.mark.parametrize("shell_path", ["/bin/sh", "/usr/bin/sh", "/custom/bin/sh"])
def test_get_shell_driver_sh(
    shell_path,
    monkeypatch,
):
    # given:

    monkeypatch.setenv("SHELL", shell_path)

    # when:

    shell_driver = _get_shell_driver("/fake/cache")

    # then:

    assert shell_driver.get_type().value == "sh"
    assert isinstance(shell_driver, ShellDriverSh)
    assert shell_driver.shell_abs_path == shell_path


@pytest.mark.parametrize(
    "shell_path, driver_type",
    [
        (None, ShellDriverSh),
        ("/bin/sh", ShellDriverSh),
        ("/bin/bash", ShellDriverBash),
        ("/bin/zsh", ShellDriverZsh),
    ],
)
@pytest.mark.parametrize("activate_venv", [False, True])
def test_get_shell_driver_environment_isolation(
    shell_path,
    driver_type,
    activate_venv,
    monkeypatch,
):
    # given:

    if shell_path is None:
        monkeypatch.delenv("SHELL", raising=False)
    else:
        monkeypatch.setenv("SHELL", shell_path)
    monkeypatch.setenv("KEEP_ME", "original")
    for env_var in EnvVar:
        monkeypatch.setenv(env_var.value, "internal")
    original_env = os.environ.copy()

    # when:

    shell_driver = _get_shell_driver(
        "/fake/cache",
        activate_venv=activate_venv,
    )
    shell_driver.shell_env_vars["KEEP_ME"] = "changed"

    # then:

    assert isinstance(shell_driver, driver_type)
    assert shell_driver.shell_abs_path == (shell_path or "/bin/sh")
    assert shell_driver.activate_venv is activate_venv
    assert shell_driver.shell_env_vars.get("SHELL") == shell_path
    assert all(env_var.value not in shell_driver.shell_env_vars for env_var in EnvVar)
    assert os.environ == original_env


def test_get_type_and_init_file():
    # given:

    shell_driver = ShellDriverSh(
        shell_abs_path="/bin/sh",
        shell_env_vars={},
        cache_dir_abs_path="/fake/cache",
    )

    # when/then:

    assert ShellType.shell_sh.value == "sh"
    assert shell_driver.get_type() == ShellType.shell_sh
    assert shell_driver.get_init_file_basename() == ".shrc"
    assert shell_driver.get_init_file_abs_path() == "/fake/cache/sh/.shrc"


@pytest.mark.parametrize("has_command", [False, True])
def test_configure_interactive_shell(has_command):
    # given:

    shell_driver = ShellDriverSh(
        shell_abs_path="/bin/sh",
        shell_env_vars={"ENV": "/old/init", "KEEP_ME": "value"},
        cache_dir_abs_path="/fake/cache with spaces",
    )

    # when:

    shell_driver.configure_interactive_shell(has_command)

    # then:

    assert shell_driver.shell_env_vars == {
        "ENV": "/fake/cache with spaces/sh/.shrc",
        "KEEP_ME": "value",
    }
    assert shell_driver.shell_args == ["/bin/sh"]


@pytest.mark.parametrize("activate_venv", [False, True])
def test_write_init_file(
    fs,
    activate_venv,
):
    # given:

    shell_driver = ShellDriverSh(
        shell_abs_path="/bin/sh",
        shell_env_vars={},
        cache_dir_abs_path="/fake/cache",
        activate_venv=activate_venv,
    )
    venv_path = "/fake/venv with 'quotes'; $HOME"

    # when:

    shell_driver.write_init_file(venv_path)

    # then:

    with open(shell_driver.get_init_file_abs_path()) as init_file:
        assert (
            init_file.read()
            == f"""
# Load user settings if available:
test -f "$HOME/.shrc" && . "$HOME/.shrc" || true
# Activate `venv`:
if [ "{str(activate_venv).lower()}" = "true" ]
then
    . {shlex.quote(venv_path + "/bin/activate")}
fi
"""
        )


@patch("os.execve")
@pytest.mark.parametrize(
    "start_interactive_shell, command_line, expected_args",
    [
        (True, None, ["/bin/sh", "-i"]),
        (False, "printf '%s' hello", ["/bin/sh", "-i", "-c", "printf '%s' hello"]),
    ],
)
def test_run_shell(
    mock_execve,
    fs,
    start_interactive_shell,
    command_line,
    expected_args,
):
    # given:

    shell_driver = ShellDriverSh(
        shell_abs_path="/bin/sh",
        shell_env_vars={"KEEP_ME": "value"},
        cache_dir_abs_path="/fake/cache",
    )

    # when:

    shell_driver.run_shell(
        start_interactive_shell,
        command_line,
        "/fake/venv",
    )

    # then:

    mock_execve.assert_called_once_with(
        "/bin/sh",
        expected_args,
        {"KEEP_ME": "value", "ENV": "/fake/cache/sh/.shrc"},
    )
    assert os.path.isfile(shell_driver.get_init_file_abs_path())
