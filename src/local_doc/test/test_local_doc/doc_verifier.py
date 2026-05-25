from __future__ import annotations

from pathlib import Path


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
