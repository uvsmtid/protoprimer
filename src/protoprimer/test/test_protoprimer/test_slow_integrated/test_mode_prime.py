import os
from pathlib import Path

from local_test.fat_mocked_helper import (
    assert_editable_install,
    run_primer_main,
)
from local_test.integrated_helper import (
    create_max_layout,
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
)


def test_relationship():
    assert_test_module_name_embeds_str(RunMode.mode_prime.value)


def test_prime_mode(tmp_path: Path):

    assert_test_func_name_embeds_str(RunMode.mode_prime.value)

    # given:

    (
        proto_kernel_abs_path,
        ref_root_abs_path,
        project_dir_abs_path,
    ) = create_max_layout(tmp_path)

    # when:

    # TODO: Variate prime mode tests for cases when different combinations of fields are missing.
    run_primer_main(
        [
            str(proto_kernel_abs_path),
            SyntaxArg.arg_v,
        ]
    )

    # then:

    assert_editable_install(project_dir_abs_path, test_package_name)

    gconf_dir = ref_root_abs_path / ConfDst.dst_global.value
    lconf_dir = ref_root_abs_path / ConfDst.dst_local.value

    # TODO: Unify names for default conf files:
    conf_primer_file = (
        ref_root_abs_path
        / ConfConstGeneral.name_proto_code
        / ConfConstInput.default_file_basename_conf_primer
    )
    conf_client_file = (
        ref_root_abs_path / ConfConstPrimer.default_client_conf_file_rel_path
    )
    conf_env_file = ref_root_abs_path / ConfConstClient.default_env_conf_file_rel_path

    assert os.path.isdir(gconf_dir) and not os.path.islink(gconf_dir)
    assert os.path.isdir(lconf_dir) and os.path.islink(lconf_dir)

    assert os.path.isfile(conf_primer_file)
    assert os.path.isfile(conf_client_file)
    assert os.path.isfile(conf_env_file)

    # when:
    # re-run in config mode - it should not fail:

    run_primer_main(
        [
            str(proto_kernel_abs_path),
            RunMode.mode_config.value,
        ]
    )
