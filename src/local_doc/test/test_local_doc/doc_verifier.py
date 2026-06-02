from __future__ import annotations

import re
from pathlib import Path

_doc_id_filename_re = re.compile(r"^[A-Za-z]+(_\d+)+\.[^.]+\.md$")
_link_def_re = re.compile(r"^\[([^\]]+)\]:\s+(\S+)")
_inline_link_re = re.compile(r"\[([^\]]+)\]\[([^\]]+)\]")


def parse_frontmatter(file_path: Path) -> dict[str, str]:
    file_lines = file_path.read_text().splitlines()
    if not file_lines or file_lines[0].strip() != "---":
        return {}
    header_end = next(
        (line_idx for line_idx in range(1, len(file_lines)) if file_lines[line_idx].strip() == "---"),
        None,
    )
    if header_end is None:
        return {}
    header_dict: dict[str, str] = {}
    for header_line in file_lines[1:header_end]:
        if ":" in header_line:
            field_key, _, field_value = header_line.partition(":")
            header_dict[field_key.strip()] = field_value.strip()
    return header_dict


def assert_has_yaml_header(file_path: Path) -> None:
    file_lines = file_path.read_text().splitlines()
    header_end = next(
        (line_idx for line_idx in range(1, len(file_lines)) if file_lines[line_idx].strip() == "---"),
        None,
    )
    assert file_lines and file_lines[0].strip() == "---"
    assert header_end is not None


def assert_id_matches_filename(file_path: Path, id_key: str) -> None:
    front_matter = parse_frontmatter(file_path)
    expected_id = file_path.stem.split(".")[0]
    actual_id = front_matter.get(id_key)
    assert actual_id == expected_id


def assert_status_valid(file_path: Path, status_key: str, valid_statuses: set[str]) -> None:
    front_matter = parse_frontmatter(file_path)
    actual_status = front_matter.get(status_key)
    assert actual_status in valid_statuses


def assert_h1_title_matches_filename(file_path: Path) -> None:
    expected_h1 = f"# {file_path.stem}"
    file_lines = file_path.read_text().splitlines()
    assert any(line.strip() == expected_h1 for line in file_lines)


def assert_title_slug_matches_filename(file_path: Path, title_key: str) -> None:
    front_matter = parse_frontmatter(file_path)
    title_value = front_matter.get(title_key, "")
    name_slug = file_path.stem.split(".", 1)[-1]
    assert title_value == name_slug


def assert_doc_id_link_labels_match_basename(file_path: Path) -> None:
    mismatches: list[tuple[str, str]] = []
    for line in file_path.read_text().splitlines():
        line_match = _link_def_re.match(line.strip())
        if not line_match:
            continue
        label, target = line_match.group(1), line_match.group(2)
        basename = Path(target).name
        if not _doc_id_filename_re.match(basename):
            continue
        if label != basename:
            mismatches.append((label, basename))
    if mismatches:
        raise AssertionError(f"Link label != basename: {mismatches}")


def assert_doc_id_link_captions_are_slug(file_path: Path) -> None:
    violations: list[tuple[str, str, str]] = []
    for line in file_path.read_text().splitlines():
        stripped_line = line.strip()
        if _link_def_re.match(stripped_line):
            continue
        for inline_match in _inline_link_re.finditer(stripped_line):
            caption, ref_id = inline_match.group(1), inline_match.group(2)
            basename = Path(ref_id).name
            if not _doc_id_filename_re.match(basename):
                continue
            expected_slug = Path(basename).stem.split(".", 1)[-1]
            if caption != expected_slug:
                violations.append(
                    (
                        caption,
                        ref_id,
                        expected_slug,
                    )
                )
    if violations:
        raise AssertionError(f"Link caption should be slug: {violations}")


def assert_title_tokens_in_title(file_path: Path, title_key: str) -> None:
    front_matter = parse_frontmatter(file_path)
    title_lower = front_matter.get(
        title_key,
        "",
    ).lower()
    stem_parts = file_path.stem.split(
        ".",
        1,
    )
    name_slug = stem_parts[-1] if len(stem_parts) > 1 else ""
    name_tokens = [name_token.lower() for name_token in name_slug.split("_") if name_token]
    missing_tokens = [name_token for name_token in name_tokens if name_token not in title_lower]
    assert not missing_tokens
