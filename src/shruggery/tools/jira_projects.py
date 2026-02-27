"""Jira projects, components, versions."""

from __future__ import annotations

from shruggery.client import get_client
from shruggery.server import mcp


@mcp.tool()
async def get_jira_projects(
    start_at: int = 0, max_results: int = 50, expand: str | None = None
) -> str:
    """List Jira projects visible to the authenticated user.

    Args:
        start_at: Pagination offset.
        max_results: Max results.
        expand: Comma-separated expansions (e.g. "description,lead").
    """
    params: dict = {"startAt": start_at, "maxResults": max_results}
    if expand:
        params["expand"] = expand
    return await get_client().jira_get("project/search", params=params)


@mcp.tool()
async def get_jira_project(project_key: str, expand: str | None = None) -> str:
    """Get a single Jira project.

    Args:
        project_key: Project key (e.g. "PROJ").
        expand: Comma-separated expansions.
    """
    params: dict = {}
    if expand:
        params["expand"] = expand
    return await get_client().jira_get(f"project/{project_key}", params=params)


@mcp.tool()
async def get_jira_components(project_key: str) -> str:
    """Get components for a Jira project.

    Args:
        project_key: Project key.
    """
    return await get_client().jira_get(f"project/{project_key}/components")


@mcp.tool()
async def get_jira_versions(
    project_key: str, start_at: int = 0, max_results: int = 50
) -> str:
    """Get versions for a Jira project.

    Args:
        project_key: Project key.
        start_at: Pagination offset.
        max_results: Max results.
    """
    return await get_client().jira_get(
        f"project/{project_key}/version",
        params={"startAt": start_at, "maxResults": max_results},
    )
