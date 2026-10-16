import os
import subprocess
import sys
import venv

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import ShellDriverSh


def test_relationship():
    assert_test_module_name_embeds_str(ShellDriverSh.__name__)


@pytest.mark.parametrize(
    "has_command, activate_venv, user_settings",
    [(True, True, True), (False, True, False), (True, False, True)],
)
def test_interactive_shell_reads_init_file(tmp_path, has_command, activate_venv, user_settings):
    home_path = tmp_path / "home dir"
    home_path.mkdir()
    if user_settings:
        (home_path / ".shrc").write_text("export SH_USER_SETTING=loaded\n")
    venv_path = tmp_path / "venv dir"
    if activate_venv:
        venv.EnvBuilder(with_pip=False).create(str(venv_path))
    # An unused venv need not exist when activation is disabled.
    cache_path = tmp_path / "cache dir"
    environment = os.environ.copy()
    environment.update({"SHELL": "/bin/sh", "HOME": str(home_path), "ENV": "/unused/init"})
    environment.pop("VIRTUAL_ENV", None)
    environment.pop("SH_USER_SETTING", None)
    command = 'printf "%s\\n" "${SH_USER_SETTING-unset}" "${VIRTUAL_ENV-unset}" "$ENV"; exit 0'
    child_code = """
import sys
from protoprimer.primer_kernel import _get_shell_driver

driver = _get_shell_driver(sys.argv[1], activate_venv=sys.argv[3] == "True")
driver.run_shell(True, sys.argv[4] if len(sys.argv) > 4 else None, sys.argv[2])
"""
    args = [sys.executable, "-c", child_code, str(cache_path), str(venv_path), str(activate_venv)]
    if has_command:
        args.append(command)

    result = subprocess.run(
        args,
        env=environment,
        input="" if has_command else command + "\n",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == [
        "loaded" if user_settings else "unset",
        str(venv_path) if activate_venv else "unset",
        str(cache_path / "sh" / ".shrc"),
    ]
