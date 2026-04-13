import os
from pathlib import Path

from local_test.case_condition import requires_max_python
from local_test.fat_mocked_helper import (
    run_primer_main,
)
from local_test.integrated_helper import (
    create_max_layout,
    create_python_version_file,
    test_python_version,
)
from local_test.name_assertion import (
    assert_test_module_name_embeds_str,
)
from protoprimer.primer_kernel import (
    ConfConstClient,
    ExecMode,
    SyntaxArg,
    TopDir,
)


def test_relationship():
    assert_test_module_name_embeds_str(ExecMode.mode_boot.value)


@requires_max_python
def test_mode_boot_without_local_config(tmp_path: Path):
    """
    Make sure bootstrap works with all defaults (from global config) when the local config file is missing.
    """

    # given:

    (
        proto_kernel_abs_path,
        ref_root_abs_path,
        project_dir_abs_path,
    ) = create_max_layout(tmp_path)

    # Use the `ConfConstGeneral.python_version_file_basename` file for this case of missing global config:
    create_python_version_file(str(ref_root_abs_path), test_python_version)

    # delete local config:

    env_local_config_abs_path = ref_root_abs_path / ConfConstClient.default_env_conf_file_rel_path
    assert os.path.isfile(env_local_config_abs_path)
    env_local_config_abs_path.unlink()

    # when:

    run_primer_main(
        [
            str(proto_kernel_abs_path),
            SyntaxArg.arg_v,
            SyntaxArg.arg_v,
        ]
    )

    # then:

    assert os.path.exists(ref_root_abs_path / TopDir.dir_venv.value)
