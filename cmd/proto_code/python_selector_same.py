from __future__ import annotations

import os
import shutil
import sys


def select_python_file_abs_path(required_version: tuple[int, int, int]) -> str | None:
    """
    Implements `SelectorFunc.select_python_file_abs_path` from `protoprimer.primer_kernel`.
    """

    # NOTE: This trivially re-evaluates the basename of the current `python` via `PATH` env var
    #       (which may or may not be the current executable):
    return shutil.which(os.path.basename(sys.executable))
