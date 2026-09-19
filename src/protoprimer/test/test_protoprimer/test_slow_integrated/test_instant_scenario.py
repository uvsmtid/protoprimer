"""
FT_21_75_54_18.instant_scenario.md
"""

import os
import subprocess
from pathlib import Path

from local_test.case_condition import requires_max_python
from local_test.fat_mocked_helper import (
    assert_editable_install,
    run_primer_main,
)
from local_test.integrated_helper import (
    create_min_leaps_shape,
    test_package_name,
)
from protoprimer.primer_kernel import (
    ConfDst,
    ExecOperation,
    SyntaxArg,
    TopDir,
)


# FT_84_11_73_28.supported_python_versions.md:
# NOTE: This test fails with `python` 3.7 because `pip` treats dependencies like
#       `"protoprimer @ file://{protoprimer_project_dir}"` as "Direct Reference" and
#       installs them in "regular" mode (copying files to site-packages) from `pypi.org`
#       rather than "editable" mode from the source.
#       This makes the installed code older than current sources.
#       If there were no changes, the test passes. It may fail otherwise.
#       This is not a problem with any other project except `protoprimer` itself
#       (because any other project does not use "editable" mode for `protoprimer`).
@requires_max_python
def test_instant_scenario(tmp_path: Path):
    """
    This test runs `proto_code` directly (rather than importing it via `entry_script`).

    It uses `create_min_leaps_shape` (see FT_59_95_81_63.tree_shape.md).
    """

    # given:

    (
        proto_kernel_abs_path,
        ref_root_abs_path,
        project_dir_abs_path,
    ) = create_min_leaps_shape(tmp_path)

    # when:

    run_primer_main(
        [
            str(proto_kernel_abs_path),
            SyntaxArg.arg_v,
            SyntaxArg.arg_v,
        ]
    )

    # then:

    assert_editable_install(project_dir_abs_path, test_package_name)

    gconf_dir = ref_root_abs_path / ConfDst.dst_global.value
    lconf_dir = ref_root_abs_path / ConfDst.dst_local.value

    assert not os.path.exists(gconf_dir)
    assert not os.path.exists(lconf_dir)

    assert os.path.exists(ref_root_abs_path / TopDir.dir_log.value)
    assert os.path.exists(ref_root_abs_path / TopDir.dir_venv.value)

    # when:
    # re-run in eval command - it should not fail:

    run_primer_main(
        [
            str(proto_kernel_abs_path),
            ExecOperation.op_eval.value,
        ]
    )


@requires_max_python
def test_instant_scenario_start_presents_clean_argv(tmp_path: Path):
    """
    This test runs `ExecOperation.op_start` directly via `proto_code`
    (rather than via a dedicated `entry_script`) - see FT_21_75_54_18.instant_scenario.md.

    Unlike a dedicated `entry_script` (whose own `sys.argv` is naturally clean), `op_start`
    runs in the same process/argv as `proto_kernel.py start <main_func>` itself, so it must
    strip its own `start`/`main_func` CLI args before calling the target function - otherwise
    a target function that inspects `sys.argv` on its own (e.g. a `click`/`argparse` CLI) sees
    unexpected extra arguments.
    """

    # given:

    (
        proto_kernel_abs_path,
        ref_root_abs_path,
        project_dir_abs_path,
    ) = create_min_leaps_shape(tmp_path)

    run_primer_main([str(proto_kernel_abs_path)])

    # when:

    sub_proc = subprocess.run(
        [
            str(proto_kernel_abs_path),
            ExecOperation.op_start.value,
            "local_doc.cmd_start_example:custom_start_main_checks_clean_argv",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    # then:

    assert "Hello, world!" in sub_proc.stdout
