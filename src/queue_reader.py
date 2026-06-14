"""Helpers for scanning the local content queue."""

from __future__ import annotations

from pathlib import Path

from src.config import CONTENT_QUEUE_DIR


def list_post_folders(queue_dir: Path = CONTENT_QUEUE_DIR) -> list[Path]:
    """Return all subfolders in the content queue directory."""
    if not queue_dir.exists():
        return []
    return sorted(
        [path for path in queue_dir.iterdir() if path.is_dir()],
        key=lambda item: item.name,
    )
