"""Confluence label management."""

from __future__ import annotations

from typing import Any

from shruggery.client import get_client
from shruggery.server import mcp


@mcp.tool()
async def get_confluence_labels(
    page_id: str,
    limit: int = 25,
    cursor: str | None = None,
) -> str:
    """Get labels on a Confluence page.

    Args:
        page_id: Page ID.
        limit: Max results.
        cursor: Pagination cursor.
    """
    params: dict[str, Any] = {"limit": limit}
    if cursor:
        params["cursor"] = cursor
    return await get_client().confluence_get(
        f"pages/{page_id}/labels", params=params
    )


@mcp.tool()
async def add_confluence_labels(page_id: str, labels: list[str]) -> str:
    """Add labels to a Confluence page.

    Args:
        page_id: Page ID.
        labels: List of label names to add.
    """
    # v1 API for label management
    body = [{"prefix": "global", "name": label} for label in labels]
    return await get_client().confluence_v1_post(
        f"content/{page_id}/label", body=body
    )


@mcp.tool()
async def remove_confluence_label(page_id: str, label: str) -> str:
    """Remove a label from a Confluence page.

    Args:
        page_id: Page ID.
        label: Label name to remove.
    """
    client = get_client()
    return await client._ok_or_error(
        "DELETE",
        f"{client.settings.confluence_v1_base}/content/{page_id}/label/{label}",
    )
