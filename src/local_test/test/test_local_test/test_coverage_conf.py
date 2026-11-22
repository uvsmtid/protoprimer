import os
import subprocess
import sys

import coverage
import pytest

from local_test import coverage_conf
from local_test.coverage_conf import (
    get_coverage_hook_script,
    get_rcfile_abs_path,
    read_source_dir_rel_paths,
)
from local_test.invoke_condition_helper import get_repo_root_abs_path
from local_test.name_assertion import assert_test_module_name_embeds_another_module_name


def test_relationship():
    assert_test_module_name_embeds_another_module_name(coverage_conf.__name__)


def test_read_source_dir_rel_paths(tmp_path):

    # given:

    rcfile_abs_path = get_rcfile_abs_path(tmp_path)
    rcfile_abs_path.parent.mkdir()
    rcfile_abs_path.write_text("[run]\n# comment\nsource =\n    src/a/main/\n    src/b/main\n\nbranch = true\n")

    # then:

    assert read_source_dir_rel_paths(tmp_path) == ["src/a/main", "src/b/main"]


def test_read_source_dir_rel_paths_fails_loudly_without_rcfile(tmp_path):

    with pytest.raises(FileNotFoundError):
        read_source_dir_rel_paths(tmp_path)


def test_read_source_dir_rel_paths_of_this_repo():

    # when:

    source_dir_rel_paths = read_source_dir_rel_paths(get_repo_root_abs_path())

    # then: the measured code exists
    assert source_dir_rel_paths
    for source_dir_rel_path in source_dir_rel_paths:
        assert (get_repo_root_abs_path() / source_dir_rel_path).is_dir()


def make_hook_run(tmp_path, monkeypatch):
    """
    Installs the hook (as `sitecustomize.py` on `PYTHONPATH`) and returns the source dir and the data file base.
    """

    source_dir = tmp_path / "source"
    source_dir.mkdir()
    hook_dir = tmp_path / "hook"
    hook_dir.mkdir()
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    rcfile = tmp_path / "rc.ini"
    rcfile.write_text("[run]\nparallel = true\n")
    data_file = data_dir / ".coverage"
    (hook_dir / "sitecustomize.py").write_text(
        get_coverage_hook_script(
            config_file=str(rcfile),
            source_dir_paths=[str(source_dir)],
            data_file=str(data_file),
        )
    )
    monkeypatch.setenv("PYTHONPATH", os.pathsep.join([str(hook_dir), str(source_dir)]))
    return source_dir, data_file


def executed_file_names(data_file):
    """
    Names of the files with executed lines (`source` also lists never imported files: they have no lines).
    """

    cov = coverage.Coverage(data_file=str(data_file), config_file=False)
    cov.combine(data_paths=[str(data_file.parent)], keep=True)
    data = cov.get_data()
    return sorted(os.path.basename(measured_file) for measured_file in data.measured_files() if data.lines(measured_file))


def test_hook_script_is_valid_python():
    compile(get_coverage_hook_script("/rc.ini", ["/src"], "/data/.coverage"), "<hook>", "exec")
    compile(get_coverage_hook_script("/rc.ini", ["/src"]), "<hook>", "exec")


def test_hook_measures_a_process(tmp_path, monkeypatch):

    # given:

    source_dir, data_file = make_hook_run(tmp_path, monkeypatch)
    (source_dir / "mod_a.py").write_text("def f():\n    return 1\n")

    # when:

    subprocess.run([sys.executable, "-c", "import mod_a; mod_a.f()"], check=True)

    # then:

    assert executed_file_names(data_file) == ["mod_a.py"]


def test_hook_saves_data_before_exec(tmp_path, monkeypatch):

    # given: the first process is replaced by the second one (`exec` runs no exit handlers)

    source_dir, data_file = make_hook_run(tmp_path, monkeypatch)
    (source_dir / "mod_a.py").write_text("def f():\n    return 1\n")
    (source_dir / "mod_b.py").write_text("def g():\n    return 2\n")

    # when:

    subprocess.run(
        [
            sys.executable,
            "-c",
            "import mod_a, os, sys\nmod_a.f()\nos.execv(sys.executable, [sys.executable, '-c', 'import mod_b; mod_b.g()'])",
        ],
        check=True,
    )

    # then: the data of the replaced process is not lost

    assert executed_file_names(data_file) == ["mod_a.py", "mod_b.py"]


def test_hook_ignores_code_outside_of_source(tmp_path, monkeypatch):

    # given:

    source_dir, data_file = make_hook_run(tmp_path, monkeypatch)
    other_dir = tmp_path / "other"
    other_dir.mkdir()
    (other_dir / "mod_other.py").write_text("def f():\n    return 1\n")
    monkeypatch.setenv("PYTHONPATH", os.pathsep.join([os.environ["PYTHONPATH"], str(other_dir)]))

    # when:

    subprocess.run([sys.executable, "-c", "import mod_other; mod_other.f()"], check=True)

    # then:

    assert executed_file_names(data_file) == []
