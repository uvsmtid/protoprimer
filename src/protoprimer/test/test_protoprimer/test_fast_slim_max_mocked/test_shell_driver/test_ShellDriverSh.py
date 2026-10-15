import os
import subprocess
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
    driver = ShellDriverSh(
        shell_abs_path="/bin/sh",
        shell_env_vars={},
        cache_dir_abs_path="/fake/cache",
    )

    assert driver.get_type() == ShellType.shell_sh


def test_get_init_file_basename():
    driver = ShellDriverSh(
        shell_abs_path="/bin/sh",
        shell_env_vars={},
        cache_dir_abs_path="/fake/cache",
    )

    assert driver.get_init_file_basename() == ".profile"


def test_configure_interactive_shell(fs):
    fs.create_dir("/fake/cache/sh")
    driver = ShellDriverSh(
        shell_abs_path="/bin/sh",
        shell_env_vars={},
        cache_dir_abs_path="/fake/cache",
    )

    driver.configure_interactive_shell(False)

    assert driver.shell_args == ["/bin/sh"]
    assert driver.shell_env_vars == {"ENV": os.path.join("/fake/cache", "sh", ".profile")}


def test_write_init_file_is_posix(fs):
    fs.create_file("/fake/venv/bin/activate")
    driver = ShellDriverSh(
        shell_abs_path="/bin/sh",
        shell_env_vars={},
        cache_dir_abs_path="/fake/cache",
    )

    driver.write_init_file("/fake/venv")

    with open(driver.get_init_file_abs_path(), encoding="utf-8") as init_file:
        init_script = init_file.read()
    assert "source " not in init_script
    assert ". ~/.profile" in init_script
    assert f". {os.path.join('/fake/venv', 'bin', 'activate')}" in init_script


def test_get_shell_driver_sh():
    with patch.dict(os.environ, {"SHELL": "/bin/sh"}, clear=True):
        driver = _get_shell_driver("/fake/cache")

    assert isinstance(driver, ShellDriverSh)
    assert driver.shell_abs_path == "/bin/sh"


@pytest.mark.skipif(not os.path.exists("/bin/sh"), reason="requires a POSIX /bin/sh")
def test_sh_reads_env_file_in_interactive_mode(tmp_path):
    init_file = tmp_path / ".profile"
    init_file.write_text("PROTO_PRIMER_SH_TEST=loaded\nexport PROTO_PRIMER_SH_TEST\n", encoding="utf-8")
    env = os.environ.copy()
    env["ENV"] = str(init_file)

    result = subprocess.run(
        ["/bin/sh", "-i", "-c", 'printf "%s" "$PROTO_PRIMER_SH_TEST"'],
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )

    assert result.stdout == "loaded"
