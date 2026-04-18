import json
import os
import pathlib
import re
import stat
import sys

from local_repo.sub_proc_util import (
    get_command_code,
    get_command_output,
)
from local_test.integrated_helper import (
    create_conf_client_file,
    create_conf_env_file,
    create_conf_primer_file,
    create_plain_proto_code,
    create_test_pyproject_toml,
    switch_to_ref_root_abs_path,
    test_pyproject_src_dir_rel_path,
)
from neoprimer import cmd_eval_conf
from neoprimer.cmd_eval_conf import custom_main
from protoprimer.primer_kernel import (
    ConfConstClient,
    ConfConstInput,
    ConfConstPrimer,
    EnvState,
    EnvVar,
    ExecMode,
    import_proto_module,
)
from protoprimer.proto_generator import generate_entry_script_content


def test_eval_conf_returns_derived_config(tmp_path: pathlib.Path):

    # given:

    ref_root_abs_path = switch_to_ref_root_abs_path(tmp_path)

    # ===

    proto_code_dir_abs_path = ref_root_abs_path / ConfConstInput.default_proto_conf_dir_rel_path
    proto_kernel_abs_path = create_plain_proto_code(proto_code_dir_abs_path)
    create_conf_primer_file(
        ref_root_abs_path,
        proto_code_dir_abs_path,
    )

    # ===

    project_dir_abs_path = ref_root_abs_path / test_pyproject_src_dir_rel_path
    create_test_pyproject_toml(project_dir_abs_path, [])

    # ===

    conf_env_dir_abs_path = ref_root_abs_path / ConfConstClient.default_default_env_dir_rel_path

    create_conf_env_file(
        ref_root_abs_path,
        conf_env_dir_abs_path,
        project_dir_abs_path,
    )

    # ===

    conf_client_dir_abs_path = ref_root_abs_path / ConfConstPrimer.default_client_conf_dir_rel_path

    create_conf_client_file(
        ref_root_abs_path,
        conf_client_dir_abs_path,
        conf_env_dir_abs_path,
        project_dir_abs_path,
    )

    # ===

    # Bootstraps the env before running other commands:
    get_command_code("./proto_code/proto_kernel.py")

    # ===

    eval_conf_script_abs_path = ref_root_abs_path / "eval_conf"
    eval_conf_script_content = generate_entry_script_content(
        ExecMode.mode_boot.value,
        str(proto_kernel_abs_path),
        str(eval_conf_script_abs_path),
        f"{cmd_eval_conf.__name__}",
        f"{custom_main.__name__}",
        {
            EnvVar.var_PROTOPRIMER_DO_INSTALL.value: str(False),
        },
    )
    with open(eval_conf_script_abs_path, "w") as f:
        f.write(eval_conf_script_content)
    eval_conf_script_abs_path.chmod(eval_conf_script_abs_path.stat().st_mode | stat.S_IEXEC)

    # when:

    output = get_command_output("./eval_conf")

    # then:

    # Strip ANSI escape codes (see RenderConfigVisitor._render_node_annotation):
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    clean_output = ansi_escape.sub("", output)

    # Save to a local module:
    module_name = f"derived_config_{tmp_path.name}"
    module_file = tmp_path / f"{module_name}.py"
    module_file.write_text(clean_output)

    # Load it dynamically:
    derived_config_module = import_proto_module(module_name, str(module_file))

    # Access the values it sets:
    # It should have leap_input, leap_primer, leap_client, leap_env, leap_derived
    assert hasattr(derived_config_module, "leap_derived")
    derived_config = derived_config_module.leap_derived

    assert isinstance(derived_config, dict)

    # Compare the values to the config files created during that test:
    assert derived_config[EnvState.state_local_venv_dir_abs_path_inited.name] == str(ref_root_abs_path / "venv")
    assert derived_config[EnvState.state_local_cache_dir_abs_path_inited.name] == str(ref_root_abs_path / "cache")
    assert derived_config[EnvState.state_project_descriptors_inited.name] == [
        {
            "build_root_dir_rel_path": "pyproject_src",
            "install_extras": [],
            "install_group": "whatever_group_main",
        }
    ]
