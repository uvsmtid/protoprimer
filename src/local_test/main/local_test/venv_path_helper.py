import os

from protoprimer.primer_kernel import (
    _ConfConstEnv,
    _ConfConstGeneral,
)

# TODO: TODO_50_98_96_87.support_windows.md: "Test suite hardcodes POSIX path separators ..." (Option B):
# expected paths are built from the same constants as the production code (`bin/python` vs `Scripts\python.exe`).


def compose_venv_python_abs_path(venv_dir_abs_path: str) -> str:
    return os.path.join(venv_dir_abs_path, _ConfConstGeneral.file_rel_path_venv_python)


def compose_uv_exec_abs_path(cache_dir_abs_path: str) -> str:
    return os.path.join(
        cache_dir_abs_path,
        _ConfConstEnv.default_dir_rel_path_venv,
        "uv.venv",
        _ConfConstGeneral.file_rel_path_venv_uv,
    )
