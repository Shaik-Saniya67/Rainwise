"""Tiny stdlib HTTP client for AWS mode. Makes a real POST to RAINWISE_API_URL."""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

REQUIRED_KEYS = ("harvestable_litres", "harvestable_kl", "recommended_tank_litres", "message")


class ApiError(Exception):
    """The AWS API call failed or returned something unusable."""


def _is_number(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def call_api(url: str, payload: dict[str, float], timeout: float = 10.0) -> dict[str, Any]:
    if not url.lower().startswith(("http://", "https://")):
        raise ApiError("RAINWISE_API_URL must start with http:// or https://")

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 (scheme checked above)
            raw = response.read()
    except urllib.error.HTTPError as exc:
        detail = ""
        try:
            body = json.loads(exc.read().decode("utf-8", errors="replace"))
            detail = " ".join([str(body.get("error", ""))] + [str(d) for d in body.get("details", [])]).strip()
        except (ValueError, AttributeError):
            pass
        raise ApiError(f"The API answered with HTTP {exc.code}. {detail}".strip()) from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise ApiError(f"Could not reach the API ({getattr(exc, 'reason', exc)}).") from exc

    try:
        data = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as exc:
        raise ApiError("The API returned a response that is not valid JSON.") from exc

    if not isinstance(data, dict) or any(k not in data for k in REQUIRED_KEYS):
        raise ApiError("The API response is missing expected fields.")
    tank = data["recommended_tank_litres"]
    if not (_is_number(data["harvestable_litres"]) and _is_number(data["harvestable_kl"])) or not (
        tank is None or _is_number(tank)
    ):
        raise ApiError("The API response has unexpected value types.")
    return data
