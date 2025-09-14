import pathlib
import subprocess

from test_protoprimer.test_integrated.integrated_helper import (
    switch_to_test_dir_with_plain_proto_code,
)


def test_primer_kernel_invalid_args_fails(
    tmp_path: pathlib.Path,
):
    # given:

    switch_to_test_dir_with_plain_proto_code(tmp_path)

    command_args = [
        "./primer_kernel.py",
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
