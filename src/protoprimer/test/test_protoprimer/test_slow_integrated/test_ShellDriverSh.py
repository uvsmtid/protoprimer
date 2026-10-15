import os
import subprocess
import sys
import venv
from pathlib import Path

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import ShellDriverSh


def test_relationship():
    assert_test_module_name_embeds_str(ShellDriverSh.__name__)


@pytest.mark.parametrize("activate_venv", [False, True])
@pytest.mark.parametrize("has_command", [False, True])
@pytest.mark.parametrize("shell_path", [None, "/bin/sh"])
def test_interactive_sh_initialization(
    tmp_path: Path,
    activate_venv,
    has_command,
    shell_path,
):
    # given:

    home_path = tmp_path / "home with 'quotes'; $(touch injected)"
    home_path.mkdir()
    (home_path / ".shrc").write_text("export PROTOPRIMER_SH_INIT=initialized\n")
    venv_path = tmp_path / "venv with 'quotes'; spaces"
    if activate_venv:
        venv.EnvBuilder(with_pip=False).create(str(venv_path))

    shell_env = os.environ.copy()
    shell_env["HOME"] = str(home_path)
    shell_env.pop("VIRTUAL_ENV", None)
    shell_env.pop("PROTOPRIMER_SH_INIT", None)
    if shell_path is None:
        shell_env.pop("SHELL", None)
        if not activate_venv:
            # Exercise the fallback without any executables (including Bash) in PATH.
            shell_env["PATH"] = ""
    else:
        shell_env["SHELL"] = shell_path

    command_line = """printf '%s\\n' "$PROTOPRIMER_SH_INIT" "${VIRTUAL_ENV-unset}"
"""
    if activate_venv:
        command_line += "python -c 'import sys; print(sys.prefix)'\n"
    command_line += "exit 0\n"
    child_script = """
import sys
from protoprimer.primer_kernel import _get_shell_driver

shell_driver = _get_shell_driver(sys.argv[1], activate_venv=sys.argv[3] == "True")
shell_driver.run_shell(True, sys.argv[4] or None, sys.argv[2])
"""
    cache_path = tmp_path / "cache with 'quotes'; spaces"

    # when:

    sub_proc = subprocess.run(
        [
            sys.executable,
            "-c",
            child_script,
            str(cache_path),
            str(venv_path),
            str(activate_venv),
            command_line if has_command else "",
        ],
        env=shell_env,
        cwd=str(tmp_path),
        input="" if has_command else command_line,
        capture_output=True,
        text=True,
        timeout=15,
    )

    # then:

    assert sub_proc.returncode == 0
    expected_output = [
        "initialized",
        str(venv_path) if activate_venv else "unset",
    ]
    if activate_venv:
        expected_output.append(str(venv_path))
    assert sub_proc.stdout.splitlines() == expected_output
    assert (cache_path / "sh" / ".shrc").is_file()
    assert not (tmp_path / "injected").exists()
