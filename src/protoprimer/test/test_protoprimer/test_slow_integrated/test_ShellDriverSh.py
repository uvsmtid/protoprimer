import os
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from protoprimer.primer_kernel import (
    _get_shell_driver,
    ShellDriverSh,
)


@pytest.mark.skipif(not Path("/bin/sh").exists(), reason="Requires a POSIX /bin/sh")
@pytest.mark.parametrize("activate_venv", [False, True])
def test_interactive_shell_applies_init_file(tmp_path: Path, activate_venv):
    # Use a private HOME so the test never reads the runner's shell settings.
    home_path = tmp_path / "home"
    home_path.mkdir()
    (home_path / ".shrc").write_text("export SH_USER_SETTINGS=loaded\n")
    venv_path = tmp_path / "venv with spaces and 'quotes'"
    (venv_path / "bin").mkdir(parents=True)
    (venv_path / "bin" / "activate").write_text("export SH_VENV_ACTIVATED=yes\n")
    with patch.dict(
        os.environ,
        {"SHELL": "/bin/sh", "HOME": str(home_path), "PATH": "/usr/bin:/bin"},
        clear=True,
    ):
        driver = _get_shell_driver(str(tmp_path / "cache"), activate_venv=activate_venv)
    assert isinstance(driver, ShellDriverSh)

    driver.write_init_file(str(venv_path))
    driver.configure_interactive_shell(has_command=True)
    result = subprocess.run(
        [*driver.shell_args, "-i", "-c", 'printf \'%s:%s\' "$SH_USER_SETTINGS" "${SH_VENV_ACTIVATED-unset}"'],
        env=driver.shell_env_vars,
        capture_output=True,
        text=True,
        timeout=10,
        check=True,
    )

    assert result.stdout == ("loaded:yes" if activate_venv else "loaded:unset")
