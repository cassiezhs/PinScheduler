# PinScheduler

A simple folder-based Pinterest auto-publishing MVP.

## What it does

This project reads post folders from `content_queue/`, loads each folder's `metadata.yaml`, publishes eligible posts to Pinterest API v5, and then moves the post folder to `posted/` or `failed/`.

## Folder-based workflow

1. Create a new folder inside `content_queue/`.
2. Add one image file and one `metadata.yaml` file.
3. Run the publisher locally or through GitHub Actions.
4. The app will move completed folders to `posted/` and failed folders to `failed/`.

Use a unique post folder name for every pin. The folder name is recorded in `logs/posted_pins.csv` and used to prevent duplicate posting on reruns.

## Post folder format

Each post folder should contain:

- `image.jpg`
- `metadata.yaml`

Example `metadata.yaml`:

```yaml
title: "Gothic Library Rubber Stamp"
description: "A dark academia rubber stamp for junk journals, vintage notebooks, and witchy desk stationery."
link: "https://www.etsy.com/listing/example"
alt_text: "Gothic library rubber stamp displayed on a vintage writing desk"
board_id: "YOUR_PINTEREST_BOARD_ID"
scheduled_date: "2026-06-14"
status: "pending"
image_url: "https://example.com/image.jpg"
```

You may also use:

```yaml
image_file: "image.jpg"
```

V1 only supports `image_url`. Local image upload and automatic hosting are planned for V2.

## Local setup

1. Create a Python 3.11+ virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and set your values:

```bash
cp .env.example .env
```

4. Run the publisher:

```bash
python -m src.publisher
```

## GitHub Actions setup

1. Add the repository secret `PINTEREST_ACCESS_TOKEN` in GitHub Settings > Secrets and variables > Actions.
2. Add the repository secret `MAX_PINS_PER_RUN`. Set it to `3` unless you want a different daily limit.
3. The workflow in `.github/workflows/daily_pin.yml` runs once per day and executes the publisher.

## Scheduling daily posting

The included workflow uses `0 9 * * *`, which runs daily at 09:00 UTC, and can also be triggered manually from the Actions tab.

The workflow has `contents: write` permission and commits changes under `content_queue/`, `posted/`, `failed/`, and `logs/` after each run. This persists the success ledger and moved folders between temporary GitHub Actions runners. Repository rules must allow the workflow to push to the default branch.

## V2 roadmap

Future improvements include:

- OpenAI Vision caption generation
- automatic image hosting for local files
- local image upload support
- Etsy API integration
- SQLite tracking for more durable status history
- Instagram cross-posting
