import importlib.util
import json
import pathlib

import pytest

import protoprimer

# FT_03_31_63_70.environment_selection.md:
_selector_file_path = pathlib.Path(protoprimer.__file__).parent.parent.parent.parent.parent / "src" / "proto_code" / "env_selector.py"


def _load_module():
    module_spec = importlib.util.spec_from_file_location("env_selector_copy", _selector_file_path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module


def _select(monkeypatch, github_job, ci=None):
    module = _load_module()
    if github_job is None:
        monkeypatch.delenv("GITHUB_JOB", raising=False)
    else:
        monkeypatch.setenv("GITHUB_JOB", github_job)
    if ci is None:
        monkeypatch.delenv("CI", raising=False)
    else:
        monkeypatch.setenv("CI", ci)
    return module.select_env_dir_rel_path()


@pytest.mark.parametrize(
    "github_job, expected_env_dir",
    [
        ("test_py_min_linux", "dst/test_python_min_linux"),
        ("test_py_med_linux", "dst/test_python_med_linux"),
        ("test_py_max_linux", "dst/test_python_max_linux"),
        ("test_py_med_windows", "dst/test_python_med_windows"),
        # listed jobs which are not `test_py_*`:
        ("verify_contract_compatibility", "dst/test_python_max_linux"),
        ("invoke_condition_scenarios", "dst/test_python_max_linux"),
    ],
)
def test_selects_env_dir_by_github_job(monkeypatch, github_job, expected_env_dir):
    assert _select(monkeypatch, github_job) == expected_env_dir


@pytest.mark.parametrize(
    "github_job",
    [
        # not in GitHub Actions (and no `CI=true`):
        None,
        # other jobs:
        "run_pre_commit",
        "build_doc",
        "test_py_med",
        "test_py_huge_linux",
        "prefix_test_py_med_linux",
    ],
)
def test_none_when_not_matching_github_job(monkeypatch, github_job):
    assert _select(monkeypatch, github_job) is None


@pytest.mark.parametrize(
    "version_info, platform, expected_env_dir",
    [
        ((3, 7, 17), "linux", "dst/test_python_min_linux"),
        ((3, 11, 2), "linux", "dst/test_python_med_linux"),
        ((3, 15, 0), "linux", "dst/test_python_max_linux"),
        ((3, 11, 2), "win32", "dst/test_python_med_windows"),
        ((3, 11, 2), "darwin", "dst/test_python_med_darwin"),
        ((3, 15, 0), "win32", "dst/test_python_max_windows"),
        ((3, 15, 0), "darwin", "dst/test_python_max_darwin"),
        # untested `python` version or platform:
        ((3, 9, 1), "linux", None),
        ((3, 11, 2), "freebsd14", None),
    ],
)
def test_selects_env_dir_by_host(tmp_path, version_info, platform, expected_env_dir):
    # All env dirs exist:
    for env_dir_rel_path in [
        "min_linux",
        "med_linux",
        "max_linux",
        "med_windows",
        "med_darwin",
        "max_windows",
        "max_darwin",
    ]:
        (tmp_path / "dst" / f"test_python_{env_dir_rel_path}").mkdir(parents=True)

    assert _load_module().select_env_dir_rel_path_by_host(version_info, platform, str(tmp_path)) == expected_env_dir


@pytest.mark.parametrize(
    "version_info, platform",
    [
        # a tested cell without the env dir:
        ((3, 7, 17), "win32"),
        ((3, 7, 17), "darwin"),
        ((3, 11, 2), "linux"),
    ],
)
def test_none_when_host_env_dir_is_missing(tmp_path, version_info, platform):
    (tmp_path / "dst").mkdir()

    assert _load_module().select_env_dir_rel_path_by_host(version_info, platform, str(tmp_path)) is None


def test_none_when_host_env_dir_is_a_file(tmp_path):
    (tmp_path / "dst").mkdir()
    (tmp_path / "dst" / "test_python_med_linux").write_text("")

    assert _load_module().select_env_dir_rel_path_by_host((3, 11, 2), "linux", str(tmp_path)) is None


def test_selects_env_dir_by_host_only_with_ci_true(monkeypatch):
    module = _load_module()
    monkeypatch.delenv("GITHUB_JOB", raising=False)
    monkeypatch.setattr(module, "select_env_dir_rel_path_by_host", lambda version_info, platform, ref_root: "dst/by_host")

    monkeypatch.delenv("CI", raising=False)
    assert module.select_env_dir_rel_path() is None

    monkeypatch.setenv("CI", "false")
    assert module.select_env_dir_rel_path() is None

    monkeypatch.setenv("CI", "true")
    assert module.select_env_dir_rel_path() == "dst/by_host"


def test_github_job_wins_over_host(monkeypatch):
    # `CI=true` is always set in GitHub Actions: non-test jobs must not fall back to the host:
    assert _select(monkeypatch, "run_pre_commit", ci="true") is None
    assert _select(monkeypatch, "test_py_min_linux", ci="true") == "dst/test_python_min_linux"
    assert _select(monkeypatch, "invoke_condition_scenarios", ci="true") == "dst/test_python_max_linux"


@pytest.mark.parametrize("github_job", ["run_pre_commit", "build_doc", "report_coverage"])
def test_lint_doc_cover_jobs_select_nothing(monkeypatch, github_job):
    assert _select(monkeypatch, github_job, ci="true") is None


def test_gconf_points_to_the_selector_file():
    gconf_file_path = _selector_file_path.parent.parent.parent / "gconf" / "proto_kernel.json"
    env_selector_file_rel_path = json.loads(gconf_file_path.read_text())["env_selector_file_rel_path"]

    assert (gconf_file_path.parent.parent / env_selector_file_rel_path).samefile(_selector_file_path)
    assert callable(_load_module().select_env_dir_rel_path)


def test_host_selection_uses_ref_root_of_the_selector_file(monkeypatch):
    module = _load_module()
    monkeypatch.delenv("GITHUB_JOB", raising=False)
    monkeypatch.setenv("CI", "true")
    seen_ref_roots = []
    monkeypatch.setattr(module, "select_env_dir_rel_path_by_host", lambda version_info, platform, ref_root: seen_ref_roots.append(ref_root))

    module.select_env_dir_rel_path()

    assert seen_ref_roots == [str(_selector_file_path.parent.parent.parent)]
