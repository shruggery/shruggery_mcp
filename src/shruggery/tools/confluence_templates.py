"""Confluence page templates."""

from __future__ import annotations

from typing import Any

from shruggery.client import get_client
from shruggery.server import mcp


@mcp.tool()
async def get_confluence_templates(
    space_key: str | None = None,
    start: int = 0,
    limit: int = 25,
) -> str:
    """List Confluence page templates.

    Args:
        space_key: Space key to filter templates. Omit for global/blueprint templates.
        start: Pagination offset.
        limit: Max results.
    """
    params: dict[str, Any] = {"start": start, "limit": limit}
    if space_key:
        # Space templates via v1 API
        return await get_client().confluence_v1_get(
            f"space/{space_key}/template", params=params
        )
    # Global/blueprint templates
    return await get_client().confluence_v1_get("template/blueprint", params=params)
