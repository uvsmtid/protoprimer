"""
Helpers for the `test_invoke_condition` test perimeter.

FT_64_09_03_66.invoke_condition.md
"""

from __future__ import annotations

import enum
import os
import pathlib
import shlex
import shutil
import subprocess
import uuid

import pytest

from local_test.case_condition import (
    any_to_bool,
    invoke_condition_env_var,
)

# Label to find (and clean up) leftover containers:
container_label = "protoprimer-test-invoke-condition"

# Pinned public images (nothing is baked into them, nothing special is maintained):
# FT_84_11_73_28.supported_python_versions.md
image_python_3_6 = "python:3.6.15-slim"
image_python_3_7 = "python:3.7.17-slim"
image_python_3_9 = "python:3.9.25-slim"
image_python_3_12 = "python:3.12.12-slim"
image_python_3_14 = "python:3.14.0-slim"
image_debian = "debian:bookworm-slim"

# Boot this repo into `/work/venv` with the `required_python_version` 3.14.0:
boot_max_script = "./prime --env dst/test_python_max"


class InvokeCondition(enum.Enum):
    """
    Registry of all scenarios (title -> number) from `FT_64_09_03_66.invoke_condition.md`.

    The number is the one in `test_invoke_condition_NN.py` file name.
    """

    py_too_old_for_kernel = 1
    py_old_not_required = 2
    py_new_not_required = 3
    py_required_not_found = 4
    py_selector_fails = 5
    py_basename_wrong_version = 6
    py_shims_and_wrappers = 7
    py_without_venv_module = 8
    py_uv_needs_newer_selected_python = 9
    venv_wrong_active = 10
    venv_right_active = 11
    venv_python_is_selected_python = 12
    venv_missing_on_start = 13
    venv_wrong_driver = 14
    venv_wrong_python_version = 15
    venv_broken_or_dangling = 16
    venv_half_created = 17
    venv_moved_or_copied = 18
    venv_with_system_site_packages = 19
    pkg_system_wide = 20
    pkg_user_site = 21
    pkg_via_pythonpath_or_cwd = 22
    pkg_version_skew = 23
    first_process_not_isolated = 24
    env_foreign_python_vars = 25
    env_foreign_tool_vars = 26
    state_var_invalid_value = 27
    state_var_stale_leaked = 28
    state_var_mismatch_reality = 29
    state_var_proto_kernel_wrong = 30
    state_var_mocked_restart_leaked = 31
    invoke_nested_other_repo = 32
    invoke_not_as_script = 33
    invoke_via_symlink = 34
    invoke_concurrent = 35
    invoke_lib_call = 36
    env_selection_mismatch = 37
    host_offline_or_proxied = 38
    host_not_posix = 39
    shell_unsupported = 40

    @property
    def test_file_basename(self) -> str:
        return f"test_invoke_condition_{self.value:02d}.py"


# Scenarios which have no `test_invoke_condition_NN.py` yet (with the reason):
not_covered: dict[InvokeCondition, str] = {
    InvokeCondition.py_shims_and_wrappers: "needs a version manager (`pyenv`, `asdf`, ...) installed in the image; the hypothesis is not confirmed yet",
    InvokeCondition.pkg_version_skew: "covered by the contract compatibility modes `old_proto_on_new_venv` and `old_entry_on_new_proto` (FT_78_72_23_04.backward_compatibility.md)",
    InvokeCondition.env_foreign_python_vars: "not decided how to reproduce: `PYTHONHOME` breaks the first `python` before `protoprimer` starts",
    InvokeCondition.invoke_nested_other_repo: "needs two repos with their own `venv`-s in one container (not implemented yet)",
    InvokeCondition.invoke_concurrent: "the race is timing-dependent (a test was flaky): needs a deterministic reproduction",
    InvokeCondition.host_not_posix: "containers are Linux: needs a Windows host (TODO_50_98_96_87.support_windows.md)",
}


def find_container_engine() -> str | None:
    for engine_name in ["docker", "podman"]:
        if shutil.which(engine_name) is not None:
            return engine_name
    return None


def skip_test_invoke_condition(
    parent_dir_abs_path: str,
    pytest_config,
    pytest_items,
):
    """
    Skips all collected tests in this directory unless `TEST_PROTOPRIMER_INVOKE_CONDITION` is `true` and a container engine is available.

    FT_64_09_03_66.invoke_condition.md
    """

    reason_text: str | None = None
    if not any_to_bool(os.environ.get(invoke_condition_env_var)):
        reason_text = f"Tests under `{parent_dir_abs_path}` skipped by default. " f"Run with environment variable `{invoke_condition_env_var}` set to `true` to enable. "
    elif find_container_engine() is None:
        reason_text = "Neither `docker` nor `podman` is available."

    if reason_text is None:
        return

    skip_marker = pytest.mark.skip(reason=reason_text)
    resolved_parent_path = pathlib.Path(parent_dir_abs_path).resolve()
    for pytest_item in pytest_items:
        resolved_test_path = pathlib.Path(str(pytest_item.fspath)).resolve()
        if resolved_parent_path == resolved_test_path or resolved_parent_path in resolved_test_path.parents:
            pytest_item.add_marker(skip_marker)


