"""Jira watchers and votes."""

from __future__ import annotations

from shruggery.client import get_client
from shruggery.server import mcp


@mcp.tool()
async def get_jira_watchers(issue_key: str) -> str:
    """Get the list of watchers for a Jira issue.

    Args:
        issue_key: Issue key.
    """
    return await get_client().jira_get(f"issue/{issue_key}/watchers")


@mcp.tool()
async def add_jira_watcher(issue_key: str, account_id: str) -> str:
    """Add a watcher to a Jira issue.

    Args:
        issue_key: Issue key.
        account_id: Atlassian account ID of the user to add.
    """
    return await get_client().jira_post(
        f"issue/{issue_key}/watchers", body=account_id
    )


@mcp.tool()
async def remove_jira_watcher(issue_key: str, account_id: str) -> str:
    """Remove a watcher from a Jira issue.

    Args:
        issue_key: Issue key.
        account_id: Atlassian account ID of the user to remove.
    """
    return await get_client().jira_delete(
        f"issue/{issue_key}/watchers", params={"accountId": account_id}
    )


@mcp.tool()
async def get_jira_votes(issue_key: str) -> str:
    """Get votes for a Jira issue.

    Args:
        issue_key: Issue key.
    """
    return await get_client().jira_get(f"issue/{issue_key}/votes")


@mcp.tool()
async def add_jira_vote(issue_key: str) -> str:
    """Vote for a Jira issue (as the authenticated user).

    Args:
        issue_key: Issue key.
    """
    return await get_client().jira_post(f"issue/{issue_key}/votes")
