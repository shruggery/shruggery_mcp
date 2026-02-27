"""Jira issue CRUD, transitions, assignment, changelog."""

from __future__ import annotations

from typing import Any

from shruggery.client import get_client
from shruggery.server import mcp


@mcp.tool()
async def get_jira_issue(
    issue_key: str,
    fields: str | None = None,
    expand: str | None = None,
) -> str:
    """Get a Jira issue by key.

    Args:
        issue_key: Issue key (e.g. "PROJ-123").
        fields: Comma-separated field names to include. Omit for all fields.
        expand: Comma-separated expansions (e.g. "renderedFields,changelog").
    """
    client = get_client()
    params: dict[str, str] = {}
    if fields:
        params["fields"] = fields
    if expand:
        params["expand"] = expand
    return await client.jira_get(f"issue/{issue_key}", params=params)


@mcp.tool()
async def create_jira_issue(
    project_key: str,
    summary: str,
    issue_type: str = "Task",
    description: str | None = None,
    fields: dict[str, Any] | None = None,
) -> str:
    """Create a Jira issue.

    Args:
        project_key: Project key (e.g. "PROJ").
        summary: Issue summary / title.
        issue_type: Issue type name (default "Task").
        description: Plain-text description (converted to ADF paragraph).
        fields: Additional fields dict merged into the request.
    """
    body: dict[str, Any] = {
        "fields": {
            "project": {"key": project_key},
            "summary": summary,
            "issuetype": {"name": issue_type},
        }
    }
    if description:
        body["fields"]["description"] = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": description}],
                }
            ],
        }
    if fields:
        body["fields"].update(fields)
    return await get_client().jira_post("issue", body=body)


@mcp.tool()
async def update_jira_issue(
    issue_key: str,
    fields: dict[str, Any] | None = None,
    update: dict[str, Any] | None = None,
) -> str:
    """Update a Jira issue's fields.

    Args:
        issue_key: Issue key.
        fields: Fields to set (e.g. {"summary": "New title"}).
        update: Operations to apply (e.g. {"labels": [{"add": "urgent"}]}).
    """
    body: dict[str, Any] = {}
    if fields:
        body["fields"] = fields
    if update:
        body["update"] = update
    return await get_client().jira_put(f"issue/{issue_key}", body=body)


@mcp.tool()
async def delete_jira_issue(issue_key: str, delete_subtasks: bool = False) -> str:
    """Delete a Jira issue.

    Args:
        issue_key: Issue key.
        delete_subtasks: Also delete subtasks.
    """
    params = {}
    if delete_subtasks:
        params["deleteSubtasks"] = "true"
    return await get_client().jira_delete(f"issue/{issue_key}", params=params)


@mcp.tool()
async def get_jira_transitions(issue_key: str) -> str:
    """Get available transitions for a Jira issue.

    Args:
        issue_key: Issue key.
    """
    return await get_client().jira_get(f"issue/{issue_key}/transitions")


@mcp.tool()
async def transition_jira_issue(
    issue_key: str,
    transition_id: str,
    fields: dict[str, Any] | None = None,
    comment: str | None = None,
) -> str:
    """Transition a Jira issue to a new status.

    Args:
        issue_key: Issue key.
        transition_id: Transition ID (from get_jira_transitions).
        fields: Fields to set during transition.
        comment: Optional comment to add during transition.
    """
    body: dict[str, Any] = {"transition": {"id": transition_id}}
    if fields:
        body["fields"] = fields
    if comment:
        body["update"] = {
            "comment": [
                {
                    "add": {
                        "body": {
                            "type": "doc",
                            "version": 1,
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": comment}],
                                }
                            ],
                        }
                    }
                }
            ]
        }
    return await get_client().jira_post(f"issue/{issue_key}/transitions", body=body)


@mcp.tool()
async def assign_jira_issue(issue_key: str, account_id: str | None = None) -> str:
    """Assign a Jira issue to a user.

    Args:
        issue_key: Issue key.
        account_id: Atlassian account ID. Pass None to unassign.
    """
    return await get_client().jira_put(
        f"issue/{issue_key}/assignee", body={"accountId": account_id}
    )


@mcp.tool()
async def get_jira_issue_changelog(
    issue_key: str, start_at: int = 0, max_results: int = 50
) -> str:
    """Get the changelog of a Jira issue.

    Args:
        issue_key: Issue key.
        start_at: Pagination offset.
        max_results: Max items to return.
    """
    return await get_client().jira_get(
        f"issue/{issue_key}/changelog",
        params={"startAt": start_at, "maxResults": max_results},
    )
