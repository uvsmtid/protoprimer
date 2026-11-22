import os
from local_test import container_hook_installer
from local_test.container_hook_installer import (
    find_uv_stdlib_dir_paths,
    get_uv_python_dir_path,
    install_hook,
)
from local_test.name_assertion import assert_test_module_name_embeds_another_module_name


def test_relationship():
    assert_test_module_name_embeds_another_module_name(container_hook_installer.__name__)


def test_install_hook_copies_once(tmp_path):

    # given:

    hook_file = tmp_path / "hook.py"
    hook_file.write_text("new")
    stdlib_dir = tmp_path / "stdlib"
    stdlib_dir.mkdir()

    # when:

    install_hook(str(hook_file), str(stdlib_dir))

    # then:

    assert (stdlib_dir / "sitecustomize.py").read_text() == "new"

    # when: an existing `sitecustomize.py` is not overwritten
    (stdlib_dir / "sitecustomize.py").write_text("existing")
    install_hook(str(hook_file), str(stdlib_dir))

    # then:

    assert (stdlib_dir / "sitecustomize.py").read_text() == "existing"


def test_get_uv_python_dir_path_priority(monkeypatch):

    monkeypatch.delenv("UV_PYTHON_INSTALL_DIR", raising=False)
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    assert get_uv_python_dir_path().endswith("/.local/share/uv/python")

    monkeypatch.setenv("XDG_DATA_HOME", "/xdg")
    assert get_uv_python_dir_path() == "/xdg/uv/python"

    monkeypatch.setenv("UV_PYTHON_INSTALL_DIR", "/uv_dir")
    assert get_uv_python_dir_path() == "/uv_dir"


def test_get_uv_python_dir_path_windows(monkeypatch):

    monkeypatch.delenv("UV_PYTHON_INSTALL_DIR", raising=False)
    monkeypatch.setattr(os, "name", "nt")
    monkeypatch.setenv("APPDATA", "appdata_dir")

    assert get_uv_python_dir_path() == os.path.join("appdata_dir", "uv", "data", "python")


def test_find_uv_stdlib_dir_paths_windows_layout(tmp_path, monkeypatch):

    monkeypatch.setenv("UV_PYTHON_INSTALL_DIR", str(tmp_path))
    stdlib_dir = tmp_path / "cpython-3.15.2-windows-x86_64-none" / "Lib"
    stdlib_dir.mkdir(parents=True)

    assert find_uv_stdlib_dir_paths() == [str(stdlib_dir)]


def test_find_uv_stdlib_dir_paths(tmp_path, monkeypatch):

    # given:

    monkeypatch.setenv("UV_PYTHON_INSTALL_DIR", str(tmp_path))
    stdlib_dir = tmp_path / "cpython-3.15.2-linux-x86_64-gnu" / "lib" / "python3.15"
    stdlib_dir.mkdir(parents=True)
    (tmp_path / "cpython-3.15.2-linux-x86_64-gnu" / "lib" / "other").mkdir()

    # then:

    assert find_uv_stdlib_dir_paths() == [str(stdlib_dir)]
