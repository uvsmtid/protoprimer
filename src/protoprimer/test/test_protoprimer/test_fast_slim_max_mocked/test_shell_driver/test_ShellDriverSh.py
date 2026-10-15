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


def test_configure_interactive_shell_without_command(fs):
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
    assert driver.shell_env_vars == {
        "ENV": "/fake/cache/sh/.shrc",
    }
    assert driver.shell_args == [
        "/bin/sh",
    ]


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
    assert driver.shell_env_vars == {
        "ENV": "/fake/cache/sh/.shrc",
    }
    assert driver.shell_args == [
        "/bin/sh",
    ]


@patch("protoprimer.primer_kernel.write_text_file")
def test_write_init_file(mock_write_text_file, fs):
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
    mock_write_text_file.assert_called_once_with(
        driver.get_init_file_abs_path(),
        f"""
# Load user settings if available:
test -f ~/.shrc && . ~/.shrc || true
# Activate `venv`:
if [ "true" = "true" ]
then
    . {driver.get_venv_activate_script_abs_path("/fake/venv")}
fi
""",
    )


@patch.dict(os.environ, {}, clear=True)
@patch("protoprimer.primer_kernel.logger.warning")
def test_get_shell_driver_no_shell_env(mock_warning):
    # when:
    driver = _get_shell_driver("/fake/cache")

    # then:
    mock_warning.assert_called_once_with("env var `SHELL` is not set - assuming `/bin/sh` as default")
    assert isinstance(driver, ShellDriverSh)
    assert driver.shell_abs_path == "/bin/sh"


def test_get_shell_driver_sh():
    # given:
    shell_path = "/bin/sh"
    with patch.dict(os.environ, {"SHELL": shell_path}, clear=True):
        # when:
        driver = _get_shell_driver("/fake/cache")

        # then:
        assert isinstance(driver, ShellDriverSh)
        assert driver.shell_abs_path == shell_path
