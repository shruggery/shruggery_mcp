"""Confluence page comments — footer and inline."""

from __future__ import annotations

from typing import Any

from shruggery.client import get_client
from shruggery.server import mcp


@mcp.tool()
async def get_confluence_comments(
    page_id: str,
    limit: int = 25,
    cursor: str | None = None,
    body_format: str = "storage",
) -> str:
    """Get footer comments on a Confluence page.

    Args:
        page_id: Page ID.
        limit: Max comments.
        cursor: Pagination cursor.
        body_format: Body format for comment bodies.
    """
    params: dict[str, Any] = {"limit": limit, "body-format": body_format}
    if cursor:
        params["cursor"] = cursor
    return await get_client().confluence_get(
        f"pages/{page_id}/footer-comments", params=params
    )


@mcp.tool()
async def get_confluence_inline_comments(
    page_id: str,
    limit: int = 25,
    cursor: str | None = None,
    body_format: str = "storage",
) -> str:
    """Get inline comments on a Confluence page.

    Args:
        page_id: Page ID.
        limit: Max comments.
        cursor: Pagination cursor.
        body_format: Body format for comment bodies.
    """
    params: dict[str, Any] = {"limit": limit, "body-format": body_format}
    if cursor:
        params["cursor"] = cursor
    return await get_client().confluence_get(
        f"pages/{page_id}/inline-comments", params=params
    )


@mcp.tool()
async def create_confluence_comment(
    page_id: str,
    body: str,
    body_format: str = "storage",
) -> str:
    """Add a footer comment to a Confluence page.

    Args:
        page_id: Page ID.
        body: Comment body content.
        body_format: Body format — "storage" or "atlas_doc_format".
    """
    payload = {
        "pageId": page_id,
        "body": {
            "representation": body_format,
            "value": body,
        },
    }
    return await get_client().confluence_post("footer-comments", body=payload)


@mcp.tool()
async def create_confluence_inline_comment(
    page_id: str,
    body: str,
    inline_marker: str,
    body_format: str = "storage",
) -> str:
    """Add an inline comment to a Confluence page.

    Args:
        page_id: Page ID.
        body: Comment body content.
        inline_marker: Text to anchor the inline comment to.
        body_format: Body format.
    """
    payload = {
        "pageId": page_id,
        "body": {
            "representation": body_format,
            "value": body,
        },
        "inlineProperties": {
            "textSelection": inline_marker,
        },
    }
    return await get_client().confluence_post("inline-comments", body=payload)


@mcp.tool()
async def delete_confluence_comment(comment_id: str) -> str:
    """Delete a Confluence comment (footer or inline).

    Args:
        comment_id: Comment ID.
    """
    return await get_client().confluence_delete(f"comments/{comment_id}")
