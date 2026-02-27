"""Confluence content properties."""

from __future__ import annotations

from typing import Any

from shruggery.client import get_client
from shruggery.server import mcp


@mcp.tool()
async def get_confluence_properties(page_id: str) -> str:
    """Get all content properties on a Confluence page.

    Args:
        page_id: Page ID.
    """
    return await get_client().confluence_v1_get(
        f"content/{page_id}/property"
    )


@mcp.tool()
async def set_confluence_property(
    page_id: str,
    key: str,
    value: Any,
    version_number: int | None = None,
) -> str:
    """Set a content property on a Confluence page.

    Args:
        page_id: Page ID.
        key: Property key.
        value: Property value (any JSON-serializable value).
        version_number: Version number for update (required if property already exists; current + 1).
    """
    body: dict[str, Any] = {"key": key, "value": value}
    if version_number is not None:
        body["version"] = {"number": version_number}
    # POST to create, PUT to update — we try PUT first, fall back to POST
    client = get_client()
    result = await client._ok_or_error(
        "PUT",
        f"{client.settings.confluence_v1_base}/content/{page_id}/property/{key}",
        json_body=body,
    )
    return result


@mcp.tool()
async def delete_confluence_property(page_id: str, key: str) -> str:
    """Delete a content property from a Confluence page.

    Args:
        page_id: Page ID.
        key: Property key.
    """
    client = get_client()
    return await client._ok_or_error(
        "DELETE",
        f"{client.settings.confluence_v1_base}/content/{page_id}/property/{key}",
    )
