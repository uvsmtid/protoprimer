import os
import subprocess
from typing import Dict, Union, List


def get_command_code(
    command_line: str,
    fail_on_error=True,
    env_vars: Union[Dict[str, str], None] = None,
) -> int:
    env = os.environ.copy()
    if env_vars:
        env.update(env_vars)
    sub_proc = subprocess.run(
        command_line,
        check=fail_on_error,
        capture_output=False,
        text=True,
        shell=True,
        env=env,
    )
    return sub_proc.returncode


def get_command_output(
    command_line: str,
    fail_on_error=True,
    env_vars: Union[Dict[str, str], None] = None,
) -> str:
    env = os.environ.copy()
    if env_vars:
        env.update(env_vars)
    sub_proc = subprocess.run(
        command_line,
        check=fail_on_error,
        capture_output=True,
        text=True,
        shell=True,
        env=env,
    )
    return sub_proc.stdout.strip()
