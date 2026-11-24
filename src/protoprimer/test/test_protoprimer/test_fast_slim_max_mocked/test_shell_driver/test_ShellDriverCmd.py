import os
import signal
import subprocess
from unittest.mock import patch

from local_test.case_condition import requires_windows
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    _get_shell_driver,
    _ShellDriverCmd,
    _ShellType,
    _TargetPlatform,
)

VENV = "C:\\fake dir\\venv"
ACTIVATE = os.path.join(VENV, primer_kernel._ConfConstGeneral.file_rel_path_venv_activate)


def make_driver(activate_venv=True) -> _ShellDriverCmd:
    return _ShellDriverCmd(
        shell_abs_path="C:\\Windows\\cmd.exe",
        shell_env_vars={"A": "B"},
        cache_dir_abs_path="C:\\fake\\cache",
        activate_venv=activate_venv,
    )


def test_relationship():
    assert_test_module_name_embeds_str(_ShellDriverCmd.__name__)


def test_get_type():
    assert make_driver().get_type() == _ShellType.shell_cmd


def test_interactive_command_line():
    driver = make_driver()
    driver.compose_shell_args(None, VENV)
    assert driver.shell_args == [f'"C:\\Windows\\cmd.exe" /S /K "call "{ACTIVATE}""']


def test_interactive_without_activation():
    driver = make_driver(activate_venv=False)
    driver.compose_shell_args(None, VENV)
    assert driver.shell_args == ['"C:\\Windows\\cmd.exe"']


def test_command_line_with_activation():
    driver = make_driver()
    driver.compose_shell_args("echo hi", VENV)
    assert driver.shell_args == [f'"C:\\Windows\\cmd.exe" /S /C "call "{ACTIVATE}" && echo hi"']


def test_command_line_without_activation():
    driver = make_driver(activate_venv=False)
    driver.compose_shell_args("echo hi", VENV)
    assert driver.shell_args == ['"C:\\Windows\\cmd.exe" /S /C "echo hi"']


def test_write_init_file_is_noop():
    with patch(f"{primer_kernel.__name__}._write_text_file") as mock_write:
        make_driver().write_init_file(VENV)
    mock_write.assert_not_called()


def test_run_shell_runs_child_returns_exit_code_and_restores_sigint():
    driver = make_driver()
    previous = signal.getsignal(signal.SIGINT)
    with patch("subprocess.run", return_value=subprocess.CompletedProcess([], 7)) as mock_run:
        assert driver.run_shell(False, "echo hi", VENV) == 7
    mock_run.assert_called_once_with(driver.shell_args[0], env={"A": "B"})
    assert signal.getsignal(signal.SIGINT) == previous


def test_run_shell_without_command_and_not_interactive_does_nothing():
    with patch("subprocess.run") as mock_run:
        assert make_driver().run_shell(False, None, VENV) == 0
    mock_run.assert_not_called()


def test_get_shell_driver_picks_cmd_on_windows_ignoring_shell_env_var():
    env = {"SHELL": "/usr/bin/bash", "COMSPEC": "C:\\Windows\\cmd.exe"}
    with patch(f"{primer_kernel.__name__}._get_target_platform", return_value=_TargetPlatform.platform_windows), patch.dict(os.environ, env, clear=True):
        driver = _get_shell_driver("C:\\fake\\cache")
    assert isinstance(driver, _ShellDriverCmd)
    assert driver.shell_abs_path == "C:\\Windows\\cmd.exe"


@requires_windows
def test_real_cmd_runs_command_with_spaces_in_path(tmp_path):
    # given: a fake `venv` (with a space in the path) with an activate script:
    venv = tmp_path / "my venv"
    scripts = venv / primer_kernel._ConfConstGeneral.name_venv_bin_dir
    scripts.mkdir(parents=True)
    (scripts / "activate.bat").write_text("@set ACTIVATED=yes\r\n")
    driver = _ShellDriverCmd(
        shell_abs_path=os.environ["COMSPEC"],
        shell_env_vars=os.environ.copy(),
        cache_dir_abs_path=str(tmp_path / "cache"),
    )
    out = tmp_path / "out.txt"
    # when:
    exit_code = driver.run_shell(False, f'echo %ACTIVATED%> "{out}" && exit /b 3', str(venv))
    # then:
    assert exit_code == 3
    assert out.read_text().strip() == "yes"


def test_sigint_is_ignored_while_child_runs_and_restored_on_failure():
    # given:
    driver = make_driver()
    previous = signal.getsignal(signal.SIGINT)
    seen = []

    def fake_run(*args, **kwargs):
        seen.append(signal.getsignal(signal.SIGINT))
        raise RuntimeError("boom")

    # when:
    with patch("subprocess.run", side_effect=fake_run):
        try:
            driver.run_shell(False, "echo hi", VENV)
        except RuntimeError:
            pass

    # then: the parent ignores `Ctrl+C` while the child runs (both get it), and the handler is restored:
    assert seen == [signal.SIG_IGN]
    assert signal.getsignal(signal.SIGINT) == previous


@requires_windows
def test_real_cmd_loads_autorun_before_activation(tmp_path):
    import winreg

    # given: `AutoRun` and `activate.bat` both append to the same file:
    out = tmp_path / "order.txt"
    venv = tmp_path / "venv"
    scripts = venv / primer_kernel._ConfConstGeneral.name_venv_bin_dir
    scripts.mkdir(parents=True)
    (scripts / "activate.bat").write_text(f'@echo activate>> "{out}"\r\n')
    key_path = r"Software\Microsoft\Command Processor"
    driver = _ShellDriverCmd(
        shell_abs_path=os.environ["COMSPEC"],
        shell_env_vars=os.environ.copy(),
        cache_dir_abs_path=str(tmp_path / "cache"),
    )

    # when: (`HKCU` value is restored whatever happens)
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
        try:
            previous_value, previous_type = winreg.QueryValueEx(key, "AutoRun")
        except FileNotFoundError:
            previous_value, previous_type = None, None
        try:
            winreg.SetValueEx(key, "AutoRun", 0, winreg.REG_SZ, f'@echo autorun>> "{out}"')
            exit_code = driver.run_shell(False, f'echo command>> "{out}"', str(venv))
        finally:
            if previous_value is None:
                winreg.DeleteValue(key, "AutoRun")
            else:
                winreg.SetValueEx(key, "AutoRun", 0, previous_type, previous_value)

    # then:
    assert exit_code == 0
    assert out.read_text().split() == ["autorun", "activate", "command"]
