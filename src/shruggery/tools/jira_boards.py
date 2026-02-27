"""Jira Agile boards and sprints."""

from __future__ import annotations

from shruggery.client import get_client
from shruggery.server import mcp


@mcp.tool()
async def get_jira_boards(
    project_key: str | None = None,
    board_type: str | None = None,
    start_at: int = 0,
    max_results: int = 50,
) -> str:
    """List Jira Agile boards.

    Args:
        project_key: Filter by project key.
        board_type: Filter by type — "scrum", "kanban", or "simple".
        start_at: Pagination offset.
        max_results: Max results.
    """
    params: dict = {"startAt": start_at, "maxResults": max_results}
    if project_key:
        params["projectKeyOrId"] = project_key
    if board_type:
        params["type"] = board_type
    return await get_client().agile_get("board", params=params)


@mcp.tool()
async def get_jira_board(board_id: int) -> str:
    """Get a single Jira Agile board.

    Args:
        board_id: Board ID.
    """
    return await get_client().agile_get(f"board/{board_id}")


@mcp.tool()
async def get_jira_sprints(
    board_id: int,
    state: str | None = None,
    start_at: int = 0,
    max_results: int = 50,
) -> str:
    """List sprints for a Jira Agile board.

    Args:
        board_id: Board ID.
        state: Filter by state — "active", "closed", "future".
        start_at: Pagination offset.
        max_results: Max results.
    """
    params: dict = {"startAt": start_at, "maxResults": max_results}
    if state:
        params["state"] = state
    return await get_client().agile_get(f"board/{board_id}/sprint", params=params)


@mcp.tool()
async def get_jira_sprint_issues(
    sprint_id: int,
    start_at: int = 0,
    max_results: int = 50,
    fields: str | None = None,
) -> str:
    """Get issues in a sprint.

    Args:
        sprint_id: Sprint ID.
        start_at: Pagination offset.
        max_results: Max results.
        fields: Comma-separated field names.
    """
    params: dict = {"startAt": start_at, "maxResults": max_results}
    if fields:
        params["fields"] = fields
    return await get_client().agile_get(f"sprint/{sprint_id}/issue", params=params)


@mcp.tool()
async def get_jira_backlog(
    board_id: int,
    start_at: int = 0,
    max_results: int = 50,
    fields: str | None = None,
) -> str:
    """Get backlog issues for a board.

    Args:
        board_id: Board ID.
        start_at: Pagination offset.
        max_results: Max results.
        fields: Comma-separated field names.
    """
    params: dict = {"startAt": start_at, "maxResults": max_results}
    if fields:
        params["fields"] = fields
    return await get_client().agile_get(f"board/{board_id}/backlog", params=params)
