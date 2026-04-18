import re
import subprocess
from pathlib import Path

from local_test.integrated_helper import (
    create_max_layout,
)
from local_test.name_assertion import (
    assert_test_module_name_embeds_str,
)
from protoprimer.primer_kernel import (
    ConfConstClient,
    ConfField,
    read_json_file,
    SyntaxArg,
    write_json_file,
)


def test_relationship():
    assert_test_module_name_embeds_str("subprocess_error")


def test_subprocess_error(tmp_path: Path):
    """
    Ensure protoprimer fails correctly when a subprocess (e.g. `pip`) returns a non-zero exit code.

    It uses `create_max_layout` (see FT_59_95_81_63.env_layout.md).
    """

    # given:

    (
        proto_kernel_abs_path,
        ref_root_abs_path,
        project_dir_abs_path,
    ) = create_max_layout(tmp_path)

    # Misconfigure the env config file to cause a failure during `pip install`:
    conf_env_dir_abs_path = ref_root_abs_path / ConfConstClient.default_default_env_dir_rel_path
    conf_env_file_abs_path = conf_env_dir_abs_path / ConfConstClient.default_file_basename_leap_env

    env_conf_data = read_json_file(str(conf_env_file_abs_path))

    # Replace `field_extra_command_args` with `["--cause_failure"]`:
    for spec in env_conf_data[ConfField.field_install_specs.value]:
        # 'whatever_group_main' is the group name used in `create_conf_env_file` (integrated_helper.py):
        if "whatever_group_main" in spec:
            spec["whatever_group_main"][ConfField.field_extra_command_args.value] = ["--cause_failure"]

    write_json_file(str(conf_env_file_abs_path), env_conf_data)

    # when:

    result = subprocess.run(
        [
            str(proto_kernel_abs_path),
            SyntaxArg.arg_v,
            SyntaxArg.arg_v,
        ],
        capture_output=True,
        text=True,
    )

    # then:

    assert result.returncode == 1

    assert "RuntimeError" in result.stderr
    # The message should contain the command line which failed:
    assert "--cause_failure" in result.stderr

    # "which should also tell some other error code (not necessarily 1) - assert it"
    match = re.search(r"command failed with `exit_code` \[(\d+)\]", result.stderr)
    assert match is not None
    orig_exit_code = int(match.group(1))

    # `pip` (or `uv`) should fail with non-zero exit code for invalid args.
    # It might be 2 or 1, but we should assert it is captured.
    assert orig_exit_code != 0
