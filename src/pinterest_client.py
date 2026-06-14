"""Pinterest API v5 integration helpers."""

from __future__ import annotations

from typing import Any

import requests

from src.config import PINTEREST_ACCESS_TOKEN

API_URL = "https://api.pinterest.com/v5/pins"


def create_pin(
    board_id: str,
    image_url: str,
    title: str,
    description: str,
    link: str,
    alt_text: str,
) -> dict[str, Any]:
    """Create a Pinterest pin using the Pinterest API v5."""
    if not PINTEREST_ACCESS_TOKEN:
        raise ValueError("PINTEREST_ACCESS_TOKEN is not set in the environment.")

    payload = {
        "board_id": board_id,
        "title": title,
        "description": description,
        "link": link,
        "alt_text": alt_text,
        "media_source": {
            "source_type": "image_url",
            "url": image_url,
        },
    }

    headers = {
        "Authorization": f"Bearer {PINTEREST_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
    except requests.HTTPError as exc:
        raise RuntimeError(
            f"Pinterest API request failed: HTTP {response.status_code} - {response.text}"
        ) from exc
    except requests.RequestException as exc:
        raise RuntimeError(f"Pinterest API request failed: {exc}") from exc

    try:
        response_data = response.json()
    except requests.exceptions.JSONDecodeError as exc:
        raise RuntimeError("Pinterest API returned an invalid JSON response.") from exc
    if not isinstance(response_data, dict):
        raise RuntimeError("Pinterest API returned an unexpected response.")

    response_data["_http_status"] = response.status_code
    return response_data
