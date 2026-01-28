import logging
from unittest.mock import (
    MagicMock,
    patch,
)

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    ShellDriverBase,
    ShellType,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        ShellDriverBase.__name__,
    )


class ShellDriverConcrete(ShellDriverBase):
    def get_type(self) -> ShellType:
        return ShellType.shell_bash

    def get_init_file_basename(self):
        return ".bashrc"

    def configure_interactive_shell(self, has_command: bool) -> None:
        pass


def test_shell_driver_base_is_instantiable(fs):
    # given:
    fs.create_dir("/fake/cache")
    # when:
    driver = ShellDriverConcrete(
        shell_abs_path="/bin/bash",
        shell_env_vars={},
        cache_dir_abs_path="/fake/cache",
    )
    # then:
    assert isinstance(driver, ShellDriverBase)


def test_get_init_file_abs_path(fs):
    # given:
    fs.create_dir("/fake/cache")
    driver = ShellDriverConcrete(
        shell_abs_path="/bin/bash",
        shell_env_vars={},
        cache_dir_abs_path="/fake/cache",
    )
    # when:
    path = driver.get_init_file_abs_path()
    # then:
    assert path == "/fake/cache/bash/.bashrc"


def test_get_venv_activate_script_abs_path():
    # given:
    # when:
    path = ShellDriverBase.get_venv_activate_script_abs_path("/fake/venv")
    # then:
    assert path == "/fake/venv/bin/activate"


@patch("protoprimer.primer_kernel.write_text_file")
def test_write_init_file(mock_write_text_file, fs):
    # given:
    fs.create_dir("/fake/cache")
    driver = ShellDriverConcrete(
        shell_abs_path="/bin/bash",
        shell_env_vars={},
        cache_dir_abs_path="/fake/cache",
    )
    # when:
    driver.write_init_file("/fake/venv")
    # then:
    mock_write_text_file.assert_called_once_with(
        "/fake/cache/bash/.bashrc",
        """
# Load user settings if available:
test -f ~/.bashrc && source ~/.bashrc || true
# Activate `venv`:
source /fake/venv/bin/activate
""",
    )


@patch("os.execve")
@patch.object(ShellDriverConcrete, "write_init_file")
@patch.object(ShellDriverConcrete, "configure_interactive_shell")
def test_run_shell(mock_configure, mock_write, mock_execve):
    # given:
    driver = ShellDriverConcrete(
        shell_abs_path="/bin/bash",
        shell_env_vars={"VAR": "value"},
        cache_dir_abs_path="/fake/cache",
    )
    mock_log_handler = MagicMock()
    mock_log_handler.level = logging.INFO
    # when:
    driver.run_shell("echo hello", mock_log_handler, "/fake/venv")
    # then:
    mock_write.assert_called_once_with("/fake/venv")
    mock_configure.assert_called_once_with(True)
    mock_execve.assert_called_once_with(
        "/bin/bash",
        ["/bin/bash", "-i", "-c", "echo hello"],
        {"VAR": "value"},
    )


def test_get_type_raises_not_implemented_error():
    # given:
    driver = ShellDriverConcrete(
        shell_abs_path="/bin/bash",
        shell_env_vars={},
        cache_dir_abs_path="/fake/cache",
    )
    # when/then:
    with pytest.raises(NotImplementedError):
        ShellDriverBase.get_type(driver)


def test_get_init_file_basename_raises_not_implemented_error():
    # given:
    driver = ShellDriverConcrete(
        shell_abs_path="/bin/bash",
        shell_env_vars={},
        cache_dir_abs_path="/fake/cache",
    )
    # when/then:
    with pytest.raises(NotImplementedError):
        ShellDriverBase.get_init_file_basename(driver)


def test_configure_interactive_shell_raises_not_implemented_error():
    # given:
    driver = ShellDriverConcrete(
        shell_abs_path="/bin/bash",
        shell_env_vars={},
        cache_dir_abs_path="/fake/cache",
    )
    # when/then:
    with pytest.raises(NotImplementedError):
        ShellDriverBase.configure_interactive_shell(driver, has_command=False)
