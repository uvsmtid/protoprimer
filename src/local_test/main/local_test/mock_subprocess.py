import os
import sys


def mock_shutil_which_python(cmd, mode=os.F_OK | os.X_OK, path=None):
    """
    Mocks `shutil.which` output used for `EnvState.state_required_python_file_abs_path_inited`.
    """

    return f"/path/to/fake/bin/{cmd}"


def mock_get_python_version_by_current(state_required_python_file_abs_path_inited: str):
    """
    Mocks output of `protoprimer.primer_kernel:get_python_version`.
    """

    return sys.version_info[:3]
