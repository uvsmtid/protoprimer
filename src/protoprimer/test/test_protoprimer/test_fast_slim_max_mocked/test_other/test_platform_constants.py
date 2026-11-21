from local_test.case_condition import (
    requires_posix,
    requires_windows,
)
from protoprimer.primer_kernel import _ConfConstGeneral

# Constants are evaluated once on import (they cannot be flipped by mocking `sys.platform`):
# these tests verify the platform they run on.
# The expected values are hard-coded (not computed via the same expressions as in `primer_kernel`).


@requires_posix
def test_platform_constants_posix():
    assert _ConfConstGeneral.is_os_windows is False
    assert _ConfConstGeneral.name_venv_bin_dir == "bin"
    assert _ConfConstGeneral.file_rel_path_venv_bin == "bin"
    assert _ConfConstGeneral.file_rel_path_venv_python == "bin/python"
    assert _ConfConstGeneral.file_rel_path_venv_activate == "bin/activate"
    assert _ConfConstGeneral.file_rel_path_venv_uv == "bin/uv"
    assert _ConfConstGeneral.file_rel_path_base_python_bin == "bin"


@requires_windows
def test_platform_constants_windows():
    assert _ConfConstGeneral.is_os_windows is True
    assert _ConfConstGeneral.name_venv_bin_dir == "Scripts"
    assert _ConfConstGeneral.file_rel_path_venv_bin == "Scripts"
    assert _ConfConstGeneral.file_rel_path_venv_python == "Scripts\\python.exe"
    assert _ConfConstGeneral.file_rel_path_venv_activate == "Scripts\\activate.bat"
    assert _ConfConstGeneral.file_rel_path_venv_uv == "Scripts\\uv.exe"
    assert _ConfConstGeneral.file_rel_path_base_python_bin == ""
