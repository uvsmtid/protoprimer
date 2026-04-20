from __future__ import annotations

from pathlib import Path


def list_doc_files(doc_dir: Path) -> list[Path]:
    return sorted(
        #
        doc_path
        for doc_path in doc_dir.iterdir()
        if doc_path.suffix == ".md" and doc_path.is_file()
    )
