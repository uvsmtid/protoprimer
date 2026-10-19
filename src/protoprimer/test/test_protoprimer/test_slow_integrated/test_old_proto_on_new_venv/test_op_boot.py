import pathlib

from local_contract_compatibility.old_proto_on_new_venv import extract_old_proto_kernel
from local_test.fat_mocked_helper import run_primer_main
from local_test.integrated_helper import create_max_leaps_shape
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    ExecOperation,
    SyntaxArg,
    TopDir,
)


def test_relationship():
    assert_test_module_name_embeds_str(ExecOperation.op_boot.value)


def test_old_proto_kernel_op_boot(
    tmp_path: pathlib.Path,
    commit_name: str,
    repo_dir_abs_path: pathlib.Path,
):
    """
    `commit_name`'s committed `proto_kernel.py` must still be able to boot into the
    current `protoprimer` (new `venv`): see `old_proto_on_new_venv` in "Modes (ids)".
    """

    # given:

    (
        proto_kernel_abs_path,
        ref_root_abs_path,
        project_dir_abs_path,
    ) = create_max_leaps_shape(tmp_path)

    # Replace the plain test copy with the actual historical `proto_kernel.py` of `commit_name`
    # (it keeps its executable bit; only the file content changes):
    extract_old_proto_kernel(
        repo_dir_abs_path,
        commit_name,
        proto_kernel_abs_path,
    )

    # when:

    run_primer_main(
        [
            str(proto_kernel_abs_path),
            SyntaxArg.arg_v,
            SyntaxArg.arg_v,
        ]
    )

    # then:

    assert (ref_root_abs_path / TopDir.dir_venv.value).exists()
