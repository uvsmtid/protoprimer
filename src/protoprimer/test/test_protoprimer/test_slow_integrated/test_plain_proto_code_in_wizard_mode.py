import os
import pathlib
import subprocess

import pytest

from local_test.integrated_helper import (
    create_conf_primer_file,
    create_plain_proto_code,
    create_test_pyproject_toml,
    switch_to_ref_root_abs_path,
    test_pyproject_src_dir_rel_path,
)
from protoprimer.primer_kernel import (
    ConfConstClient,
    ConfConstGeneral,
    ConfConstInput,
    ConfConstPrimer,
    ConfDst,
    ConfLeap,
    SyntaxArg,
    WizardField,
)


# TODO: obsolete: FT_32_54_11_56.wizard_mode.md:
@pytest.mark.skip(reason="TODO: obsolete: FT_32_54_11_56.wizard_mode.md:")
def test_wizard_mode_interaction(tmp_path: pathlib.Path):

    # given:

    ref_root_abs_path = switch_to_ref_root_abs_path(tmp_path)

    # ===

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

    conf_env_dir_abs_path = (
        ref_root_abs_path / ConfConstClient.default_client_default_env_dir_rel_path
    )
    conf_env_dir_abs_path.mkdir(parents=True)

    # ===

    # TODO: Figure out how can minimal layout be achieved (when `pyproject.toml` is in the ref root)?
    project_dir_abs_path = ref_root_abs_path / test_pyproject_src_dir_rel_path
    create_test_pyproject_toml(project_dir_abs_path)

    # ===

    command_args = [
        proto_kernel_abs_path,
        SyntaxArg.arg_mode_wizard,
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
        ("", WizardField.field_client_default_env_dir_rel_path),
        ("", WizardField.field_client_default_env_dir_rel_path),
        ("", WizardField.field_required_python_file_abs_path),
        ("", WizardField.field_required_python_file_abs_path),
        ("", WizardField.field_local_venv_dir_rel_path),
        ("", WizardField.field_local_venv_dir_rel_path),
        ("", WizardField.field_local_log_dir_rel_path),
        ("", WizardField.field_local_log_dir_rel_path),
        ("", WizardField.field_local_tmp_dir_rel_path),
        ("", WizardField.field_local_tmp_dir_rel_path),
        (
            test_pyproject_src_dir_rel_path,
            WizardField.field_build_root_dir_rel_path,
        ),
        ("y", WizardField.field_build_root_dir_rel_path),
        # ---
        ("y", ConfLeap.leap_client),
        # ---
        # See: FT_32_54_11_56.wizard_mode.md:
        # We wizard fields into `ConfLeap.leap_client`.
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

    gconf_dir = ref_root_abs_path / ConfDst.dst_global.value
    lconf_dir = ref_root_abs_path / ConfDst.dst_local.value

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
