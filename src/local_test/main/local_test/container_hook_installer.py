"""
Runs INSIDE a container (by the `python3` of the image): installs the coverage hook as `sitecustomize.py`
into the stdlib dirs of `python`-s (shared by their `venv`-s): `PYTHONPATH` is ignored by isolated `-I` mode.

It is copied into the container by `invoke_condition_helper.ContainerSession` (it is not imported from there):
it uses the standard library only and must stay compatible with the min `python`.

FT_47_61_24_68.combined_coverage.md

Usage:
    python3 container_hook_installer.py <hook_file> once   - install into the `python` which runs this script
    python3 container_hook_installer.py <hook_file> watch  - keep installing into `python`-s downloaded by `uv` (until killed)
"""

import glob
import os
import shutil
import sys
import sysconfig
import time


def install_hook(
    hook_file_path: str,
    stdlib_dir_path: str,
) -> None:
    hook_dst_path = os.path.join(stdlib_dir_path, "sitecustomize.py")
    if not os.path.exists(hook_dst_path):
        shutil.copy(hook_file_path, hook_dst_path)


def get_uv_python_dir_path() -> str:
    """
    Where `uv` keeps the `python`-s it downloads (see `uv` docs: `UV_PYTHON_INSTALL_DIR`, `XDG_DATA_HOME`, `APPDATA`).
    """

    if os.environ.get("UV_PYTHON_INSTALL_DIR"):
        return os.environ["UV_PYTHON_INSTALL_DIR"]
    if os.name == "nt":
        return os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~\\AppData\\Roaming"), "uv", "data", "python")
    data_dir_path = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    return os.path.join(data_dir_path, "uv", "python")


def find_uv_stdlib_dir_paths() -> list:
    uv_python_dir_path = get_uv_python_dir_path()
    # Posix: `<uv python dir>/<python build>/lib/python3.X`; Windows: `<uv python dir>/<python build>/Lib`:
    return glob.glob(os.path.join(uv_python_dir_path, "*", "lib", "python3.*")) + glob.glob(os.path.join(uv_python_dir_path, "*", "Lib"))


def main() -> None:
    hook_file_path = sys.argv[1]
    mode = sys.argv[2]

    if mode == "once":
        install_hook(hook_file_path, sysconfig.get_paths()["stdlib"])
    elif mode == "watch":
        # `uv` downloads (and `venv` is based on) its own `python` during a scenario: copy the hook right when it appears:
        while True:
            for stdlib_dir_path in find_uv_stdlib_dir_paths():
                try:
                    install_hook(hook_file_path, stdlib_dir_path)
                except OSError:
                    # The dir may be being created: try again on the next iteration:
                    pass
            time.sleep(0.1)
    else:
        raise ValueError("unknown mode [{}]".format(mode))


if __name__ == "__main__":
    main()
