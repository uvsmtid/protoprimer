"""
Shared helpers to verify that `ExecOperation.op_wrap` regenerates
already-committed `entry_script`-s byte-for-byte (no `git diff`).

Used by both the `./cmd/*` and `./prime` slow_integrated tests -
see FT_75_87_82_46.entry_script.md / UC_71_59_90_97.generated_entry_script.md.
"""

from __future__ import annotations

import dataclasses
import pathlib
import re
import subprocess
import sys

import protoprimer.primer_kernel
from protoprimer.primer_kernel import (
    EntryFunc,
    ExecOperation,
    SyntaxArg,
)

_ENTRY_FUNC_CALL_REGEX = re.compile(r"proto_kernel\.(?P<entry_func>" rf"{EntryFunc.func_boot_env.value}|{EntryFunc.func_start_app.value}" r")\(\"(?P<main_func>[^\"]+)\"\)")


def get_repo_root_abs_path() -> pathlib.Path:
    """
    See also: `test_kernel_files_line_count`.
    """
    primer_kernel_file_abs_path = pathlib.Path(protoprimer.primer_kernel.__file__)
    return primer_kernel_file_abs_path.parents[4]


def list_cmd_entry_script_rel_paths(
    repo_root_abs_path: pathlib.Path,
) -> list[str]:
    cmd_dir_abs_path = repo_root_abs_path / "cmd"
    return sorted(
        entry.name
        for entry in cmd_dir_abs_path.iterdir()
        if entry.is_file()
        #
    )


@dataclasses.dataclass(frozen=True)
class ParsedEntryScript:
    entry_func: str
    main_func: str


def parse_entry_script(
    entry_script_abs_path: pathlib.Path,
) -> ParsedEntryScript:
    entry_script_content = entry_script_abs_path.read_text()
    regex_match = _ENTRY_FUNC_CALL_REGEX.search(entry_script_content)
    if regex_match is None:
        raise AssertionError(f"Could not find a `{EntryFunc.func_boot_env.value}`/`{EntryFunc.func_start_app.value}` call in [{entry_script_abs_path}]")
    return ParsedEntryScript(
        entry_func=regex_match.group("entry_func"),
        main_func=regex_match.group("main_func"),
    )


def assert_wrap_regenerates_with_no_git_diff(
    repo_root_abs_path: pathlib.Path,
    proto_kernel_abs_path: pathlib.Path,
    entry_script_abs_path: pathlib.Path,
) -> None:
    """
    Runs `ExecOperation.op_wrap` for real against `entry_script_abs_path`
    (an already `git`-tracked, previously generated `entry_script`)
    and asserts `git` reports no changes - i.e., regeneration is idempotent.
    """

    parsed_entry_script = parse_entry_script(entry_script_abs_path)

    subprocess.run(
        [
            sys.executable,
            str(proto_kernel_abs_path),
            ExecOperation.op_wrap.value,
            parsed_entry_script.entry_func,
            SyntaxArg.arg_entry_script_path,
            str(entry_script_abs_path),
            SyntaxArg.arg_main_func,
            parsed_entry_script.main_func,
        ],
        check=True,
        cwd=str(repo_root_abs_path),
    )

    git_diff_process = subprocess.run(
        [
            "git",
            "diff",
            "--exit-code",
            "--",
            str(entry_script_abs_path),
        ],
        cwd=str(repo_root_abs_path),
        capture_output=True,
        text=True,
    )
    assert git_diff_process.returncode == 0, (
        f"`{ExecOperation.op_wrap.value}` regenerated [{entry_script_abs_path}] with changes:\n{git_diff_process.stdout}"
        #
    )
