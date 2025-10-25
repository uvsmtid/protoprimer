import os
import pathlib

from local_repo.sub_proc_util import (
    get_command_output,
)
from local_test.integrated_helper import (
    create_plain_proto_code,
    switch_to_ref_root_abs_path,
)


def test_help(tmp_path: pathlib.Path):

    # given:

    ref_root_abs_path = switch_to_ref_root_abs_path(tmp_path)

    # ===

    create_plain_proto_code(ref_root_abs_path / "proto_code")

    # when:

    help_output = get_command_output("./proto_code/proto_kernel.py --help")

    # then:

    assert "usage: proto_kernel.py" in help_output
