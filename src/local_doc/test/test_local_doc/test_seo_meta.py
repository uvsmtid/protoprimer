from __future__ import annotations

from collections import Counter
from pathlib import Path

import pytest

from local_test.repo_tree import change_to_known_repo_path
from test_local_doc.doc_verifier import (
    assert_meta_description_valid,
    assert_seo_title_valid,
    parse_meta_description,
    parse_seo_title,
)

# Pages reachable from the side menu (see `doc/index.md` and nested `toctree`-s)
# plus the indexed `orphan` page (`faq.md`):
_side_menu_page_names = [
    "intro.md",
    "background_why_proto.md",
    "background_why_primer.md",
    "background_why_not_shell.md",
    "background_why_not_uv.md",
    "tutorial_overview.md",
    "tutorial_init_flat_repo.md",
    "tutorial_boot_env.md",
    "tutorial_form_nested_repo.md",
    "tutorial_start_app.md",
    "tutorial_clean_repo_root.md",
    "tutorial_enable_updates.md",
    "config.md",
    "reference.md",
    "dictionary.md",
    "alternative.md",
    "faq.md",
]

with change_to_known_repo_path():
    _side_menu_pages = [Path("doc").resolve() / page_name for page_name in _side_menu_page_names]

_min_description_len = 80
_max_description_len = 160
_max_seo_title_len = 60


@pytest.mark.parametrize(
    "file_path",
    _side_menu_pages,
    ids=[doc_file.name for doc_file in _side_menu_pages],
)
def test_meta_description_valid(file_path: Path) -> None:
    assert_meta_description_valid(
        file_path,
        _min_description_len,
        _max_description_len,
    )


@pytest.mark.parametrize(
    "file_path",
    _side_menu_pages,
    ids=[doc_file.name for doc_file in _side_menu_pages],
)
def test_seo_title_valid(file_path: Path) -> None:
    assert_seo_title_valid(
        file_path,
        _max_seo_title_len,
    )


def test_meta_descriptions_unique() -> None:
    description_counts = Counter(parse_meta_description(file_path) for file_path in _side_menu_pages)
    duplicates = [description for description, count in description_counts.items() if count > 1]
    assert not duplicates


def test_seo_titles_unique() -> None:
    title_counts = Counter(parse_seo_title(file_path) for file_path in _side_menu_pages)
    duplicates = [seo_title for seo_title, count in title_counts.items() if count > 1]
    assert not duplicates


def test_side_menu_pages_exist() -> None:
    missing_pages = [file_path.name for file_path in _side_menu_pages if not file_path.is_file()]
    assert not missing_pages
