import logging
import os
import pathlib
import subprocess

import protoprimer
from local_test.toml_handler import save_toml_data
from protoprimer.primer_kernel import (
    ArgConst,
    ConfConstClient,
    ConfConstInput,
    ConfConstPrimer,
    ConfDst,
    ConfLeap,
    WizardField,
)
from test_protoprimer.test_integrated.integrated_helper import (
    switch_to_test_dir_with_plain_proto_code,
)


def test_wizard_mode_interaction(tmp_path: pathlib.Path):

    # given:

    switch_to_test_dir_with_plain_proto_code(tmp_path)

    os.mkdir(tmp_path / "pyproject")

    protoprimer_project_dir = pathlib.Path(protoprimer.__file__).parent.parent.parent

    toml_data = {
        "project": {
            "name": "whatever",
            "version": "0.0.0.dev0",
            "dependencies": [
                # Install `protoprimer` from local sources:
                f"protoprimer @ file://{protoprimer_project_dir}",
            ],
        }
    }

    # TODO: Figure out how can minimal layout be achieved (when `pyproject.toml` is in the ref root)?
    save_toml_data(
        str(tmp_path / "pyproject" / "pyproject.toml"),
        toml_data,
    )

    logging.info(f"toml_data: {toml_data}")

    command_args = [
        "./primer_kernel.py",
        ArgConst.arg_mode_wizard,
    ]

    sub_proc = subprocess.Popen(
        command_args,
        stdin=subprocess.PIPE,
        text=True,
    )

    # Wizard interaction
    inputs_with_fields: list[tuple[str, WizardField | ConfLeap | None]] = [
        # ---
        ("", WizardField.field_primer_ref_root_dir_rel_path),
        ("", WizardField.field_primer_ref_root_dir_rel_path),
        ("", WizardField.field_primer_conf_client_file_rel_path),
        ("", WizardField.field_primer_conf_client_file_rel_path),
        # ---
        ("y", ConfLeap.leap_client),
        # ---
        ("", WizardField.field_client_link_name_dir_rel_path),
        ("", WizardField.field_client_link_name_dir_rel_path),
        ("", WizardField.field_client_default_target_dir_rel_path),
        ("", WizardField.field_client_default_target_dir_rel_path),
        # ---
        ("y", ConfLeap.leap_client),
        # ---
        ("", WizardField.field_env_local_python_file_abs_path),
        ("", WizardField.field_env_local_python_file_abs_path),
        ("", WizardField.field_env_local_venv_dir_rel_path),
        ("", WizardField.field_env_local_venv_dir_rel_path),
        ("", WizardField.field_env_local_log_dir_rel_path),
        ("", WizardField.field_env_local_log_dir_rel_path),
        ("", WizardField.field_env_local_tmp_dir_rel_path),
        ("", WizardField.field_env_local_tmp_dir_rel_path),
        ("pyproject", WizardField.field_env_build_root_dir_rel_path),
        ("y", WizardField.field_env_build_root_dir_rel_path),
        # ---
        ("y", ConfLeap.leap_client),
        # ---
    ]
    user_responses_only = [user_response for user_response, _ in inputs_with_fields]
    wizard_input = "\n".join(user_responses_only) + "\n"

    # when:

    sub_proc.communicate(input=wizard_input)

    # then:

    assert sub_proc.returncode == 0

    gconf_dir = tmp_path / ConfDst.dst_global.value
    lconf_dir = tmp_path / ConfDst.dst_local.value

    conf_primer_file = tmp_path / ConfConstInput.default_file_basename_conf_primer
    conf_client_file = tmp_path / ConfConstPrimer.default_client_conf_file_rel_path
    conf_env_file = tmp_path / ConfConstClient.default_file_basename_leap_env

    assert os.path.isdir(gconf_dir) and not os.path.islink(gconf_dir)
    assert os.path.isdir(lconf_dir) and os.path.islink(lconf_dir)

    assert os.path.isfile(conf_primer_file)
    assert os.path.isfile(conf_client_file)
    assert os.path.isfile(conf_env_file)
