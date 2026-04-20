from __future__ import annotations

from pathlib import Path

import pytest

from local_doc.common_func import list_doc_files
from local_test.repo_tree import change_to_known_repo_path

with change_to_known_repo_path():
    _ft_files = list_doc_files(Path("doc/feature_topic").resolve())

_valid_topic_statuses = {"TODO", "TEST", "DONE"}


def _parse_frontmatter(file_path: Path) -> dict[str, str]:
    file_lines = file_path.read_text().splitlines()
    if not file_lines or file_lines[0].strip() != "---":
        return {}
    header_end = next(
        (i for i in range(1, len(file_lines)) if file_lines[i].strip() == "---"),
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


@pytest.mark.parametrize(
    "file_path",
    _ft_files,
    ids=[doc_file.name for doc_file in _ft_files],
)
def test_has_yaml_header(file_path: Path) -> None:
    # given:
    file_lines = file_path.read_text().splitlines()

    # when:
    header_end = next(
        (i for i in range(1, len(file_lines)) if file_lines[i].strip() == "---"),
        None,
    )

    # then:
    assert file_lines and file_lines[0].strip() == "---"
    assert header_end is not None


@pytest.mark.parametrize(
    "file_path",
    _ft_files,
    ids=[doc_file.name for doc_file in _ft_files],
)
def test_feature_topic_id_matches_filename(file_path: Path) -> None:
    # given:
    front_matter = _parse_frontmatter(file_path)
    expected_id = file_path.stem.split(".")[0]

    # when:
    actual_id = front_matter.get("feature_topic")

    # then:
    assert actual_id == expected_id


@pytest.mark.parametrize(
    "file_path",
    _ft_files,
    ids=[doc_file.name for doc_file in _ft_files],
)
def test_topic_status_valid(file_path: Path) -> None:
    # given:
    front_matter = _parse_frontmatter(file_path)

    # when:
    actual_status = front_matter.get("topic_status")

    # then:
    assert actual_status in _valid_topic_statuses


@pytest.mark.parametrize(
    "file_path",
    _ft_files,
    ids=[doc_file.name for doc_file in _ft_files],
)
def test_topic_title_tokens_in_title(file_path: Path) -> None:
    # given:
    front_matter = _parse_frontmatter(file_path)
    title_lower = front_matter.get("topic_title", "").lower()
    stem_parts = file_path.stem.split(
        ".",
        1,
    )
    name_slug = stem_parts[-1] if len(stem_parts) > 1 else ""
    name_tokens = [name_token.lower() for name_token in name_slug.split("_") if name_token]

    # when:
    missing_tokens = [name_token for name_token in name_tokens if name_token not in title_lower]

    # then:
    assert not missing_tokens
