"""Confluence page CRUD, versions, history."""

from __future__ import annotations

from typing import Any

from shruggery.client import get_client
from shruggery.server import mcp


@mcp.tool()
async def get_confluence_page(
    page_id: str,
    body_format: str = "storage",
    include_body: bool = True,
) -> str:
    """Get a Confluence page by ID.

    Args:
        page_id: Page ID.
        body_format: Body format — "storage", "atlas_doc_format", or "view".
        include_body: Whether to include the page body.
    """
    params: dict[str, str] = {}
    if include_body:
        params["body-format"] = body_format
    return await get_client().confluence_get(f"pages/{page_id}", params=params)


@mcp.tool()
async def get_confluence_pages(
    space_id: str | None = None,
    title: str | None = None,
    status: str = "current",
    limit: int = 25,
    cursor: str | None = None,
) -> str:
    """List Confluence pages, optionally filtered.

    Args:
        space_id: Filter by space ID.
        title: Filter by exact title.
        status: Page status — "current", "draft", "trashed".
        limit: Max results per page.
        cursor: Pagination cursor from previous response.
    """
    params: dict[str, Any] = {"status": status, "limit": limit}
    if space_id:
        params["space-id"] = space_id
    if title:
        params["title"] = title
    if cursor:
        params["cursor"] = cursor
    return await get_client().confluence_get("pages", params=params)


@mcp.tool()
async def create_confluence_page(
    space_id: str,
    title: str,
    body: str,
    body_format: str = "storage",
    parent_id: str | None = None,
    status: str = "current",
) -> str:
    """Create a Confluence page.

    Args:
        space_id: Space ID to create the page in.
        title: Page title.
        body: Page body content.
        body_format: Body format — "storage" (XHTML) or "atlas_doc_format" (ADF JSON).
        parent_id: Optional parent page ID.
        status: "current" (published) or "draft".
    """
    payload: dict[str, Any] = {
        "spaceId": space_id,
        "status": status,
        "title": title,
        "body": {
            "representation": body_format,
            "value": body,
        },
    }
    if parent_id:
        payload["parentId"] = parent_id
    return await get_client().confluence_post("pages", body=payload)


@mcp.tool()
async def update_confluence_page(
    page_id: str,
    title: str,
    body: str,
    version_number: int,
    body_format: str = "storage",
    status: str = "current",
    version_message: str | None = None,
) -> str:
    """Update a Confluence page.

    Args:
        page_id: Page ID.
        title: New page title.
        body: New page body content.
        version_number: New version number (must be current + 1).
        body_format: Body format — "storage" or "atlas_doc_format".
        status: "current" or "draft".
        version_message: Optional version change message.
    """
    version: dict[str, Any] = {"number": version_number}
    if version_message:
        version["message"] = version_message

    payload: dict[str, Any] = {
        "id": page_id,
        "status": status,
        "title": title,
        "body": {
            "representation": body_format,
            "value": body,
        },
        "version": version,
    }
    return await get_client().confluence_put(f"pages/{page_id}", body=payload)


@mcp.tool()
async def delete_confluence_page(page_id: str) -> str:
    """Delete a Confluence page (moves to trash).

    Args:
        page_id: Page ID.
    """
    return await get_client().confluence_delete(f"pages/{page_id}")


@mcp.tool()
async def get_confluence_page_versions(
    page_id: str, limit: int = 25, cursor: str | None = None
) -> str:
    """Get version history of a Confluence page.

    Args:
        page_id: Page ID.
        limit: Max versions to return.
        cursor: Pagination cursor.
    """
    params: dict[str, Any] = {"limit": limit}
    if cursor:
        params["cursor"] = cursor
    return await get_client().confluence_get(f"pages/{page_id}/versions", params=params)


@mcp.tool()
async def get_confluence_page_by_title(
    space_id: str, title: str, body_format: str = "storage"
) -> str:
    """Find a Confluence page by exact title within a space.

    Args:
        space_id: Space ID to search in.
        title: Exact page title.
        body_format: Body format for results.
    """
    params: dict[str, Any] = {
        "space-id": space_id,
        "title": title,
        "body-format": body_format,
        "limit": 1,
    }
    return await get_client().confluence_get("pages", params=params)
