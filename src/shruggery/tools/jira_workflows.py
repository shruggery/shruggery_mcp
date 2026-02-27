"""Jira workflow metadata."""

from __future__ import annotations

from shruggery.client import get_client
from shruggery.server import mcp


@mcp.tool()
async def get_jira_workflows() -> str:
    """Get all Jira workflows visible to the authenticated user."""
    return await get_client().jira_get("workflow")
