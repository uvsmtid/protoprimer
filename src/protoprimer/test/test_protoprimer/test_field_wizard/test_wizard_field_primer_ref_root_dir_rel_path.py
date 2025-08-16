import io
import os
import sys
from unittest.mock import MagicMock

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    ConfField,
    StateNode,
    wizard_confirm_single_value,
    WizardField,
)


# noinspection PyPep8Naming
def test_relationship():
    assert_test_module_name_embeds_str(
        ConfField.field_primer_ref_root_dir_rel_path.name
    )


@pytest.mark.parametrize(
    "user_input_lines, expected_field_value, expected_stdout_lines",
    [
        (
            [
                "new_ref_root_1",
                "y",
            ],
            "new_ref_root_1",
            [
                "---",
                "progress",
                "progress",
                "Field: primer_ref_root_dir_rel_path",
                "Description:",
                "Enter",
                "The base",
                "Confirming...",
            ],
        ),
        (
            [
                "",
                "",
            ],
            "old_ref_root",
            [
                "---",
                "progress",
                "progress",
                "Field: primer_ref_root_dir_rel_path",
                "Description:",
                "Enter",
                "The base",
                "Skipping...",
            ],
        ),
        (
            [
                "another_ref_root",
                "n",
                "new_ref_root_2",
                "y",
            ],
            "new_ref_root_2",
            [
                "---",
                "progress",
                "progress",
                "Field: primer_ref_root_dir_rel_path",
                "Description:",
                "Enter",
                "The base",
                "Retrying...",
                "---",
                "progress",
                "progress",
                "Field: primer_ref_root_dir_rel_path",
                "Description:",
                "Enter",
                "The base",
                "Confirming...",
            ],
        ),
        (
            [
                "non_existent_path",
                "new_ref_root_1",
                "y",
            ],
            "new_ref_root_1",
            [
                "---",
                "progress",
                "progress",
                "Field: primer_ref_root_dir_rel_path",
                "Description:",
                "Enter",
                "The base",
                "point to a non-existent path",
                "Failing...",
                "---",
                "progress",
                "progress",
                "Field: primer_ref_root_dir_rel_path",
                "Description:",
                "Enter",
                "The base",
                "Confirming...",
            ],
        ),
    ],
)
def test_wizard_confirm_single_value_field_primer_ref_root_dir_rel_path(
    # Standard `pytest` name to capture `stderr` & `stdout`:
    capsys,
    fs,
    monkeypatch,
    user_input_lines,
    expected_field_value,
    expected_stdout_lines,
):
    # given:

    monkeypatch.setattr(sys, "stdin", io.StringIO("\n".join(user_input_lines) + "\n"))

    file_data = {
        ConfField.field_primer_ref_root_dir_rel_path.value: "old_ref_root",
    }

    wizard_meta = WizardField.field_primer_ref_root_dir_rel_path.value

    # when:

    mock_state_node = MagicMock(spec=StateNode)
    mock_state_node.eval_parent_state.return_value = "mocked_path"

    fs.create_dir(os.path.join("mocked_path", "new_ref_root_1"))
    fs.create_dir(os.path.join("mocked_path", "old_ref_root"))
    fs.create_dir(os.path.join("mocked_path", "new_ref_root_2"))
    fs.create_dir(os.path.join("mocked_path", "another_ref_root"))

    wizard_confirm_single_value(
        state_node=mock_state_node,
        wizard_meta=wizard_meta,
        file_data=file_data,
        sub_ordinal_n=1,
        sub_size=1,
        total_ordinal_n=1,
        total_size=len(WizardField),
    )

    # then:

    expected_file_data = {
        ConfField.field_primer_ref_root_dir_rel_path.value: expected_field_value,
    }
    assert file_data == expected_file_data

    captured_stdout_combined = capsys.readouterr()
    captured_stdout_lines = captured_stdout_combined.out.splitlines()
    assert len(expected_stdout_lines) == len(captured_stdout_lines)
    for line_i, expected_stdout_line in enumerate(expected_stdout_lines):
        assert expected_stdout_line in captured_stdout_lines[line_i]
