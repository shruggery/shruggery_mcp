"""Generic pagination helpers for Atlassian REST APIs."""

from __future__ import annotations


def jira_paginate_params(start_at: int = 0, max_results: int = 50) -> dict:
    """Build Jira offset-based pagination params."""
    return {"startAt": start_at, "maxResults": max_results}


def confluence_paginate_params(
    cursor: str | None = None, limit: int = 25
) -> dict:
    """Build Confluence cursor-based pagination params."""
    params: dict = {"limit": limit}
    if cursor:
        params["cursor"] = cursor
    return params
