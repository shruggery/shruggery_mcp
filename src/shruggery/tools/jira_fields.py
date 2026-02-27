"""Jira field metadata."""

from __future__ import annotations

from shruggery.client import get_client
from shruggery.server import mcp


@mcp.tool()
async def get_jira_fields() -> str:
    """Get all Jira fields (system + custom). Useful for finding custom field IDs."""
    return await get_client().jira_get("field")
