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


@pytest.mark.parametrize("shell_path", ["/bin/sh", "/custom/bin/sh"])
@pytest.mark.parametrize("activate_venv", [False, True])
def test_get_shell_driver_sh(shell_path, activate_venv):
    # given:
    with patch.dict(os.environ, {"SHELL": shell_path}, clear=True):
        # when:
        driver = _get_shell_driver("/fake/cache", activate_venv=activate_venv)

        # then:
        assert isinstance(driver, ShellDriverSh)
        assert driver.shell_abs_path == shell_path
        assert driver.activate_venv is activate_venv


@pytest.mark.parametrize("has_command", [False, True])
def test_configure_interactive_shell_overrides_env_in_child_only(has_command, fs):
    # given:
    parent_env = {
        "SHELL": "/bin/sh",
        "ENV": "/home/user/original-init",
        "PROTOPRIMER_SH_INIT_FILE": "/home/user/stale-init",
        "KEEP": "value",
    }
    with patch.dict(os.environ, parent_env, clear=True):
        driver = _get_shell_driver("/fake/cache with spaces")

        # when:
        driver.configure_interactive_shell(has_command)

        # then:
        assert driver.shell_args == ["/bin/sh"]
        assert driver.shell_env_vars == {
            "SHELL": "/bin/sh",
            "ENV": "${PROTOPRIMER_SH_INIT_FILE}",
            "PROTOPRIMER_SH_INIT_FILE": "/fake/cache with spaces/sh/.shrc",
            "KEEP": "value",
        }
        assert dict(os.environ) == parent_env


@pytest.mark.parametrize("activate_venv", [False, True])
@pytest.mark.parametrize(
    "venv_path, quoted_activate_path",
    [
        ("/fake/venv", "/fake/venv/bin/activate"),
        ("/fake/venv with spaces", "'/fake/venv with spaces/bin/activate'"),
        (
            "/fake/venv with 'quotes' $(touch unwanted)",
            "'/fake/venv with '\"'\"'quotes'\"'\"' $(touch unwanted)/bin/activate'",
        ),
    ],
)
@patch("protoprimer.primer_kernel.write_text_file")
def test_write_init_file_uses_posix_dot_and_literal_path(mock_write_text_file, venv_path, quoted_activate_path, activate_venv, fs):
    # given:
    driver = ShellDriverSh(
        shell_abs_path="/bin/sh",
        shell_env_vars={"ENV": "/home/user/original-init"},
        cache_dir_abs_path="/fake/cache",
        activate_venv=activate_venv,
    )

    # when:
    driver.write_init_file(venv_path)

    # then:
    mock_write_text_file.assert_called_once()
    init_path, init_content = mock_write_text_file.call_args[0]
    assert init_path == "/fake/cache/sh/.shrc"
    assert os.path.isdir("/fake/cache/sh")
    assert "unset ENV PROTOPRIMER_SH_INIT_FILE\n" in init_content
    assert f'if [ "{str(activate_venv).lower()}" = "true" ]' in init_content
    assert f"    . {quoted_activate_path}\n" in init_content
    assert "source " not in init_content
    assert "/home/user/original-init" not in init_content


@pytest.mark.parametrize(
    "start_interactive_shell, command_line, expected_args",
    [
        (True, None, ["/bin/sh", "-i"]),
        (False, "printf hello", ["/bin/sh", "-i", "-c", "printf hello"]),
        (False, "", ["/bin/sh", "-i", "-c", ""]),
    ],
)
@patch("os.execve")
@patch.object(ShellDriverSh, "write_init_file")
def test_run_shell(mock_write_init_file, mock_execve, start_interactive_shell, command_line, expected_args, fs):
    # given:
    driver = ShellDriverSh(
        shell_abs_path="/bin/sh",
        shell_env_vars={"KEEP": "value"},
        cache_dir_abs_path="/fake/cache",
    )

    # when:
    driver.run_shell(start_interactive_shell, command_line, "/fake/venv")

    # then:
    mock_write_init_file.assert_called_once_with("/fake/venv")
    mock_execve.assert_called_once_with(
        "/bin/sh",
        expected_args,
        {
            "KEEP": "value",
            "ENV": "${PROTOPRIMER_SH_INIT_FILE}",
            "PROTOPRIMER_SH_INIT_FILE": "/fake/cache/sh/.shrc",
        },
    )
