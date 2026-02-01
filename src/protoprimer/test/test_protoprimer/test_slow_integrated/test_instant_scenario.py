import os
from pathlib import Path

from local_test.fat_mocked_helper import (
    assert_editable_install,
    run_primer_main,
)
from local_test.integrated_helper import (
    create_min_layout,
    test_package_name,
)
from protoprimer.primer_kernel import (
    ConfDst,
    RunMode,
    SyntaxArg,
    TopDir,
)


def test_instant_scenario(tmp_path: Path):
    """
    This test runs `proto_code` directly (rather than importing it via `entry_script`).

    It uses `create_min_layout` (see FT_59_95_81_63.env_layout.md).
    """

    # given:

    (
        proto_kernel_abs_path,
        ref_root_abs_path,
        project_dir_abs_path,
    ) = create_min_layout(tmp_path)

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
    # re-run in config mode - it should not fail:

    run_primer_main(
        [
            str(proto_kernel_abs_path),
            RunMode.mode_config.value,
        ]
    )
