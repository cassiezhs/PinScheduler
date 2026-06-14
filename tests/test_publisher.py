"""Focused tests for queue eligibility and publishing behavior."""

from __future__ import annotations

import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

from src.publisher import main, publish_post


class PublishPostTests(unittest.TestCase):
    """Test one-folder publishing behavior without calling Pinterest."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.queue = self.root / "content_queue"
        self.posted = self.root / "posted"
        self.queue.mkdir()
        self.posted.mkdir()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def make_post(self, name: str, metadata: str) -> Path:
        """Create a queued post folder with metadata."""
        folder = self.queue / name
        folder.mkdir()
        (folder / "metadata.yaml").write_text(metadata, encoding="utf-8")
        return folder

    def test_future_post_is_skipped_without_api_call(self) -> None:
        future = (date.today() + timedelta(days=1)).isoformat()
        folder = self.make_post(
            "future",
            f"status: pending\nscheduled_date: {future}\nimage_url: https://example.com/a.jpg\n",
        )

        with patch("src.publisher.create_pin") as create_pin:
            self.assertFalse(publish_post(folder))

        create_pin.assert_not_called()
        self.assertTrue(folder.exists())

    def test_local_image_only_raises_clear_error(self) -> None:
        folder = self.make_post(
            "local",
            f"status: pending\nscheduled_date: {date.today().isoformat()}\n"
            "board_id: board\nimage_file: image.jpg\n",
        )

        with self.assertRaisesRegex(ValueError, "V1 requires image_url"):
            publish_post(folder)

    def test_success_is_logged_before_folder_is_moved(self) -> None:
        folder = self.make_post(
            "ready",
            f"status: pending\nscheduled_date: {date.today().isoformat()}\n"
            "board_id: board\nimage_url: https://example.com/a.jpg\n",
        )

        with (
            patch("src.publisher.POSTED_DIR", self.posted),
            patch("src.publisher.has_posted_folder", return_value=False),
            patch("src.publisher.create_pin", return_value={"id": "pin-1", "_http_status": 201}),
            patch("src.publisher.append_csv_row") as append_csv_row,
        ):
            self.assertTrue(publish_post(folder))

        self.assertFalse(folder.exists())
        self.assertTrue((self.posted / "ready").exists())
        append_csv_row.assert_called_once()
        self.assertEqual(append_csv_row.call_args.kwargs["status"], "201")

    def test_logged_post_is_moved_without_duplicate_api_call(self) -> None:
        folder = self.make_post(
            "recovered",
            f"status: pending\nscheduled_date: {date.today().isoformat()}\n",
        )

        with (
            patch("src.publisher.POSTED_DIR", self.posted),
            patch("src.publisher.has_posted_folder", return_value=True),
            patch("src.publisher.create_pin") as create_pin,
        ):
            self.assertFalse(publish_post(folder))

        create_pin.assert_not_called()
        self.assertTrue((self.posted / "recovered").exists())


class MainTests(unittest.TestCase):
    """Test batch-level limits."""

    def test_skipped_folder_does_not_consume_run_limit(self) -> None:
        folders = [Path("future"), Path("ready"), Path("extra")]

        with (
            patch("src.publisher.MAX_PINS_PER_RUN", 1),
            patch("src.publisher.setup_logging"),
            patch("src.publisher.ensure_directories"),
            patch("src.publisher.list_post_folders", return_value=folders),
            patch("src.publisher.publish_post", side_effect=[False, True]) as publish_post_mock,
        ):
            main()

        self.assertEqual(publish_post_mock.call_count, 2)


if __name__ == "__main__":
    unittest.main()
