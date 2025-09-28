import pathlib
import subprocess

from local_test.integrated_helper import (
    create_plain_proto_code,
    switch_to_ref_root_abs_path,
)


def test_primer_kernel_invalid_args_fails(
    tmp_path: pathlib.Path,
):
    # given:

    ref_root_abs_path = switch_to_ref_root_abs_path(tmp_path)

    # ===

    create_plain_proto_code(ref_root_abs_path / "proto_code")

    # ===

    command_args = [
        "./proto_code/proto_kernel.py",
        "--invalid-arg",
        "some_value",
    ]

    # when:

    sub_proc = subprocess.run(
        command_args,
        capture_output=True,
        text=True,
        check=False,  # Do not raise an exception for non-zero exit codes
    )

    # then:

    assert sub_proc.returncode != 0
    assert "error" in sub_proc.stderr.lower() or "usage" in sub_proc.stderr.lower()
