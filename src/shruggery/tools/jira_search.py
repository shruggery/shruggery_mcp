"""Jira JQL search."""

from __future__ import annotations

from shruggery.client import get_client
from shruggery.server import mcp


@mcp.tool()
async def search_jira_jql(
    jql: str,
    fields: str | None = None,
    expand: str | None = None,
    next_page_token: str | None = None,
    max_results: int = 25,
) -> str:
    """Search Jira issues using JQL.

    Returns up to 25 issues per call. Use next_page_token for pagination.
    Use ``fields`` to limit response size (e.g. "summary,status,assignee").

    Args:
        jql: JQL query string.
        fields: Comma-separated field names to return.
        expand: Comma-separated expansions.
        next_page_token: Pagination token from a previous response.
        max_results: Max results per page (default 25, max 100).
    """
    body: dict = {
        "jql": jql,
        "maxResults": min(max_results, 100),
    }
    if next_page_token:
        body["nextPageToken"] = next_page_token
    if fields:
        body["fields"] = [f.strip() for f in fields.split(",")]
    if expand:
        body["expand"] = [e.strip() for e in expand.split(",")]
    return await get_client().jira_post("search/jql", body=body)
