"""AWS Lambda handler for POST /calculate (API Gateway HTTP API, payload format 2.0).

Stateless: parse JSON -> validate -> call the shared calculator -> return JSON.
"""
from __future__ import annotations

import base64
import json
from typing import Any

from .calculator import ValidationError, result_from_payload

MAX_BODY_BYTES = 4_096
_HEADERS = {"Content-Type": "application/json"}


def _response(status: int, body: dict[str, Any]) -> dict[str, Any]:
    return {"statusCode": status, "headers": _HEADERS, "body": json.dumps(body)}


def _error(status: int, message: str, details: list[str] | None = None) -> dict[str, Any]:
    body: dict[str, Any] = {"error": message}
    if details:
        body["details"] = details
    return _response(status, body)


def _reject_constant(name: str) -> None:
    """json.loads would otherwise accept NaN / Infinity; reject them."""
    raise ValueError(f"Invalid JSON constant: {name}")


def lambda_handler(event: Any, context: Any = None) -> dict[str, Any]:
    if not isinstance(event, dict):
        return _error(400, "Malformed request.")

    raw = event.get("body")
    if raw is None or raw == "":
        return _error(400, "Request body is required.")
    if not isinstance(raw, str):
        return _error(400, "Request body must be a JSON string.")

    if event.get("isBase64Encoded"):
        try:
            raw = base64.b64decode(raw, validate=True).decode("utf-8")
        except (ValueError, UnicodeDecodeError):
            return _error(400, "Request body is not valid base64-encoded UTF-8.")

    if len(raw.encode("utf-8")) > MAX_BODY_BYTES:
        return _error(413, "Request body is too large.")

    try:
        payload = json.loads(raw, parse_constant=_reject_constant)
    except (ValueError, RecursionError):
        return _error(400, "Request body is not valid JSON.")

    if not isinstance(payload, dict):
        return _error(400, "Request body must be a JSON object.")

    missing = [k for k in ("roof_area_m2", "rainfall_mm", "efficiency_percent") if k not in payload]
    if missing:
        return _error(400, "Missing required fields.", [f"Missing: {k}" for k in missing])

    try:
        result = result_from_payload(payload)
    except ValidationError as exc:
        return _error(400, "Invalid input.", exc.errors)

    return _response(200, result)
