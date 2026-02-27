"""Jira user lookup and group membership."""

from __future__ import annotations

from shruggery.client import get_client
from shruggery.server import mcp


@mcp.tool()
async def find_jira_users(
    query: str, start_at: int = 0, max_results: int = 50
) -> str:
    """Search for Jira users by name or email.

    Args:
        query: Search string (name, email, display name).
        start_at: Pagination offset.
        max_results: Max results.
    """
    return await get_client().jira_get(
        "user/search",
        params={"query": query, "startAt": start_at, "maxResults": max_results},
    )


@mcp.tool()
async def get_jira_user(account_id: str) -> str:
    """Get a Jira user by account ID.

    Args:
        account_id: Atlassian account ID.
    """
    return await get_client().jira_get(
        "user", params={"accountId": account_id}
    )


@mcp.tool()
async def get_jira_user_groups(account_id: str) -> str:
    """Get groups a Jira user belongs to.

    Args:
        account_id: Atlassian account ID.
    """
    return await get_client().jira_get(
        "user/groups", params={"accountId": account_id}
    )
