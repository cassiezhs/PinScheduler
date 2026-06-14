"""Application configuration and environment helpers."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
CONTENT_QUEUE_DIR = BASE_DIR / "content_queue"
POSTED_DIR = BASE_DIR / "posted"
FAILED_DIR = BASE_DIR / "failed"
LOGS_DIR = BASE_DIR / "logs"
POSTED_PINS_CSV = LOGS_DIR / "posted_pins.csv"
ERRORS_LOG = LOGS_DIR / "errors.log"

PINTEREST_ACCESS_TOKEN = os.getenv("PINTEREST_ACCESS_TOKEN", "").strip()


def _positive_int_from_env(name: str, default: int) -> int:
    """Read a positive integer environment variable."""
    raw_value = os.getenv(name, "").strip() or str(default)
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise ValueError(f"{name} must be a positive integer.") from exc
    if value < 1:
        raise ValueError(f"{name} must be a positive integer.")
    return value


MAX_PINS_PER_RUN = _positive_int_from_env("MAX_PINS_PER_RUN", 3)


def setup_logging() -> None:
    """Configure a simple logger for the application."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    error_handler = logging.FileHandler(ERRORS_LOG, mode="a", encoding="utf-8")
    error_handler.setLevel(logging.ERROR)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            error_handler,
        ],
    )
