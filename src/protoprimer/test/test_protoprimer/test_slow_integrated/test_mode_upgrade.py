import pathlib

from local_repo.sub_proc_util import (
    get_command_output,
)
from local_test.fat_mocked_helper import run_primer_main
from local_test.integrated_helper import (
    create_conf_client_file,
    create_conf_env_file,
    create_conf_primer_file,
    create_plain_proto_code,
    create_test_pyproject_toml,
    switch_to_ref_root_abs_path,
    test_pyproject_src_dir_rel_path,
)
from local_test.package_version_verifier import extract_package_version
from protoprimer.primer_kernel import (
    ConfConstClient,
    ConfConstEnv,
    ConfConstInput,
    ConfConstPrimer,
    RunMode,
    SyntaxArg,
)


def test_upgrade(tmp_path: pathlib.Path):

    # given:

    ref_root_abs_path = switch_to_ref_root_abs_path(tmp_path)

    # === create `ConfLeap.leap_primer`

    proto_code_dir_abs_path = (
        ref_root_abs_path / ConfConstInput.default_proto_conf_dir_rel_path
    )
    proto_kernel_abs_path: pathlib.Path = create_plain_proto_code(
        proto_code_dir_abs_path
    )
    create_conf_primer_file(
        ref_root_abs_path,
        proto_code_dir_abs_path,
    )

    # === create `pyproject.toml`

    project_dir_abs_path = ref_root_abs_path / test_pyproject_src_dir_rel_path
    create_test_pyproject_toml(project_dir_abs_path, ["pyfakefs"])

    # === create `ConfLeap.leap_env` / `default_env`

    conf_env_dir_abs_path = (
        ref_root_abs_path / ConfConstClient.default_default_env_dir_rel_path
    )

    create_conf_env_file(
        ref_root_abs_path,
        conf_env_dir_abs_path,
        project_dir_abs_path,
    )

    # === create `ConfLeap.leap_client`

    conf_client_dir_abs_path = (
        ref_root_abs_path / ConfConstPrimer.default_client_conf_dir_rel_path
    )

    create_conf_client_file(
        ref_root_abs_path,
        conf_client_dir_abs_path,
        conf_env_dir_abs_path,
        project_dir_abs_path,
    )

    # ===

    package_name = "pyfakefs"
    constraints_file = conf_env_dir_abs_path / ConfConstEnv.constraints_txt_basename
    constraints_file.write_text(f"{package_name}==5.7.4")

    # when:

    run_primer_main(
        [
            str(proto_kernel_abs_path),
            "prime",
            SyntaxArg.arg_v,
            SyntaxArg.arg_v,
        ]
    )

    # then:

    venv_pip = (
        ref_root_abs_path / ConfConstEnv.default_dir_rel_path_venv / "bin" / "pip"
    )
    pip_freeze_output_install = get_command_output(f"{venv_pip} freeze")
    package_version_install = extract_package_version(
        pip_freeze_output_install,
        package_name,
    )
    assert f"{package_name}==5.7.4" in pip_freeze_output_install

    # when:

    run_primer_main(
        [
            str(proto_kernel_abs_path),
            RunMode.mode_upgrade.value,
            SyntaxArg.arg_v,
            SyntaxArg.arg_v,
        ]
    )

    # then:

    pip_freeze_output_reinstall = get_command_output(f"{venv_pip} freeze")

    package_version_reinstall = extract_package_version(
        pip_freeze_output_reinstall,
        package_name,
    )
    assert package_version_install < package_version_reinstall
