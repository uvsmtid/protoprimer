import pytest

from local_test.case_condition import git_is_not_available
from local_test.entry_script_regen_helper import (
    assert_wrap_regenerates_with_no_git_diff,
    get_repo_root_abs_path,
)
from local_test.name_assertion import (
    assert_test_func_name_embeds_str,
    assert_test_module_name_embeds_str,
)
from protoprimer.primer_kernel import ExecOperation

repo_root_abs_path = get_repo_root_abs_path()
proto_kernel_abs_path = repo_root_abs_path / "src" / "proto_code" / "proto_kernel.py"


def test_relationship():
    assert_test_module_name_embeds_str(ExecOperation.op_wrap.value)


@pytest.mark.skipif(git_is_not_available(), reason="git command is not available")
def test_wrap_regenerates_prime():
    """
    Regenerates `./prime` via `ExecOperation.op_wrap`
    and asserts the result is byte-for-byte identical to what is committed.
    """

    assert_test_func_name_embeds_str(ExecOperation.op_wrap.value)

    entry_script_abs_path = repo_root_abs_path / "prime"

    assert_wrap_regenerates_with_no_git_diff(
        repo_root_abs_path,
        proto_kernel_abs_path,
        entry_script_abs_path,
    )
