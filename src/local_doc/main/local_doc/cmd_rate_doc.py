from __future__ import annotations

import logging
import subprocess
from pathlib import Path

from local_doc.common_func import list_doc_files

logger = logging.getLogger(__name__)

rated_doc_dirs: list[str] = [
    "doc/feature_topic",
    "doc/use_case",
]


def rate_doc() -> None:
    """
    Main func to list all docs from `rated_doc_dirs` ordered by their last git-commit date.
    """

    dated_doc_files: list[tuple[str, Path]] = []

    for rated_doc_dir in rated_doc_dirs:
        doc_dir_path = Path(rated_doc_dir).resolve()
        if not doc_dir_path.is_dir():
            logger.warning(f"Directory not found at {doc_dir_path}")
            continue
        for doc_file_path in list_doc_files(doc_dir_path):
            last_updated_date = get_last_updated_date(doc_file_path)
            if last_updated_date is None:
                logger.warning(f"No git history found for {doc_file_path}")
                continue
            dated_doc_files.append((last_updated_date, doc_file_path))

    dated_doc_files.sort(key=lambda dated_doc_file: (dated_doc_file[0], dated_doc_file[1]))

    for last_updated_date, doc_file_path in dated_doc_files:
        print(f"{last_updated_date} {doc_file_path.relative_to(Path.cwd())}")


def get_last_updated_date(doc_file_path: Path) -> str | None:
    """
    Finds the date (`YYYY-MM-DD`) of the latest git commit which touched `doc_file_path`.

    Returns:
        The date string, or `None` if the file has no git history (e.g., not yet committed).
    """
    completed_process = subprocess.run(
        [
            "git",
            "log",
            "-1",
            "--format=%cd",
            "--date=format:%Y-%m-%d",
            "--",
            str(doc_file_path),
        ],
        cwd=doc_file_path.parent,
        capture_output=True,
        text=True,
        check=True,
    )

    last_updated_date = completed_process.stdout.strip()
    if not last_updated_date:
        return None
    return last_updated_date


if __name__ == "__main__":
    rate_doc()
