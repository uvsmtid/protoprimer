from unittest.mock import patch

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
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
    init_file_basename = driver.get_init_file_basename()

    # then:
    assert init_file_basename == ".shrc"


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
    assert driver.shell_env_vars == {
        "ENV": driver.get_init_file_abs_path(),
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
    init_file_path = driver.get_init_file_abs_path()
    activate_path = driver.get_venv_activate_script_abs_path("/fake/venv")
    mock_write_text_file.assert_called_once_with(
        init_file_path,
        f"""
# Load user settings if available:
test -f ~/.shrc && . ~/.shrc || true
# Activate `venv`:
if [ "true" = "true" ]
then
    . {activate_path}
fi
""",
    )


@patch("os.execve")
def test_run_shell_builds_expected_command_line_and_env(mock_execve, fs):
    # given:
    fs.create_dir("/fake/cache/sh")

    driver = ShellDriverSh(
        shell_abs_path="/bin/sh",
        shell_env_vars={"EXISTING": "1"},
        cache_dir_abs_path="/fake/cache",
    )

    # when:
    driver.run_shell(True, None, "/fake/venv")

    # then:
    mock_execve.assert_called_once_with(
        "/bin/sh",
        [
            "/bin/sh",
            "-i",
        ],
        {
            "EXISTING": "1",
            "ENV": driver.get_init_file_abs_path(),
        },
    )


@patch("os.execve")
def test_run_shell_with_command_line(mock_execve, fs):
    # given:
    fs.create_dir("/fake/cache/sh")

    driver = ShellDriverSh(
        shell_abs_path="/bin/sh",
        shell_env_vars={},
        cache_dir_abs_path="/fake/cache",
    )

    # when:
    driver.run_shell(False, "echo hello", "/fake/venv")

    # then:
    mock_execve.assert_called_once_with(
        "/bin/sh",
        [
            "/bin/sh",
            "-i",
            "-c",
            "echo hello",
        ],
        {
            "ENV": driver.get_init_file_abs_path(),
        },
    )
