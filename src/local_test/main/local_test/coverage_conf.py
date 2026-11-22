"""
Shared coverage settings: the single source of truth is `coveragerc.ini` in the global conf dir of the repo.

FT_47_61_24_68.combined_coverage.md
"""

from __future__ import annotations

import configparser
import json
import pathlib
from typing import Optional

from protoprimer.primer_kernel import _ConfDst

# Set to a dir to collect coverage of the code run in other processes or places (opt-in):
coverage_dir_env_var = "PROTOPRIMER_COVERAGE_DIR"

rcfile_basename = "coveragerc.ini"


def get_rcfile_abs_path(
    repo_dir_abs_path: pathlib.Path,
) -> pathlib.Path:
    return repo_dir_abs_path / _ConfDst.dst_global.value / rcfile_basename


def read_source_dir_rel_paths(
    repo_dir_abs_path: pathlib.Path,
) -> list[str]:
    """
    The code which is measured: `[run] source` of the `rcfile` (relative to the repo root).

    They are relative to the current dir `coverage` is run from: callers anchor them where the code is
    (for example, `cwd` is not the repo root for old tests, and it differs per process in containers).
    """

    rcfile_abs_path = get_rcfile_abs_path(repo_dir_abs_path)
    if not rcfile_abs_path.is_file():
        raise FileNotFoundError(f"[{rcfile_abs_path}] does not exist")
    config_parser = configparser.ConfigParser(interpolation=None)
    config_parser.read(str(rcfile_abs_path))
    return [line.strip().rstrip("/") for line in config_parser.get("run", "source").splitlines() if line.strip()]


def get_coverage_hook_script(
    config_file: str,
    source_dir_paths: list[str],
    data_file: Optional[str] = None,
) -> str:
    """
    The text of `sitecustomize.py` which starts `coverage` in every `python` process (it never fails or prints).

    It must be installed where isolated `-I` mode finds it (the stdlib dir): `PYTHONPATH` is ignored there.
    The hook runs under any `python` (even min): `coverage` is imported when it is available there.

    Paths are absolute: the current dir differs per process, but relative paths of the config are resolved against it.
    `data_file` is `COVERAGE_FILE` env var when not set (the data of every process adds its own suffix: `parallel`).

    `os.exec*` replaces the process without running exit handlers: the data is saved right before it
    (otherwise, the data of every process which is followed by another one in a chain would be lost).
    """

    data_file_line = f"        data_file={json.dumps(data_file)},\n" if data_file else ""
    return f"""
try:
    import os
    import warnings
    import coverage
    from coverage.exceptions import CoverageWarning
    warnings.simplefilter("ignore", CoverageWarning)
    _cov = coverage.Coverage(
        config_file={json.dumps(config_file)},
        source={json.dumps(source_dir_paths)},
{data_file_line}        messages=False,
        auto_data=True,
    )
    _cov.start()

    def _save_before_exec(name):
        original = getattr(os, name)

        def wrapper(*args, **kwargs):
            try:
                _cov.stop()
                _cov.save()
            except Exception:
                pass
            try:
                return original(*args, **kwargs)
            except BaseException:
                _cov.start()
                raise

        setattr(os, name, wrapper)

    for _name in ("execv", "execve"):
        _save_before_exec(_name)
except Exception:
    pass
"""
