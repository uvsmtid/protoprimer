import os
import subprocess
import venv
from unittest.mock import patch

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel


def test_relationship():
    assert_test_module_name_embeds_str(primer_kernel.ShellDriverSh.__name__)


@pytest.mark.parametrize("shell_is_set", [True, False])
@pytest.mark.parametrize("activate_venv", [True, False])
@pytest.mark.parametrize("has_command", [True, False])
def test_interactive_init_file(tmp_path, shell_is_set, activate_venv, has_command):
    # given:

    venv_path = tmp_path / "test's venv"
    venv.EnvBuilder(with_pip=False, symlinks=True).create(str(venv_path))
    home_path = tmp_path / "isolated home"
    home_path.mkdir()
    (home_path / ".shrc").write_text("export SH_INIT_MARKER=from_init_file\n")

    # Neither inherited activation nor user startup files may satisfy the assertions.
    # An empty PATH also proves the fallback does not need to locate bash.
    shell_env = {"HOME": str(home_path), "PATH": ""}
    if shell_is_set:
        shell_env["SHELL"] = "/bin/sh"
    with patch.dict(os.environ, shell_env, clear=True):
        driver = primer_kernel._get_shell_driver(
            str(tmp_path / "shell cache"),
            activate_venv,
        )

    # when:

    command = 'printf "%s\\n" "${SH_INIT_MARKER-unset}" "${VIRTUAL_ENV-unset}"'
    with patch("os.execve") as mock_execve:
        driver.run_shell(
            True,
            command if has_command else None,
            str(venv_path),
        )
    executable, args, env = mock_execve.call_args[0]

    def run_shell(shell_env):
        result = subprocess.run(
            args,
            executable=executable,
            env=shell_env,
            input=None if has_command else command + "\nexit\n",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            timeout=15,
        )
        assert result.returncode == 0, result.stderr
        return result.stdout.splitlines()

    # then:

    # Negative control: without ENV the same process must not report initialization.
    without_init = env.copy()
    without_init.pop("ENV")
    assert run_shell(without_init) == ["unset", "unset"]
    assert run_shell(env) == ["from_init_file", str(venv_path) if activate_venv else "unset"]
