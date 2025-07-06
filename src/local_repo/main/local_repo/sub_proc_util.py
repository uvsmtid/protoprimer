import subprocess


def get_command_code(
    command_line: str,
    fail_on_error=True,
) -> int:
    sub_proc = subprocess.run(
        command_line,
        check=fail_on_error,
        capture_output=False,
        text=True,
        shell=True,
    )
    return sub_proc.returncode


def get_command_output(
    command_line: str,
    fail_on_error=True,
) -> str:
    sub_proc = subprocess.run(
        command_line,
        check=fail_on_error,
        capture_output=True,
        text=True,
        shell=True,
    )
    return sub_proc.stdout.strip()
