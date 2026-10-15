import os
import subprocess
from unittest.mock import patch

import pytest

from protoprimer.primer_kernel import _get_shell_driver


@pytest.mark.skipif(not os.path.isfile("/bin/sh"), reason="POSIX shell required")
@pytest.mark.parametrize("activate_venv", [False, True])
def test_ShellDriverSh_applies_init_file(tmp_path, activate_venv):
    home = tmp_path / "home with spaces"
    home.mkdir()
    (home / ".shrc").write_text("export USER_INIT_APPLIED=user-init\n")
    venv = tmp_path / "venv with 'quotes'"
    (venv / "bin").mkdir(parents=True)
    (venv / "bin" / "activate").write_text("export VENV_INIT_APPLIED=venv-init\n")
    with patch.dict(os.environ, {"SHELL": "/bin/sh", "HOME": str(home)}, clear=True):
        driver = _get_shell_driver(str(tmp_path / "cache with spaces"), activate_venv)
    driver.write_init_file(str(venv))
    driver.configure_interactive_shell(True)
    command = 'printf "%s|%s" "$USER_INIT_APPLIED" "${VENV_INIT_APPLIED-unset}"'
    result = subprocess.run(
        driver.shell_args + ["-i", "-c", command],
        env=driver.shell_env_vars,
        input="",
        capture_output=True,
        text=True,
        timeout=10,
        check=True,
    )
    assert result.stdout == "user-init|" + ("venv-init" if activate_venv else "unset")
