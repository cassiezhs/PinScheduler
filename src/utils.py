"""Utility helpers for filesystem and logging operations."""

from __future__ import annotations

import csv
import shutil
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

from src.config import LOGS_DIR, POSTED_PINS_CSV


def ensure_directories(*paths: Path) -> None:
    """Create the given directories if they do not already exist."""
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def load_yaml_file(path: Path) -> dict[str, Any]:
    """Load YAML content from a file into a dictionary."""
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must contain a YAML mapping.")
    return data


def append_csv_row(
    post_folder: str,
    title: str,
    board_id: str,
    pin_id: str,
    posted_at: str,
    status: str,
) -> None:
    """Append a row to the posted pins CSV log."""
    ensure_directories(LOGS_DIR)
    file_exists = POSTED_PINS_CSV.exists()
    with POSTED_PINS_CSV.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        if not file_exists:
            writer.writerow(["post_folder", "title", "board_id", "pin_id", "posted_at", "status"])
        writer.writerow([post_folder, title, board_id, pin_id, posted_at, status])


def has_posted_folder(post_folder: str) -> bool:
    """Return whether a post folder is already recorded as successfully posted."""
    if not POSTED_PINS_CSV.exists():
        return False
    with POSTED_PINS_CSV.open("r", newline="", encoding="utf-8") as handle:
        return any(
            row.get("post_folder") == post_folder
            for row in csv.DictReader(handle)
        )


def move_folder(source: Path, destination: Path) -> None:
    """Move a folder to a new location safely."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise FileExistsError(f"Destination already exists: {destination}")
    shutil.move(str(source), str(destination))


def is_scheduled_today_or_earlier(scheduled_date: str) -> bool:
    """Return True when scheduled_date is today or earlier."""
    try:
        scheduled = datetime.strptime(scheduled_date, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError("scheduled_date must be in YYYY-MM-DD format.") from exc
    return scheduled <= date.today()
