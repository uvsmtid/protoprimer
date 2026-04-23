import pathlib
import stat
import subprocess
import sys

from local_test import cmd_check_context_isolation
from local_test.integrated_helper import (
    create_conf_client_file,
    create_conf_env_file,
    create_conf_primer_file,
    create_plain_proto_code,
    create_test_pyproject_toml,
    switch_to_ref_root_abs_path,
    test_pyproject_src_dir_rel_path,
    test_python_version,
)
from protoprimer.primer_kernel import (
    ConfConstClient,
    ConfConstGeneral,
    ConfConstInput,
    ConfConstPrimer,
    SubCommand,
    SyntaxArg,
    VenvDriverPip,
)
from protoprimer.proto_generator import generate_entry_script_content

from local_test.fat_mocked_helper import run_primer_main


def test_start_app_cleans_protoprimer_env_vars(tmp_path: pathlib.Path):
    """
    FT_66_02_54_56.context_isolation.md
    """

    # given:

    ref_root_abs_path = switch_to_ref_root_abs_path(tmp_path)

    proto_code_dir_abs_path = ref_root_abs_path / ConfConstInput.default_proto_conf_dir_rel_path
    proto_kernel_abs_path: pathlib.Path = create_plain_proto_code(proto_code_dir_abs_path)
    create_conf_primer_file(
        ref_root_abs_path,
        proto_code_dir_abs_path,
    )

    arbitrary_venv_dir = ref_root_abs_path / "arbitrary_venv"
    venv_driver = VenvDriverPip(
        test_python_version,
        sys.executable,
        str(arbitrary_venv_dir),
    )
    venv_driver.create_venv(str(arbitrary_venv_dir))
    arbitrary_venv_python = arbitrary_venv_dir / ConfConstGeneral.file_rel_path_venv_python

    project_dir_abs_path = ref_root_abs_path / test_pyproject_src_dir_rel_path
    create_test_pyproject_toml(project_dir_abs_path)

    common_env_dir_name = ConfConstClient.common_env_name
    common_env_dir_abs_path = ref_root_abs_path / common_env_dir_name
    create_conf_env_file(
        ref_root_abs_path,
        common_env_dir_abs_path,
        project_dir_abs_path,
    )

    conf_client_dir_abs_path = ref_root_abs_path / ConfConstPrimer.default_client_conf_dir_rel_path
    create_conf_client_file(
        ref_root_abs_path,
        conf_client_dir_abs_path,
        common_env_dir_abs_path,
        project_dir_abs_path,
    )

    start_app_script_abs_path = ref_root_abs_path / "start_app"
    start_app_script_content = generate_entry_script_content(
        SubCommand.command_start.value,
        str(proto_kernel_abs_path),
        str(start_app_script_abs_path),
        f"{cmd_check_context_isolation.__name__}",
        f"{cmd_check_context_isolation.custom_main.__name__}",
        {},
    )
    with open(start_app_script_abs_path, "w") as f:
        f.write(start_app_script_content)
    start_app_script_abs_path.chmod(start_app_script_abs_path.stat().st_mode | stat.S_IEXEC)

    # when:
    # bootstrap env

    run_primer_main(
        [
            str(proto_kernel_abs_path),
            SyntaxArg.arg_v,
            SyntaxArg.arg_v,
        ]
    )

    # when:
    # run start_app
    # See FT_75_87_82_46.entry_script.md

    subprocess.run(
        [
            str(arbitrary_venv_python),
            str(start_app_script_abs_path),
        ],
        check=True,
    )
