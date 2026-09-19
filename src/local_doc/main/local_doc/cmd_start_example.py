# FT_11_27_29_83.exec_operation.md: see also `cmd_start_app_example.py`
from __future__ import annotations

import sys


def custom_start_main_checks_clean_argv():
    """
    For `ExecOperation.op_start`: `sys.argv` must not leak the `start`/`main_func` CLI args
    (as if this function were started via a dedicated `entry_script` instead).
    """
    assert sys.argv == sys.argv[:1], f"sys.argv leaked extra args: {sys.argv}"
    print("Hello, world!")


if __name__ == "__main__":
    custom_start_main_checks_clean_argv()
