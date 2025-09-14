import os
import pathlib

import protoprimer
from local_repo.sub_proc_util import (
    get_command_code,
    get_command_output,
)
from local_test.package_version_verifier import extract_package_version
from local_test.toml_handler import save_toml_data
from protoprimer.primer_kernel import (
    ConfConstClient,
    ConfConstEnv,
    ConfConstInput,
    ConfConstPrimer,
    ConfField,
    write_json_file,
)
from test_protoprimer.test_integrated.integrated_helper import (
    switch_to_test_dir_with_plain_proto_code,
)


def test_reinstall(tmp_path: pathlib.Path):

    # given:

    switch_to_test_dir_with_plain_proto_code(tmp_path)

    os.mkdir(tmp_path / "pyproject")

    protoprimer_project_dir = pathlib.Path(protoprimer.__file__).parent.parent.parent

    toml_data = {
        "project": {
            "name": "whatever",
            "version": "0.0.0.dev0",
            "dependencies": [
                f"protoprimer @ file://{protoprimer_project_dir}",
                "pyfakefs",
            ],
        }
    }
    save_toml_data(
        str(tmp_path / "pyproject" / "pyproject.toml"),
        toml_data,
    )

    prime_conf_data = {
        ConfField.field_primer_ref_root_dir_rel_path.value: ".",
        ConfField.field_primer_conf_client_file_rel_path.value: ConfConstPrimer.default_client_conf_file_rel_path,
    }
    write_json_file(
        str(tmp_path / ConfConstInput.default_file_basename_conf_primer),
        prime_conf_data,
    )

    client_conf_data = {
        ConfField.field_client_link_name_dir_rel_path.value: ConfConstClient.default_dir_rel_path_leap_env_link_name,
        ConfField.field_client_default_target_dir_rel_path.value: ConfConstClient.default_client_default_target_dir_rel_path,
    }
    os.makedirs(
        os.path.dirname(tmp_path / ConfConstPrimer.default_client_conf_file_rel_path)
    )
    write_json_file(
        str(tmp_path / ConfConstPrimer.default_client_conf_file_rel_path),
        client_conf_data,
    )

    env_conf_data = {
        ConfField.field_env_local_python_file_abs_path.value: ConfConstEnv.default_file_abs_path_python,
        ConfField.field_env_local_venv_dir_rel_path.value: ConfConstEnv.default_dir_rel_path_venv,
        ConfField.field_env_project_descriptors.value: [
            {
                ConfField.field_env_build_root_dir_rel_path.value: "pyproject",
                ConfField.field_env_install_extras.value: [],
            },
        ],
    }

    # The bootstrap process will create a symlink from lconf to the directory containing this file:
    env_conf_file = tmp_path / ConfConstClient.default_file_basename_leap_env
    write_json_file(
        str(env_conf_file),
        env_conf_data,
    )

    package_name = "pyfakefs"
    constraints_file = env_conf_file.parent / "constraints.txt"
    constraints_file.write_text(f"{package_name}==5.7.4")

    # when:

    get_command_code("./primer_kernel.py")

    # then:

    venv_pip = tmp_path / ConfConstEnv.default_dir_rel_path_venv / "bin" / "pip"
    pip_freeze_output_install = get_command_output(f"{venv_pip} freeze")
    package_version_install = extract_package_version(
        pip_freeze_output_install, package_name
    )
    assert f"{package_name}==5.7.4" in pip_freeze_output_install

    # when:

    get_command_code("./primer_kernel.py --reinstall")

    # then:

    pip_freeze_output_reinstall = get_command_output(f"{venv_pip} freeze")

    package_version_reinstall = extract_package_version(
        pip_freeze_output_reinstall, package_name
    )
    assert package_version_install < package_version_reinstall
