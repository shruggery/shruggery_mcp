"""Jira issue comments CRUD."""

from __future__ import annotations

from shruggery.client import get_client
from shruggery.server import mcp
from shruggery.utils.formatting import markdown_to_adf


@mcp.tool()
async def get_jira_comments(
    issue_key: str, start_at: int = 0, max_results: int = 50
) -> str:
    """Get comments on a Jira issue.

    Args:
        issue_key: Issue key.
        start_at: Pagination offset.
        max_results: Max comments to return.
    """
    return await get_client().jira_get(
        f"issue/{issue_key}/comment",
        params={"startAt": start_at, "maxResults": max_results},
    )


@mcp.tool()
async def add_jira_comment(issue_key: str, body_text: str) -> str:
    """Add a comment to a Jira issue.

    Args:
        issue_key: Issue key.
        body_text: Comment text (markdown, converted to ADF).
    """
    body = {"body": markdown_to_adf(body_text)}
    return await get_client().jira_post(f"issue/{issue_key}/comment", body=body)


@mcp.tool()
async def update_jira_comment(
    issue_key: str, comment_id: str, body_text: str
) -> str:
    """Update an existing comment on a Jira issue.

    Args:
        issue_key: Issue key.
        comment_id: Comment ID.
        body_text: New comment text (markdown, converted to ADF).
    """
    body = {"body": markdown_to_adf(body_text)}
    return await get_client().jira_put(
        f"issue/{issue_key}/comment/{comment_id}", body=body
    )


@mcp.tool()
async def delete_jira_comment(issue_key: str, comment_id: str) -> str:
    """Delete a comment from a Jira issue.

    Args:
        issue_key: Issue key.
        comment_id: Comment ID.
    """
    return await get_client().jira_delete(
        f"issue/{issue_key}/comment/{comment_id}"
    )
