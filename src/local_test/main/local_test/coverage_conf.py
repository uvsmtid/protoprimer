"""
Shared coverage settings: the single source of truth is `coveragerc.ini` in the global conf dir of the repo.

FT_47_61_24_68.combined_coverage.md
"""

from __future__ import annotations

import configparser
import pathlib

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
