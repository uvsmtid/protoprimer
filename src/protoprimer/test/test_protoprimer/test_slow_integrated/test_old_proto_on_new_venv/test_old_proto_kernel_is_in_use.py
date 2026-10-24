"""
Guard: the swap is implicit (an autouse fixture in `conftest.py`), so make sure it really happens:
otherwise every test in this dir would pass vacuously with the current `proto_kernel.py`.

FT_78_72_23_04.backward_compatibility.md
"""

import pathlib
import subprocess

from local_contract_compatibility.old_proto_on_new_venv import get_old_proto_kernel_rel_path
from local_test.integrated_helper import create_plain_proto_kernel


def test_plain_proto_kernel_is_the_committed_one_of_commit_name(
    tmp_path: pathlib.Path,
    commit_name: str,
    repo_dir_abs_path: pathlib.Path,
):

    # given:

    committed_content = subprocess.run(
        ["git", "show", f"{commit_name}:{get_old_proto_kernel_rel_path()}"],
        cwd=str(repo_dir_abs_path),
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    # when:

    proto_kernel_abs_path = create_plain_proto_kernel(tmp_path)

    # then:

    assert proto_kernel_abs_path.read_text() == committed_content
