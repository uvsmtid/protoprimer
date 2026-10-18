import os
from unittest.mock import patch


def _get_tmp_dir_abs_path():
    """
    The `tmp` dir from the `protoprimer` config (`None` if the config is not available).
    """
    try:
        from protoprimer.primer_kernel import ConfLeap, EnvState, get_config

        ref_root_abs_path = os.path.dirname(os.path.abspath(__file__))
        proto_kernel_abs_path = os.path.join(ref_root_abs_path, "src", "proto_code", "proto_kernel.py")
        original_cwd = os.getcwd()
        os.chdir(ref_root_abs_path)
        try:
            # `get_config` needs `proto_kernel_abs_path` which is not set outside of an entry script:
            with patch("protoprimer.primer_kernel.get_proto_kernel_abs_path", return_value=proto_kernel_abs_path):
                return get_config(ConfLeap.leap_derived)[EnvState.state_local_tmp_dir_abs_path_inited.name]
        finally:
            os.chdir(original_cwd)
    except Exception:
        return None


# Do not collect `git worktree`-s of baseline commits (see `local_contract_compatibility`):
_tmp_dir_abs_path = _get_tmp_dir_abs_path()
collect_ignore = [] if _tmp_dir_abs_path is None else [_tmp_dir_abs_path]
