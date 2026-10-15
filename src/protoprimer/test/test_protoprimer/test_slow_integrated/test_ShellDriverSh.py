import os
import subprocess
import venv
from pathlib import Path
from unittest.mock import patch

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import _get_shell_driver, ShellDriverSh


def test_relationship():
    assert_test_module_name_embeds_str(ShellDriverSh.__name__)


@pytest.mark.parametrize("shell_is_set", [True, False])
@pytest.mark.parametrize("activate_venv", [True, False])
def test_interactive_init_file(tmp_path: Path, shell_is_set, activate_venv):
    # A real activation script, with spaces and a quote in its path.
    venv_path = tmp_path / "test's venv"
    venv.EnvBuilder(with_pip=False).create(str(venv_path))
    home_path = tmp_path / "home with spaces"
    home_path.mkdir()
    (home_path / ".shrc").write_text("export SH_INIT_MARKER=loaded_from_shrc\n")

    # Do not inherit the test runner's virtualenv, ENV, or user startup files.
    shell_env = {"HOME": str(home_path), "PATH": "/usr/bin:/bin"}
    if shell_is_set:
        shell_env["SHELL"] = "/bin/sh"
    with patch.dict(os.environ, shell_env, clear=True):
        driver = _get_shell_driver(str(tmp_path / "shell cache"), activate_venv)

    # Capture the exec boundary, then run exactly that command in a subprocess.
    with patch("os.execve") as mock_execve:
        driver.run_shell(
            True,
            'printf "%s\\n" "$SH_INIT_MARKER" "${VIRTUAL_ENV-unset}"',
            str(venv_path),
        )
    executable, args, env = mock_execve.call_args[0]
    result = subprocess.run(
        args,
        executable=executable,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        timeout=15,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == [
        "loaded_from_shrc",
        str(venv_path) if activate_venv else "unset",
    ]
