"""
FT_99_89_51_06.venv_shell.md

Run a real interactive POSIX `/bin/sh` (whatever implementation the environment has)
and verify that the init file (passed via the `ENV` env var) is applied:
it loads the user's `~/.shrc` and activates the `venv`.
"""

from __future__ import annotations

import os
import subprocess
import venv
from pathlib import Path
from unittest.mock import patch

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    _get_shell_driver,
    ShellDriverSh,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        ShellDriverSh.__name__,
    )


@pytest.mark.parametrize(
    "shell_env_var_value",
    [
        # `SHELL` is not set => fall back to `/bin/sh`:
        None,
        "/bin/sh",
    ],
)
@pytest.mark.parametrize(
    "activate_venv",
    [
        True,
        False,
    ],
)
def test_interactive_sh_applies_init_file_via_ENV(
    tmp_path: Path,
    shell_env_var_value: str | None,
    activate_venv: bool,
):

    # given:

    # A real `venv` (its real `activate` script must work in POSIX `sh`) with a space in its path:
    venv_abs_path = tmp_path / "some venv"
    venv.EnvBuilder(with_pip=False, symlinks=True).create(str(venv_abs_path))

    # Isolate from the user's `~/.shrc` - use a test one instead (with a space in its path too):
    home_abs_path = tmp_path / "some home"
    home_abs_path.mkdir()
    (home_abs_path / ".shrc").write_text("TEST_SHRC_MARKER=shrc_loaded\nexport TEST_SHRC_MARKER\n")

    # Do not inherit `VIRTUAL_ENV`, `ENV`, etc. from the test runner:
    shell_env_vars = {
        "HOME": str(home_abs_path),
        "PATH": "/usr/bin:/bin",
    }
    if shell_env_var_value is not None:
        shell_env_vars["SHELL"] = shell_env_var_value

    with patch.dict(os.environ, shell_env_vars, clear=True):
        shell_driver = _get_shell_driver(
            str(tmp_path / "cache"),
            activate_venv=activate_venv,
        )

    assert isinstance(shell_driver, ShellDriverSh)
    assert shell_driver.shell_abs_path == "/bin/sh"

    # Capture what `run_shell` passes to `os.execve` (instead of replacing the test process):
    with patch("os.execve") as mock_execve:
        shell_driver.run_shell(
            start_interactive_shell=False,
            command_line='echo "shrc=[${TEST_SHRC_MARKER:-}]"; echo "venv=[${VIRTUAL_ENV:-}]"',
            venv_abs_path=str(venv_abs_path),
        )
    exec_path, exec_args, exec_env = mock_execve.call_args[0]

    # The init file is passed via `ENV` (POSIX `sh` has no `--init-file`):
    assert exec_env["ENV"] == shell_driver.get_init_file_abs_path()
    assert "--init-file" not in exec_args

    # when:

    sub_proc = subprocess.run(
        exec_args,
        executable=exec_path,
        env=exec_env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        timeout=60,
    )

    # then:

    assert sub_proc.returncode == 0, sub_proc.stderr
    # Some `sh` implementations print a banner when interactive (e.g. `busybox` `ash`) - check the lines only:
    output_lines = sub_proc.stdout.splitlines()
    assert "shrc=[shrc_loaded]" in output_lines, sub_proc.stdout
    assert f"venv=[{venv_abs_path if activate_venv else ''}]" in output_lines, sub_proc.stdout
