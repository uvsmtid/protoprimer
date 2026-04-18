"""
FT_56_85_65_41.generated_boilerplate.md
"""

from pre_commit.commands.clean import clean

import pathlib

from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    ConfConstGeneral,
    _is_blank_line,
)

max_lines_between_generated_boilerplate = 40


def _clean_placeholder_lines(file_text: str) -> str:
    """
    This makes this test ignore references to `FT_56_85_65_41.generated_boilerplate.md`.
    """
    clean_lines = []
    for file_line in file_text.splitlines():
        if "FT_56_85_65_41.generated_boilerplate.md" in file_line:
            clean_lines.append("")
        else:
            clean_lines.append(file_line)
    return "\n".join(clean_lines)


_primer_kernel_content: str = _clean_placeholder_lines(open(str(primer_kernel.__file__)).read())


def test_single_header_placeholder():

    # given:

    file_lines = _primer_kernel_content.splitlines()
    boilerplate_text = ConfConstGeneral.func_get_proto_code_generated_boilerplate_single_header(primer_kernel)
    boilerplate_height = len(boilerplate_text.splitlines())

    # when:

    is_found = False
    for line_index in range(1, len(file_lines) - boilerplate_height + 1):
        if all(_is_blank_line(file_lines[line_index + offset_index]) for offset_index in range(boilerplate_height)):
            is_found = True
            break

    # then:

    if not is_found:
        raise AssertionError(f"[{primer_kernel.__file__}] must have [{boilerplate_height}] consecutive empty lines after shebang:")


def test_multiple_body_placeholder():

    # given:

    file_lines = _primer_kernel_content.splitlines()

    # when:

    max_run = 0
    curr_run = 0
    for file_line in file_lines:
        if not _is_blank_line(file_line):
            curr_run += 1
            if curr_run > max_run:
                max_run = curr_run
        else:
            curr_run = 0

    # then:

    if max_run > max_lines_between_generated_boilerplate:
        raise AssertionError(f"[{primer_kernel.__file__}] has a run of [{max_run}] consecutive non-empty lines (max allowed: [{max_lines_between_generated_boilerplate}]):")


def test_kernel_files_line_count():

    # given:

    primer_kernel_file_path = pathlib.Path(primer_kernel.__file__)
    # The `proto_kernel.py` is located in `cmd/proto_code/` relative to the repo root.
    repo_root = primer_kernel_file_path.parents[4]
    proto_kernel_file_path = repo_root / "cmd" / "proto_code" / "proto_kernel.py"

    # when:

    primer_kernel_line_count = len(primer_kernel_file_path.read_text().splitlines())
    proto_kernel_line_count = len(proto_kernel_file_path.read_text().splitlines())

    # then:

    if primer_kernel_line_count != proto_kernel_line_count:
        # Re-run `./prime` sync the `*_kernel.py` files before running this test:
        raise AssertionError(f"line count mismatch: primer_kernel.py [{primer_kernel_line_count}] != proto_kernel.py [{proto_kernel_line_count}]")
