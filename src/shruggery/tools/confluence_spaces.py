"""Confluence spaces."""

from __future__ import annotations

from typing import Any

from shruggery.client import get_client
from shruggery.server import mcp


@mcp.tool()
async def get_confluence_spaces(
    space_type: str | None = None,
    status: str | None = None,
    limit: int = 25,
    cursor: str | None = None,
) -> str:
    """List Confluence spaces.

    Args:
        space_type: Filter by type — "global" or "personal".
        status: Filter by status — "current" or "archived".
        limit: Max results.
        cursor: Pagination cursor.
    """
    params: dict[str, Any] = {"limit": limit}
    if space_type:
        params["type"] = space_type
    if status:
        params["status"] = status
    if cursor:
        params["cursor"] = cursor
    return await get_client().confluence_get("spaces", params=params)


@mcp.tool()
async def get_confluence_space(space_id: str) -> str:
    """Get a Confluence space by ID.

    Args:
        space_id: Space ID.
    """
    return await get_client().confluence_get(f"spaces/{space_id}")


@mcp.tool()
async def get_confluence_space_pages(
    space_id: str,
    status: str = "current",
    limit: int = 25,
    cursor: str | None = None,
    depth: str | None = None,
) -> str:
    """List pages in a Confluence space.

    Args:
        space_id: Space ID.
        status: Page status — "current", "draft", "trashed".
        limit: Max results.
        cursor: Pagination cursor.
        depth: Depth — "root" for top-level pages only, or "all".
    """
    params: dict[str, Any] = {"status": status, "limit": limit}
    if cursor:
        params["cursor"] = cursor
    if depth:
        params["depth"] = depth
    return await get_client().confluence_get(
        f"spaces/{space_id}/pages", params=params
    )
