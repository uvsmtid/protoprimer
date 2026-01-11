from unittest.mock import patch
import os
import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    ShellDriverZsh,
    ShellType,
    _get_shell_driver,
    ShellDriverBash,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        ShellDriverZsh.__name__,
    )


def test_get_type():
    # given:
    driver = ShellDriverZsh(
        shell_abs_path="/bin/zsh",
        shell_env_vars={},
        cache_dir_abs_path="/fake/cache",
    )
    # when:
    shell_type = driver.get_type()
    # then:
    assert shell_type == ShellType.shell_zsh


def test_get_init_file_basename():
    # given:
    driver = ShellDriverZsh(
        shell_abs_path="/bin/zsh",
        shell_env_vars={},
        cache_dir_abs_path="/fake/cache",
    )
    # when:
    basename = driver.get_init_file_basename()
    # then:
    assert basename == ".zshrc"


@patch("sys.stdin")
def test_configure_interactive_shell_tty(mock_stdin, fs):
    # given:
    mock_stdin.isatty.return_value = True
    fs.create_dir("/fake/cache/zsh")
    driver = ShellDriverZsh(
        shell_abs_path="/bin/zsh",
        shell_env_vars={},
        cache_dir_abs_path="/fake/cache",
    )
    # when:
    driver.configure_interactive_shell(False)
    # then:
    assert driver.shell_env_vars == {"ZDOTDIR": "/fake/cache/zsh"}
    assert driver.shell_args == ["/bin/zsh"]


@patch("sys.stdin")
def test_configure_interactive_shell_pipe(mock_stdin, fs):
    # given:
    mock_stdin.isatty.return_value = False
    mock_stdin.closed = False
    fs.create_dir("/fake/cache/zsh")
    driver = ShellDriverZsh(
        shell_abs_path="/bin/zsh",
        shell_env_vars={},
        cache_dir_abs_path="/fake/cache",
    )
    # when:
    driver.configure_interactive_shell(False)
    # then:
    assert driver.shell_env_vars == {"ZDOTDIR": "/fake/cache/zsh"}
    assert driver.shell_args == ["/bin/zsh", "-s"]


def test_configure_interactive_shell_with_command(fs):
    # given:
    fs.create_dir("/fake/cache/zsh")
    driver = ShellDriverZsh(
        shell_abs_path="/bin/zsh",
        shell_env_vars={},
        cache_dir_abs_path="/fake/cache",
    )
    # when:
    driver.configure_interactive_shell(True)
    # then:
    assert driver.shell_env_vars == {"ZDOTDIR": "/fake/cache/zsh"}
    assert driver.shell_args == ["/bin/zsh"]


@patch.dict(os.environ, {}, clear=True)
@patch("shutil.which")
@patch("protoprimer.primer_kernel.logger.warning")
def test_get_shell_driver_no_shell_env(mock_warning, mock_which):
    # given:
    mock_which.return_value = "/bin/bash"

    # when:
    driver = _get_shell_driver("/fake/cache")

    # then:
    mock_warning.assert_called_once_with(
        "env var `SHELL` is not set - assuming `bash` as default"
    )
    assert isinstance(driver, ShellDriverBash)
    assert driver.shell_abs_path == "/bin/bash"


@patch.dict(os.environ, {}, clear=True)
@patch("shutil.which")
@patch("protoprimer.primer_kernel.logger.warning")
def test_get_shell_driver_no_shell_env_no_bash(mock_warning, mock_which):
    # given:
    mock_which.return_value = None

    # when:
    driver = _get_shell_driver("/fake/cache")

    # then:
    mock_warning.assert_called_once_with(
        "env var `SHELL` is not set - assuming `bash` as default"
    )
    assert isinstance(driver, ShellDriverBash)
    assert driver.shell_abs_path is None


def test_get_shell_driver_unknown_shell():
    # given:
    with patch.dict(os.environ, {"SHELL": "/bin/fish"}, clear=True):
        # when/then:
        with pytest.raises(ValueError) as excinfo:
            _get_shell_driver("/fake/cache")
        assert "env var `SHELL` has unknown value [/bin/fish]" in str(excinfo.value)


def test_get_shell_driver_zsh():
    # given:
    shell_path = f"/bin/{ShellType.shell_zsh.value}"
    with patch.dict(os.environ, {"SHELL": shell_path}, clear=True):
        # when:
        driver = _get_shell_driver("/fake/cache")

        # then:
        assert isinstance(driver, ShellDriverZsh)
        assert driver.shell_abs_path == shell_path
