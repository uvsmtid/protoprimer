from __future__ import annotations

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    ConfField,
    RootNode_primer,
)


def test_relationship():
    assert_test_module_name_embeds_str(RootNode_primer.__name__)


def test_render_config_with_primer_fields():

    state_input_proto_conf_primer_file_abs_path_eval_finalized = (
        "/abs/path/to/file.json"
    )

    config_data = {
        ConfField.field_primer_ref_root_dir_rel_path.value: "../..",
        ConfField.field_primer_conf_client_file_rel_path.value: "client.json",
    }

    root_node = RootNode_primer(
        0,
        config_data,
        state_input_proto_conf_primer_file_abs_path_eval_finalized,
    )

    expected_output = """\
# The data is loaded from file [/abs/path/to/file.json].
leap_primer = {
    "primer_ref_root_dir_rel_path":
        # The path is relative to dir [/abs/path/to]:
        "../..",
    "primer_conf_client_file_rel_path":
        # The path is relative to dir specified in "primer_ref_root_dir_rel_path" field:
        "client.json",
}
"""
    assert root_node.render_node() == expected_output
