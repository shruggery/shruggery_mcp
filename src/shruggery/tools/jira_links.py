"""Jira issue links and remote links."""

from __future__ import annotations

from typing import Any

from shruggery.client import get_client
from shruggery.server import mcp
from shruggery.utils.formatting import markdown_to_adf


@mcp.tool()
async def create_jira_link(
    inward_issue: str,
    outward_issue: str,
    link_type: str,
    comment: str | None = None,
) -> str:
    """Create a link between two Jira issues.

    Args:
        inward_issue: Inward issue key (e.g. "PROJ-1").
        outward_issue: Outward issue key (e.g. "PROJ-2").
        link_type: Link type name (e.g. "Blocks", "Relates", "Duplicate").
        comment: Optional markdown comment on the link.
    """
    body: dict[str, Any] = {
        "type": {"name": link_type},
        "inwardIssue": {"key": inward_issue},
        "outwardIssue": {"key": outward_issue},
    }
    if comment:
        body["comment"] = {"body": markdown_to_adf(comment)}
    return await get_client().jira_post("issueLink", body=body)


@mcp.tool()
async def delete_jira_link(link_id: str) -> str:
    """Delete an issue link.

    Args:
        link_id: Issue link ID.
    """
    return await get_client().jira_delete(f"issueLink/{link_id}")


@mcp.tool()
async def get_jira_link_types() -> str:
    """Get all available issue link types."""
    return await get_client().jira_get("issueLinkType")


@mcp.tool()
async def get_jira_remote_links(issue_key: str) -> str:
    """Get remote links on a Jira issue.

    Args:
        issue_key: Issue key.
    """
    return await get_client().jira_get(f"issue/{issue_key}/remotelink")


@mcp.tool()
async def create_jira_remote_link(
    issue_key: str,
    url: str,
    title: str,
    summary: str | None = None,
) -> str:
    """Create a remote link on a Jira issue.

    Args:
        issue_key: Issue key.
        url: URL to link to.
        title: Link title.
        summary: Optional summary text.
    """
    obj: dict[str, Any] = {"url": url, "title": title}
    if summary:
        obj["summary"] = summary
    return await get_client().jira_post(
        f"issue/{issue_key}/remotelink", body={"object": obj}
    )
