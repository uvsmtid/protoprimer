import os
from unittest.mock import patch


def get_tmp_dir_abs_path(
    repo_dir_abs_path: str,
) -> str:
    """
    The `tmp` dir from the `protoprimer` config of the repo (fails if the config is not available).
    """
    from protoprimer.primer_kernel import _ConfLeap, _EnvState, get_config

    proto_kernel_abs_path = os.path.join(repo_dir_abs_path, "src", "proto_code", "proto_kernel.py")
    original_cwd = os.getcwd()
    os.chdir(repo_dir_abs_path)
    try:
        # TODO: TODO_71_33_38_11.override_proto_kernel_abs_path_in_conf_getter.md:
        # `get_config` needs `proto_kernel_abs_path` which is not set outside of an entry script:
        with patch("protoprimer.primer_kernel.get_proto_kernel_abs_path", return_value=proto_kernel_abs_path):
            return get_config(_ConfLeap.leap_derived)[_EnvState.state_local_tmp_dir_abs_path_inited.name]
    finally:
        os.chdir(original_cwd)
