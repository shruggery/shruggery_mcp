"""Confluence CQL search."""

from __future__ import annotations

from shruggery.client import get_client
from shruggery.server import mcp


@mcp.tool()
async def search_confluence_cql(
    cql: str,
    limit: int = 25,
    cursor: str | None = None,
) -> str:
    """Search Confluence using CQL (Confluence Query Language).

    Args:
        cql: CQL query string (e.g. 'type=page AND space.key="DEV"').
        limit: Max results.
        cursor: Pagination cursor.
    """
    params: dict = {"cql": cql, "limit": limit}
    if cursor:
        params["cursor"] = cursor
    # CQL search is still on v1 API
    return await get_client().confluence_v1_get("search", params=params)
