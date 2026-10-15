"""
TODO_74_35_76_27.shell_driver_fallback_to_sh.md

Run a real interactive `/bin/sh` (whatever implementation the environment has)
and verify that the init file passed via the `ENV` env var is applied.
"""

import os
import subprocess
from pathlib import Path
from unittest.mock import patch

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    _get_shell_driver,
    ConfConstGeneral,
    ShellDriverSh,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        ShellDriverSh.__name__,
    )


def test_interactive_sh_applies_init_file_via_ENV(tmp_path: Path):

    # given:

    # Fake `venv` with an `activate` script which only sets a marker:
    venv_abs_path = tmp_path / "venv"
    activate_abs_path = venv_abs_path / ConfConstGeneral.file_rel_path_venv_activate
    activate_abs_path.parent.mkdir(parents=True)
    activate_abs_path.write_text("TEST_SH_INIT_MARKER=venv_activated\nexport TEST_SH_INIT_MARKER\n")

    # Isolate from the user's `~/.shrc`:
    home_abs_path = tmp_path / "home"
    home_abs_path.mkdir()

    cache_dir_abs_path = tmp_path / "cache"

    with patch.dict(
        os.environ,
        {
            "SHELL": "/bin/sh",
            "HOME": str(home_abs_path),
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        },
        clear=True,
    ):
        shell_driver = _get_shell_driver(str(cache_dir_abs_path))

    assert isinstance(shell_driver, ShellDriverSh)

    shell_driver.write_init_file(str(venv_abs_path))
    shell_driver.configure_interactive_shell(has_command=True)

    # The init file is passed via `ENV` (no `--init-file`):
    assert shell_driver.shell_env_vars["ENV"] == shell_driver.get_init_file_abs_path()
    assert "--init-file" not in shell_driver.shell_args

    # when:

    # `ENV` is read only by interactive shells - hence, `-i`
    # (same args as `ShellDriverBase.run_shell`, but via `subprocess` instead of `os.execve`):
    sub_proc = subprocess.run(
        [
            *shell_driver.shell_args,
            "-i",
            "-c",
            'echo "marker=[${TEST_SH_INIT_MARKER}]"',
        ],
        env=shell_driver.shell_env_vars,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=30,
    )

    # then:

    assert sub_proc.returncode == 0, sub_proc.stderr
    assert "marker=[venv_activated]" in sub_proc.stdout