def get_repo_root_abs_path() -> pathlib.Path:
    return pathlib.Path(
        subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=str(pathlib.Path(__file__).parent),
            universal_newlines=True,
        ).strip()
    )


def export_clean_tree(dst_dir_path: pathlib.Path) -> pathlib.Path:
    """
    Copy the working tree: tracked and untracked (but not ignored) files.

    It excludes leftovers (`venv`, `lconf`, `cache`, ...) which are `.gitignore`-d.
    """
    repo_root = get_repo_root_abs_path()
    file_rel_paths = subprocess.check_output(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=str(repo_root),
    ).split(b"\0")
    for file_rel_path_bytes in file_rel_paths:
        if not file_rel_path_bytes:
            continue
        file_rel_path = os.fsdecode(file_rel_path_bytes)
        src_path = repo_root / file_rel_path
        dst_path = dst_dir_path / file_rel_path
        if not (src_path.exists() or src_path.is_symlink()):
            # Deleted in the working tree (but still tracked):
            continue
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(src_path), str(dst_path), follow_symlinks=False)
    return dst_dir_path


class StepResult:
    def __init__(
        self,
        exit_code: int,
        stdout: str,
        stderr: str,
    ):
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr

    @property
    def output(self) -> str:
        return f"{self.stdout}\n{self.stderr}"

    def __str__(self) -> str:
        return f"exit_code: [{self.exit_code}]\nstdout:\n{self.stdout}\nstderr:\n{self.stderr}"


class ContainerSession:
    """
    One long-living container: each step (`run`) is a script executed in it,
    so steps can build on each other (for example, boot online, then go offline).

    The clean tree of the repo is read-only at `/src` and copied to `/work` (the working dir of steps).
    """

    src_dir = "/src"
    work_dir = "/work"

    def __init__(
        self,
        image: str,
        tmp_dir_path: pathlib.Path,
    ):
        engine = find_container_engine()
        assert engine is not None
        self.engine: str = engine
        self.image: str = image
        self.tmp_dir_path: pathlib.Path = tmp_dir_path
        self.name: str = f"protoprimer-test-{uuid.uuid4().hex[:12]}"

    def __enter__(self) -> ContainerSession:
        tree_dir_path = export_clean_tree(self.tmp_dir_path / "tree")
        subprocess.run(
            [
                self.engine,
                "run",
                "-d",
                "--init",
                "--name",
                self.name,
                "--label",
                container_label,
                # `z`: relabel for SELinux hosts:
                "-v",
                f"{tree_dir_path}:{self.src_dir}:ro,z",
                self.image,
                "sleep",
                "infinity",
            ],
            check=True,
        )
        copy_result = self.run(f"cp -a {self.src_dir} {self.work_dir}", work_dir="/")
        assert copy_result.exit_code == 0, str(copy_result)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        subprocess.run(
            [self.engine, "rm", "-f", self.name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def run(
        self,
        script: str,
        env: dict[str, str] | None = None,
        work_dir: str | None = None,
        timeout: int = 1800,
    ) -> StepResult:
        """
        Execute the `script` step in the container (does not raise on non-zero exit code).
        """
        command = [
            self.engine,
            "exec",
            "-w",
            work_dir if work_dir is not None else self.work_dir,
        ]
        for env_name, env_value in (env or {}).items():
            command.extend(["-e", f"{env_name}={env_value}"])
        command.extend([self.name, "bash", "-c", script])
        completed = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            timeout=timeout,
        )
        return StepResult(completed.returncode, completed.stdout, completed.stderr)

    def write_file(
        self,
        file_path: str,
        content: str,
    ) -> None:
        """
        Write the `content` (for example, multi-line `python` code) to the `file_path` (relative to the working dir).
        """
        subprocess.run(
            [
                self.engine,
                "exec",
                "-i",
                "-w",
                self.work_dir,
                self.name,
                "bash",
                "-c",
                f"cat > {shlex.quote(file_path)}",
            ],
            input=content,
            universal_newlines=True,
            check=True,
        )

    def disconnect_network(self) -> None:
        """
        Make the container offline (it was created with the default network).
        """
        network_name = "podman" if self.engine == "podman" else "bridge"
        subprocess.run(
            [self.engine, "network", "disconnect", network_name, self.name],
            check=True,
        )
