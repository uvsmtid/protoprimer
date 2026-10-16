"""The real POSIX shell must read the generated ENV file before running commands."""

import os
import shlex
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import ShellDriverSh, _get_shell_driver


def test_relationship():
    assert_test_module_name_embeds_str(ShellDriverSh.__name__)


@pytest.mark.skipif(not Path("/bin/sh").is_file(), reason="Requires a real /bin/sh")
@pytest.mark.parametrize("has_command", [False, True])
@pytest.mark.parametrize(
    "cache_dir_name",
    ["cache with spaces", "cache $HOME", "cache $(touch injected)"],
)
def test_interactive_shell_applies_init_file(tmp_path: Path, has_command: bool, cache_dir_name: str):
    # given:
    injected_file = tmp_path / "injected"
    assert not injected_file.exists()
    home_dir = tmp_path / "home"
    home_dir.mkdir()
    venv_dir = tmp_path / "venv ' $(touch injected)"
    activate_file = venv_dir / "bin" / "activate"
    activate_file.parent.mkdir(parents=True)
    marker = "activated-by-generated-ENV-" + tmp_path.name
    activate_file.write_text(
        "export SH_ENV_TEST_MARKER=" + shlex.quote(marker) + "\n" "export VIRTUAL_ENV=" + shlex.quote(str(venv_dir)) + "\n",
        encoding="utf-8",
    )

    # Do not inherit a runner's active venv or startup file: either could give a false pass.
    isolated_env = {"HOME": str(home_dir), "PATH": "/usr/bin:/bin", "SHELL": "/bin/sh"}
    with patch.dict(os.environ, isolated_env, clear=True):
        driver = _get_shell_driver(str(tmp_path / cache_dir_name))
    assert isinstance(driver, ShellDriverSh)
    driver.write_init_file(str(venv_dir))
    driver.configure_interactive_shell(has_command)

    command = 'printf "%s\\n%s\\n%s\\n%s\\n" ' '"${SH_ENV_TEST_MARKER-}" "${VIRTUAL_ENV-}" ' '"${ENV+set}" "${PROTOPRIMER_SH_INIT_FILE+set}"'
    # run_shell uses -i even with -c because POSIX sh ignores ENV in non-interactive mode.
    shell_args = driver.shell_args + ["-i"]
    shell_input = command + "\nexit\n"
    if has_command:
        shell_args += ["-c", command]
        shell_input = None

    # when:
    result = subprocess.run(
        shell_args,
        input=shell_input,
        env=driver.shell_env_vars,
        cwd=tmp_path,
        # Keep job control independent of the pytest runner's terminal:
        start_new_session=True,
        capture_output=True,
        text=True,
        check=True,
        timeout=15,
    )

    # then:
    # The startup hook must clean both variables before the user command executes.
    assert result.stdout == marker + "\n" + str(venv_dir) + "\n\n\n"
    assert not injected_file.exists()

    # Without ENV, the same real interactive shell must not see either activation value.
    no_init_env = driver.shell_env_vars.copy()
    no_init_env.pop("ENV")
    without_init = subprocess.run(
        shell_args,
        input=shell_input,
        env=no_init_env,
        cwd=tmp_path,
        start_new_session=True,
        capture_output=True,
        text=True,
        check=True,
        timeout=15,
    )
    assert without_init.stdout.splitlines()[:2] == ["", ""]
    assert not injected_file.exists()
