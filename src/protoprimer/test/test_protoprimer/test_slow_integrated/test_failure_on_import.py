import pathlib
import stat
import subprocess

from local_test.integrated_helper import (
    create_conf_client_file,
    create_conf_env_file,
    create_conf_primer_file,
    create_plain_proto_code,
    create_test_pyproject_toml,
    switch_to_ref_root_abs_path,
    test_pyproject_src_dir_rel_path,
)
from protoprimer.primer_kernel import (
    ConfConstClient,
    ConfConstInput,
    ConfConstPrimer,
)
from protoprimer.proto_generator import generate_entry_script_content


def test_failure_on_import(tmp_path: pathlib.Path):
    # given:
    ref_root_abs_path = switch_to_ref_root_abs_path(tmp_path)

    # ===
    proto_code_dir_abs_path = (
        ref_root_abs_path / ConfConstInput.default_proto_conf_dir_rel_path
    )
    create_plain_proto_code(proto_code_dir_abs_path)
    create_conf_primer_file(
        ref_root_abs_path,
        proto_code_dir_abs_path,
    )

    # ===
    project_dir_abs_path = ref_root_abs_path / test_pyproject_src_dir_rel_path
    create_test_pyproject_toml(project_dir_abs_path, [])

    # ===
    conf_env_dir_abs_path = (
        ref_root_abs_path / ConfConstClient.default_client_default_env_dir_rel_path
    )
    create_conf_env_file(
        ref_root_abs_path,
        conf_env_dir_abs_path,
        project_dir_abs_path,
    )

    # ===
    conf_client_dir_abs_path = (
        ref_root_abs_path / ConfConstPrimer.default_client_conf_dir_rel_path
    )
    create_conf_client_file(
        ref_root_abs_path,
        conf_client_dir_abs_path,
        conf_env_dir_abs_path,
    )

    # ===
    non_existing_module = "non_existing_module"
    non_existing_function = "non_existing_function"
    entry_script_content = generate_entry_script_content(
        non_existing_module,
        non_existing_function,
    )
    entry_script_path = ref_root_abs_path / "test_entry_script"
    with open(entry_script_path, "w") as f:
        f.write(entry_script_content)
    entry_script_path.chmod(entry_script_path.stat().st_mode | stat.S_IEXEC)

    # when:
    sub_proc = subprocess.run(
        "./test_entry_script",
        shell=True,
        text=True,
        capture_output=True,
    )

    # then:
    assert sub_proc.returncode != 0
    assert (
        f"{ModuleNotFoundError.__name__}: No module named '{non_existing_module}'"
        in sub_proc.stderr
    )
