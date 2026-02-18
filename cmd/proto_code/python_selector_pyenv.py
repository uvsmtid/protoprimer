from __future__ import annotations

import os
import subprocess


def select_python_file_abs_path(required_version: tuple[int, int, int]) -> str | None:
    """
    Example to install `required_version` via `pyenv`.

    Implements `SelectorFunc.select_python_file_abs_path` from `protoprimer.primer_kernel`.
    """

    # Convert (3, 10, 12) to "3.10.12":
    python_version = ".".join(map(str, required_version))

    try:
        # If it exists, `pyenv` exits immediately with code 0:
        subprocess.check_call(
            [
                "pyenv",
                "install",
                "--skip-existing",
                python_version,
            ],
        )

        # Get the prefix path for that specific version:
        prefix_abs_path = subprocess.check_output(
            args=[
                "pyenv",
                "prefix",
                python_version,
            ],
            text=True,
        ).strip()

        return os.path.join(prefix_abs_path, "bin", "python")

    except subprocess.CalledProcessError:
        # if `pyenv` is missing or the installation fails:
        return None
    except FileNotFoundError:
        # if the `pyenv` command is not found in `PATH`:
        return None
