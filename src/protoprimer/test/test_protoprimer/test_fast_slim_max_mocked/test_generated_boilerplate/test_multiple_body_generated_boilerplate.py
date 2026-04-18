"""
FT_56_85_65_41.generated_boilerplate.md
"""

from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    ConfConstGeneral,
    read_text_file,
    _replace_multiple_body_in_empty_lines,
    write_text_file,
)

_boilerplate_text = ConfConstGeneral.func_get_proto_code_generated_boilerplate_multiple_body(primer_kernel).strip("\n")


def _call(fs, input_content: str) -> str:
    input_path = "/test_input.py"
    output_path = "/test_output.py"
    fs.create_file(input_path, contents=input_content)
    boilerplate_text = ConfConstGeneral.func_get_proto_code_generated_boilerplate_multiple_body(primer_kernel)
    output_text = _replace_multiple_body_in_empty_lines(
        input_text=read_text_file(input_path),
        boilerplate_text=boilerplate_text,
        min_lines_between=ConfConstGeneral.min_lines_between_generated_boilerplate,
    )
    write_text_file(output_path, output_text)
    return read_text_file(output_path)


def test_no_replacement_when_lines_less_than_min(fs):
    # given: 19 non-empty lines (< min=20) then empty — no replacement.

    input_content = (
        #
        "line_01\n"
        "line_02\n"
        "line_03\n"
        "line_04\n"
        "line_05\n"
        "line_06\n"
        "line_07\n"
        "line_08\n"
        "line_09\n"
        "line_10\n"
        "line_11\n"
        "line_12\n"
        "line_13\n"
        "line_14\n"
        "line_15\n"
        "line_16\n"
        "line_17\n"
        "line_18\n"
        "line_19\n"
        "\n"
        "trailing\n"
    )

    # when:

    actual_content = _call(fs, input_content)

    # then: unchanged — only 19 non-empty lines passed before the empty line.

    expected_content = (
        #
        "line_01\n"
        "line_02\n"
        "line_03\n"
        "line_04\n"
        "line_05\n"
        "line_06\n"
        "line_07\n"
        "line_08\n"
        "line_09\n"
        "line_10\n"
        "line_11\n"
        "line_12\n"
        "line_13\n"
        "line_14\n"
        "line_15\n"
        "line_16\n"
        "line_17\n"
        "line_18\n"
        "line_19\n"
        "\n"
        "trailing\n"
    )
    assert actual_content == expected_content


def test_replacement_when_lines_equal_min(fs):
    # given: 20 non-empty lines (= min=20) then empty — replacement at the empty line.

    input_content = (
        #
        "line_01\n"
        "line_02\n"
        "line_03\n"
        "line_04\n"
        "line_05\n"
        "line_06\n"
        "line_07\n"
        "line_08\n"
        "line_09\n"
        "line_10\n"
        "line_11\n"
        "line_12\n"
        "line_13\n"
        "line_14\n"
        "line_15\n"
        "line_16\n"
        "line_17\n"
        "line_18\n"
        "line_19\n"
        "line_20\n"
        "\n"
        "trailing\n"
    )

    # when:

    actual_content = _call(fs, input_content)

    # then: empty line replaced by boilerplate line (1:1).

    expected_content = (
        #
        "line_01\n"
        "line_02\n"
        "line_03\n"
        "line_04\n"
        "line_05\n"
        "line_06\n"
        "line_07\n"
        "line_08\n"
        "line_09\n"
        "line_10\n"
        "line_11\n"
        "line_12\n"
        "line_13\n"
        "line_14\n"
        "line_15\n"
        "line_16\n"
        "line_17\n"
        "line_18\n"
        "line_19\n"
        "line_20\n"
        f"{_boilerplate_text}\n"
        "trailing\n"
    )
    assert actual_content == expected_content


def test_replacement_when_lines_between_min_and_max(fs):
    # given: 25 non-empty lines (min=20 < 25 < max=40) then empty — replacement.

    input_content = (
        #
        "line_01\n"
        "line_02\n"
        "line_03\n"
        "line_04\n"
        "line_05\n"
        "line_06\n"
        "line_07\n"
        "line_08\n"
        "line_09\n"
        "line_10\n"
        "line_11\n"
        "line_12\n"
        "line_13\n"
        "line_14\n"
        "line_15\n"
        "line_16\n"
        "line_17\n"
        "line_18\n"
        "line_19\n"
        "line_20\n"
        "line_21\n"
        "line_22\n"
        "line_23\n"
        "line_24\n"
        "line_25\n"
        "\n"
        "trailing\n"
    )

    # when:

    actual_content = _call(fs, input_content)

    # then: empty line replaced by boilerplate line.

    expected_content = (
        #
        "line_01\n"
        "line_02\n"
        "line_03\n"
        "line_04\n"
        "line_05\n"
        "line_06\n"
        "line_07\n"
        "line_08\n"
        "line_09\n"
        "line_10\n"
        "line_11\n"
        "line_12\n"
        "line_13\n"
        "line_14\n"
        "line_15\n"
        "line_16\n"
        "line_17\n"
        "line_18\n"
        "line_19\n"
        "line_20\n"
        "line_21\n"
        "line_22\n"
        "line_23\n"
        "line_24\n"
        "line_25\n"
        f"{_boilerplate_text}\n"
        "trailing\n"
    )
    assert actual_content == expected_content


def test_replacement_when_lines_equal_max(fs):
    # given: 40 non-empty lines (= max=40) then empty — replacement at the boundary.

    input_content = "".join(f"line_{i:02d}\n" for i in range(1, 41)) + "\n" + "trailing\n"

    # when:

    actual_content = _call(fs, input_content)

    # then: empty line replaced by boilerplate line.

    expected_content = "".join(f"line_{i:02d}\n" for i in range(1, 41)) + f"{_boilerplate_text}\n" + "trailing\n"
    assert actual_content == expected_content


def test_no_replacement_when_lines_exceed_max(fs):
    # given: 41 non-empty lines (> max=40) with no empty line — no replacement possible.

    input_content = "".join(f"line_{i:02d}\n" for i in range(1, 42))

    # when:

    actual_content = _call(fs, input_content)

    # then: unchanged — no empty line to replace.

    assert actual_content == input_content
