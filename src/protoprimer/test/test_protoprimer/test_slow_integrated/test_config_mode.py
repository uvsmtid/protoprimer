import os
from pathlib import Path

from local_test.fat_mocked_helper import (
    assert_editable_install,
    run_primer_main,
)
from local_test.integrated_helper import (
    create_max_layout,
    create_min_layout,
    test_package_name,
)
from local_test.name_assertion import (
    assert_test_func_name_embeds_str,
    assert_test_module_name_embeds_str,
)
from protoprimer.primer_kernel import (
    ConfConstClient,
    ConfConstGeneral,
    ConfConstInput,
    ConfConstPrimer,
    ConfDst,
    RunMode,
    SyntaxArg,
    TopDir,
)


def test_relationship():
    assert_test_module_name_embeds_str(RunMode.mode_config.value)


def test_config_mode_with_min_layout(tmp_path: Path):

    assert_test_func_name_embeds_str(RunMode.mode_config.value)

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
            SyntaxArg.arg_mode_config,
        ]
    )

    # then:
    # no installation happened:

    assert not os.path.exists(ref_root_abs_path / TopDir.dir_tmp.value)
    assert not os.path.exists(ref_root_abs_path / TopDir.dir_venv.value)
    assert not os.path.exists(ref_root_abs_path / TopDir.dir_cache.value)


def test_config_mode_with_max_layout(tmp_path: Path):

    assert_test_func_name_embeds_str(RunMode.mode_config.value)

    # given:

    (
        proto_kernel_abs_path,
        ref_root_abs_path,
        project_dir_abs_path,
    ) = create_max_layout(tmp_path)

    # when:

    run_primer_main(
        [
            str(proto_kernel_abs_path),
            SyntaxArg.arg_mode_config,
        ]
    )

    # then:
    # no installation happened:

    assert not os.path.exists(ref_root_abs_path / TopDir.dir_tmp.value)
    assert not os.path.exists(ref_root_abs_path / TopDir.dir_venv.value)
    assert not os.path.exists(ref_root_abs_path / TopDir.dir_cache.value)
