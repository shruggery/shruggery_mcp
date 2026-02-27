"""Jira saved filters."""

from __future__ import annotations

from shruggery.client import get_client
from shruggery.server import mcp


@mcp.tool()
async def get_jira_filter(filter_id: str, expand: str | None = None) -> str:
    """Get a Jira saved filter by ID.

    Args:
        filter_id: Filter ID.
        expand: Comma-separated expansions (e.g. "jql,description").
    """
    params: dict = {}
    if expand:
        params["expand"] = expand
    return await get_client().jira_get(f"filter/{filter_id}", params=params)


@mcp.tool()
async def get_jira_favorite_filters(expand: str | None = None) -> str:
    """Get the authenticated user's favorite Jira filters.

    Args:
        expand: Comma-separated expansions.
    """
    params: dict = {}
    if expand:
        params["expand"] = expand
    return await get_client().jira_get("filter/favourite", params=params)


@mcp.tool()
async def create_jira_filter(
    name: str,
    jql: str,
    description: str | None = None,
    favourite: bool = False,
) -> str:
    """Create a new saved Jira filter.

    Args:
        name: Filter name.
        jql: JQL query string.
        description: Optional description.
        favourite: Whether to mark as favourite.
    """
    body: dict = {"name": name, "jql": jql, "favourite": favourite}
    if description:
        body["description"] = description
    return await get_client().jira_post("filter", body=body)
