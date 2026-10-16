import os
from unittest.mock import patch

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


def test_get_source_builtin():
    # given:
    driver = ShellDriverSh(
        shell_abs_path="/bin/sh",
        shell_env_vars={},
        cache_dir_abs_path="/fake/cache",
    )
    # when:
    source_builtin = driver.get_source_builtin()
    # then:
    # POSIX `sh` has no `source` builtin:
    assert source_builtin == "."


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
    # POSIX `sh` has no `--init-file` option:
    # the init file is passed via the `ENV` env var:
    assert driver.shell_env_vars == {"ENV": "/fake/cache/sh/.shrc"}
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
    assert driver.shell_env_vars == {"ENV": "/fake/cache/sh/.shrc"}
    assert driver.shell_args == ["/bin/sh"]


@patch("protoprimer.primer_kernel.write_text_file")
def test_write_init_file_posix(mock_write_text_file, fs):
    # given:
    fs.create_dir("/fake/cache")
    driver = ShellDriverSh(
        shell_abs_path="/bin/sh",
        shell_env_vars={},
        cache_dir_abs_path="/fake/cache",
    )
    # when:
    driver.write_init_file("/fake/venv")
    # then:
    # POSIX `sh` shells files with `.` instead of the non-POSIX `source`:
    mock_write_text_file.assert_called_once_with(
        "/fake/cache/sh/.shrc",
        """
# Load user settings if available:
test -f ~/.shrc && . ~/.shrc || true
# Activate `venv`:
if [ "true" = "true" ]
then
    . /fake/venv/bin/activate
fi
""",
    )


def test_get_shell_driver_shell_env_sh():
    # given:
    shell_path = f"/bin/{ShellType.shell_sh.value}"
    with patch.dict(os.environ, {"SHELL": shell_path}, clear=True):
        # when:
        driver = _get_shell_driver("/fake/cache")

        # then:
        assert isinstance(driver, ShellDriverSh)
        assert driver.shell_abs_path == shell_path


@patch("os.execve")
@patch.object(ShellDriverSh, "write_init_file")
def test_run_shell_passes_init_file_via_ENV(mock_write, mock_execve, fs):
    # given:
    fs.create_dir("/fake/cache/sh")
    driver = ShellDriverSh(
        shell_abs_path="/bin/sh",
        shell_env_vars={"VAR": "value"},
        cache_dir_abs_path="/fake/cache",
    )
    # when:
    driver.run_shell(False, "echo hello", "/fake/venv")
    # then:
    mock_write.assert_called_once_with("/fake/venv")
    mock_execve.assert_called_once_with(
        "/bin/sh",
        ["/bin/sh", "-i", "-c", "echo hello"],
        {"VAR": "value", "ENV": "/fake/cache/sh/.shrc"},
    )
