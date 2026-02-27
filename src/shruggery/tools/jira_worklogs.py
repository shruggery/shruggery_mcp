"""Jira worklogs — time tracking."""

from __future__ import annotations

from typing import Any

from shruggery.client import get_client
from shruggery.server import mcp
from shruggery.utils.formatting import markdown_to_adf


@mcp.tool()
async def get_jira_worklogs(
    issue_key: str, start_at: int = 0, max_results: int = 50
) -> str:
    """Get worklogs for a Jira issue.

    Args:
        issue_key: Issue key.
        start_at: Pagination offset.
        max_results: Max results.
    """
    return await get_client().jira_get(
        f"issue/{issue_key}/worklog",
        params={"startAt": start_at, "maxResults": max_results},
    )


@mcp.tool()
async def add_jira_worklog(
    issue_key: str,
    time_spent: str,
    comment: str | None = None,
    started: str | None = None,
) -> str:
    """Add a worklog entry to a Jira issue.

    Args:
        issue_key: Issue key.
        time_spent: Time spent string (e.g. "2h 30m", "1d").
        comment: Optional markdown comment text.
        started: When the work started (ISO datetime). Defaults to now.
    """
    body: dict[str, Any] = {"timeSpent": time_spent}
    if comment:
        body["comment"] = markdown_to_adf(comment)
    if started:
        body["started"] = started
    return await get_client().jira_post(f"issue/{issue_key}/worklog", body=body)


@mcp.tool()
async def update_jira_worklog(
    issue_key: str,
    worklog_id: str,
    time_spent: str | None = None,
    comment: str | None = None,
    started: str | None = None,
) -> str:
    """Update a worklog entry.

    Args:
        issue_key: Issue key.
        worklog_id: Worklog ID.
        time_spent: New time spent string.
        comment: New markdown comment text.
        started: New start time.
    """
    body: dict[str, Any] = {}
    if time_spent:
        body["timeSpent"] = time_spent
    if comment:
        body["comment"] = markdown_to_adf(comment)
    if started:
        body["started"] = started
    return await get_client().jira_put(
        f"issue/{issue_key}/worklog/{worklog_id}", body=body
    )


@mcp.tool()
async def delete_jira_worklog(issue_key: str, worklog_id: str) -> str:
    """Delete a worklog entry.

    Args:
        issue_key: Issue key.
        worklog_id: Worklog ID.
    """
    return await get_client().jira_delete(
        f"issue/{issue_key}/worklog/{worklog_id}"
    )
