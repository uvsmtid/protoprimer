"""
Shared coverage settings: the single source of truth is `coveragerc.ini` in the global conf dir of the repo.

FT_47_61_24_68.combined_coverage.md
"""

from __future__ import annotations

import configparser
import contextlib
import glob
import json
import logging
import os
import pathlib
import subprocess
import sys
import sysconfig
import threading
from typing import Iterator, Optional, Sequence

from local_test.container_hook_installer import find_uv_stdlib_dir_paths
from protoprimer.primer_kernel import _ConfDst

logger = logging.getLogger()

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


def get_stdlib_dir_path(
    python_abs_path: str,
) -> pathlib.Path:
    # A `venv` shares the stdlib dir of its base `python`:
    if os.path.abspath(python_abs_path) == os.path.abspath(sys.executable):
        return pathlib.Path(sysconfig.get_paths()["stdlib"])
    return pathlib.Path(
        subprocess.run(
            [python_abs_path, "-c", "import sysconfig; print(sysconfig.get_paths()['stdlib'])"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    )


def _install_hook_file(
    hook_text: str,
    stdlib_dir_path: pathlib.Path,
) -> bool:
    """
    Never overwrites an existing `sitecustomize.py`.
    """

    hook_file_path = stdlib_dir_path / "sitecustomize.py"
    if hook_file_path.exists():
        logger.warning(f"[{hook_file_path}] already exists: subprocesses of its `python` are not measured")
        return False
    try:
        hook_file_path.write_text(hook_text)
    except OSError as os_error:
        logger.warning(f"cannot write [{hook_file_path}] ({os_error}): subprocesses of its `python` are not measured")
        return False
    return True


def _remove_hook_file(
    stdlib_dir_path: pathlib.Path,
) -> None:
    with contextlib.suppress(FileNotFoundError):
        (stdlib_dir_path / "sitecustomize.py").unlink()
    for pyc_file_path in glob.glob(str(stdlib_dir_path / "__pycache__" / "sitecustomize.*.pyc")):
        os.remove(pyc_file_path)


@contextlib.contextmanager
def installed_coverage_hook(
    repo_dir_abs_path: pathlib.Path,
    python_abs_paths: Optional[Sequence[str]] = None,
) -> Iterator[bool]:
    """
    Installs the coverage hook as `sitecustomize.py` into the stdlib dirs of `python_abs_paths`
    (the current `python` by default) and removes it on exit:
    it starts `coverage` in every `python` process - `PYTHONPATH` is ignored by isolated `-I` mode.

    `python`-s which `uv` downloads while the context is active also get the hook (see `container_hook_installer`).

    Yields `True` if installed into at least one of `python_abs_paths`.
    """

    hook_text = get_coverage_hook_script(
        config_file=str(get_rcfile_abs_path(repo_dir_abs_path)),
        source_dir_paths=[str(repo_dir_abs_path / source_dir_rel_path) for source_dir_rel_path in read_source_dir_rel_paths(repo_dir_abs_path)],
    )

    installed_dir_paths: list[pathlib.Path] = []
    stdlib_dir_paths = {get_stdlib_dir_path(python_abs_path) for python_abs_path in (python_abs_paths or [sys.executable])}
    for stdlib_dir_path in stdlib_dir_paths:
        if _install_hook_file(hook_text, stdlib_dir_path):
            installed_dir_paths.append(stdlib_dir_path)

    # Only the dirs installed by this watcher (the dirs of `python_abs_paths` are handled above):
    stop_event = threading.Event()
    watched_dir_paths: list[pathlib.Path] = []

    def watch_uv_pythons() -> None:
        while not stop_event.is_set():
            for uv_stdlib_dir in find_uv_stdlib_dir_paths():
                uv_stdlib_dir_path = pathlib.Path(uv_stdlib_dir)
                if uv_stdlib_dir_path in stdlib_dir_paths or uv_stdlib_dir_path in watched_dir_paths or (uv_stdlib_dir_path / "sitecustomize.py").exists():
                    continue
                try:
                    (uv_stdlib_dir_path / "sitecustomize.py").write_text(hook_text)
                    watched_dir_paths.append(uv_stdlib_dir_path)
                except OSError:
                    # The dir may be being created: try again on the next iteration:
                    pass
            stop_event.wait(0.1)

    watcher_thread = threading.Thread(target=watch_uv_pythons, daemon=True)
    watcher_thread.start()
    try:
        yield bool(installed_dir_paths)
    finally:
        stop_event.set()
        watcher_thread.join()
        for installed_dir_path in installed_dir_paths + watched_dir_paths:
            _remove_hook_file(installed_dir_path)
