"""Main publisher entry point for the Pinterest MVP."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

from src.config import (
    CONTENT_QUEUE_DIR,
    FAILED_DIR,
    MAX_PINS_PER_RUN,
    POSTED_DIR,
    setup_logging,
)
from src.pinterest_client import create_pin
from src.queue_reader import list_post_folders
from src.utils import (
    append_csv_row,
    ensure_directories,
    has_posted_folder,
    is_scheduled_today_or_earlier,
    load_yaml_file,
    move_folder,
)

logger = logging.getLogger("publisher")


def publish_post(folder: Path) -> bool:
    """Publish one queued post folder, returning whether an API call was made."""
    metadata_path = folder / "metadata.yaml"
    if not metadata_path.exists():
        raise FileNotFoundError(f"Missing metadata.yaml in {folder.name}")

    metadata = load_yaml_file(metadata_path)
    status = str(metadata.get("status", "")).strip().lower()
    if status != "pending":
        logger.info("Skipping %s because status is %s", folder.name, status or "missing")
        return False

    scheduled_date = str(metadata.get("scheduled_date", "")).strip()
    if not scheduled_date:
        raise ValueError("Missing scheduled_date in metadata.yaml.")
    if not is_scheduled_today_or_earlier(scheduled_date):
        logger.info("Skipping %s because scheduled_date is in the future", folder.name)
        return False

    if has_posted_folder(folder.name):
        logger.warning(
            "Skipping Pinterest API call for %s because it is already in the posted log.",
            folder.name,
        )
        move_folder(folder, POSTED_DIR / folder.name)
        return False

    image_url = str(metadata.get("image_url", "")).strip()
    image_file = metadata.get("image_file")
    if not image_url:
        if image_file:
            raise ValueError(
                "V1 requires image_url in metadata.yaml. Local image_file upload is not supported yet. "
                "Add a public image_url or use V2 automatic hosting."
            )
        raise ValueError("Missing image_url in metadata.yaml. V1 requires a public image URL.")

    board_id = str(metadata.get("board_id", "")).strip()
    title = str(metadata.get("title", folder.name))
    description = str(metadata.get("description", ""))
    link = str(metadata.get("link", ""))
    alt_text = str(metadata.get("alt_text", ""))

    if not board_id:
        raise ValueError("Missing board_id in metadata.yaml.")

    if (POSTED_DIR / folder.name).exists():
        raise FileExistsError(
            f"Destination already exists in posted/: {folder.name}. "
            "The Pinterest API call was not made."
        )

    pin = create_pin(board_id, image_url, title, description, link, alt_text)
    pin_id = str(pin.get("id", ""))
    response_status = str(pin.get("_http_status", "success"))
    append_csv_row(
        post_folder=folder.name,
        title=title,
        board_id=board_id,
        pin_id=pin_id,
        posted_at=datetime.now(timezone.utc).isoformat(),
        status=response_status,
    )
    move_folder(folder, POSTED_DIR / folder.name)
    logger.info("Posted %s to Pinterest (pin_id=%s)", folder.name, pin_id)
    return True


def main() -> None:
    """Run one batch of queued Pinterest posts."""
    setup_logging()
    ensure_directories(CONTENT_QUEUE_DIR, POSTED_DIR, FAILED_DIR)

    folders = list_post_folders(CONTENT_QUEUE_DIR)
    attempts = 0

    for folder in folders:
        if attempts >= MAX_PINS_PER_RUN:
            logger.info("Reached MAX_PINS_PER_RUN=%s; stopping.", MAX_PINS_PER_RUN)
            break

        try:
            if publish_post(folder):
                attempts += 1
        except Exception:
            attempts += 1
            logger.exception("Failed to publish %s", folder.name)
            try:
                move_folder(folder, FAILED_DIR / folder.name)
            except FileExistsError:
                logger.warning("Destination already exists for %s; leaving folder in place.", folder.name)
            except OSError as move_error:
                logger.error("Could not move %s to failed/: %s", folder.name, move_error)


if __name__ == "__main__":
    main()
