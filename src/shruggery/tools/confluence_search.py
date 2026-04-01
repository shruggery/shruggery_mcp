"""Confluence CQL search."""

from __future__ import annotations

from shruggery.client import get_client
from shruggery.server import mcp


@mcp.tool()
async def search_confluence_cql(
    cql: str,
    limit: int = 15,
    cursor: str | None = None,
) -> str:
    """Search Confluence using CQL (Confluence Query Language).

    Returns up to 15 results per call. Use cursor for pagination.

    Args:
        cql: CQL query string (e.g. 'type=page AND space.key="DEV"').
        limit: Max results per page (default 15).
        cursor: Pagination cursor from previous response.
    """
    params: dict = {"cql": cql, "limit": limit}
    if cursor:
        params["cursor"] = cursor
    # CQL search is still on v1 API
    return await get_client().confluence_v1_get("search", params=params)
