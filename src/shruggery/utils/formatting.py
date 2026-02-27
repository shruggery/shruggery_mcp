"""Response formatting and content truncation."""

from __future__ import annotations

import json
from typing import Any

MAX_RESPONSE_LEN = 80_000


def fmt(data: Any) -> str:
    """Format API response data as indented JSON string, truncated if needed."""
    text = json.dumps(data, indent=2, default=str)
    if len(text) > MAX_RESPONSE_LEN:
        return text[:MAX_RESPONSE_LEN] + "\n... (truncated)"
    return text


def error_msg(status: int, body: Any) -> str:
    """Format an error response."""
    return json.dumps({"error": True, "status": status, "detail": body}, indent=2, default=str)
