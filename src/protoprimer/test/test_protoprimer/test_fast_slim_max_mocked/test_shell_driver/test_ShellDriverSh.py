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


@patch.dict(os.environ, {}, clear=True)
@patch("shutil.which")
@patch("protoprimer.primer_kernel.logger.warning")
def test_get_shell_driver_no_shell_env_no_bash_with_sh(mock_warning, mock_which):
    # given:
    # `bash` is not in `PATH`, but POSIX `sh` is:
    mock_which.side_effect = [None, "/bin/sh"]

    # when:
    driver = _get_shell_driver("/fake/cache")

    # then:
    mock_warning.assert_any_call("`bash` is not in `PATH` - falling back to `sh`")
    assert isinstance(driver, ShellDriverSh)
    assert driver.shell_abs_path == "/bin/sh"


@patch.dict(os.environ, {}, clear=True)
@patch("shutil.which")
@patch("protoprimer.primer_kernel.logger.warning")
def test_get_shell_driver_no_shell_env_no_bash_no_sh(mock_warning, mock_which):
    # given:
    # Neither `bash` nor `sh` is in `PATH`:
    mock_which.return_value = None

    # when:
    driver = _get_shell_driver("/fake/cache")

    # then:
    # The last resort is the standard location of the POSIX shell:
    mock_warning.assert_any_call("`bash` is not in `PATH` - falling back to `sh`")
    assert isinstance(driver, ShellDriverSh)
    assert driver.shell_abs_path == "/bin/sh"
