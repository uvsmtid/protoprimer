import io
import sys
from unittest.mock import MagicMock

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    ConfField,
    ConfLeap,
    StateNode,
    wizard_confirm_single_value,
    WizardField,
)


# noinspection PyPep8Naming
def test_relationship():
    assert_test_module_name_embeds_str(
        ConfField.field_client_link_name_dir_rel_path.name
    )


def test_wizard_field_with_trivial_review(capsys, monkeypatch):
    # given:
    # A wizard field that uses review_value_trivially
    wizard_meta = WizardField.field_client_link_name_dir_rel_path.value
    assert wizard_meta.review_value.__name__ == "review_value_trivially"

    monkeypatch.setattr(sys, "stdin", io.StringIO("new_value\ny\n"))

    file_data = {
        ConfField.field_client_link_name_dir_rel_path.value: "old_value",
    }

    mock_state_node = MagicMock(spec=StateNode)

    # when:
    wizard_confirm_single_value(
        state_node=mock_state_node,
        conf_leap=ConfLeap.leap_client,
        wizard_meta=wizard_meta,
        file_data=file_data,
        sub_ordinal_n=1,
        sub_size=1,
        total_ordinal_n=1,
        total_size=len(WizardField),
    )

    # then:
    # The value should be updated
    assert file_data[ConfField.field_client_link_name_dir_rel_path.value] == "new_value"

    # No "Review:" text should be in the output
    captured = capsys.readouterr()
    assert "Review:" not in captured.out

    # Check for other expected output
    assert "Field: client_link_name_dir_rel_path" in captured.out
    assert "Description:" in captured.out
    assert "Confirming..." in captured.out
