from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    ConfConstGeneral,
    EntryFunc,
    generate_entry_script_content,
    merge_entry_script_content,
)


def test_relationship():
    assert_test_module_name_embeds_str(merge_entry_script_content.__name__)


def _generate() -> str:
    return generate_entry_script_content(
        EntryFunc.func_boot_env.value,
        "/dummy/path/proto_kernel.py",
        "/dummy/path/entry.py",
        "my_module",
        "my_func",
    )


def test_merge_with_no_existing_content_returns_generated_as_is():

    generated_content = _generate()

    merged_content = merge_entry_script_content(None, generated_content)

    assert merged_content == generated_content


def test_merge_with_existing_content_without_markers_returns_generated_as_is():

    generated_content = _generate()

    merged_content = merge_entry_script_content(
        "#!/usr/bin/env python3\n# some hand-written script, no markers here\n",
        generated_content,
    )

    assert merged_content == generated_content


def test_merge_preserves_header_and_footer_outside_markers():

    generated_content = _generate()

    custom_header = "# FT_11_11_11_11.some_topic.md"
    custom_footer = "# trailing note"

    existing_content = "\n".join(
        [
            "#!/usr/bin/env python3",
            custom_header,
            generated_content.rstrip("\n"),
            custom_footer,
            "",
        ]
    )

    merged_content = merge_entry_script_content(existing_content, generated_content)

    assert custom_header in merged_content
    assert custom_footer in merged_content
    assert ConfConstGeneral.entry_script_boilerplate_begin_marker in merged_content
    assert ConfConstGeneral.entry_script_boilerplate_end_marker in merged_content

    # Merging an already-consistent file is idempotent:
    assert merge_entry_script_content(merged_content, generated_content) == merged_content


def test_merge_replaces_stale_marked_region():

    stale_generated_content = generate_entry_script_content(
        EntryFunc.func_boot_env.value,
        "/dummy/path/proto_kernel.py",
        "/dummy/path/entry.py",
        "old_module",
        "old_func",
    )
    custom_header = "# a hand-written header comment"
    existing_content = "\n".join(
        [
            "#!/usr/bin/env python3",
            custom_header,
            stale_generated_content.rstrip("\n"),
            "",
        ]
    )

    fresh_generated_content = _generate()

    merged_content = merge_entry_script_content(existing_content, fresh_generated_content)

    assert custom_header in merged_content
    assert "old_module:old_func" not in merged_content
    assert "my_module:my_func" in merged_content
