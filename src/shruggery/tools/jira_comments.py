"""Jira issue comments CRUD."""

from __future__ import annotations

from shruggery.client import get_client
from shruggery.server import mcp
from shruggery.utils.formatting import markdown_to_adf


def _jsm_guard(issue_key: str, internal: bool, public_override: bool) -> str | None:
    """Block public comments on JSM projects unless explicitly overridden.

    Returns an error string if blocked, None if allowed.
    """
    prefix = issue_key.split("-")[0].upper()
    settings = get_client().settings
    if prefix in settings.jsm_project_prefixes and not internal and not public_override:
        return (
            f"BLOCKED: {prefix} is a JSM project — comments are customer-visible "
            f"by default. Pass internal=true for an internal note, or "
            f"public_override=true to explicitly post as customer-visible."
        )
    return None


def _comment_body(body_text: str, internal: bool) -> dict:
    """Build the JSON body for a comment, with optional JSM visibility."""
    body: dict = {"body": markdown_to_adf(body_text)}
    if internal:
        body["properties"] = [
            {"key": "sd.public.comment", "value": {"internal": True}}
        ]
    return body


@mcp.tool()
async def get_jira_comments(
    issue_key: str, start_at: int = 0, max_results: int = 20
) -> str:
    """Get comments on a Jira issue.

    Returns up to 20 comments per call (ADF bodies are large).
    Use start_at for pagination — response includes ``total`` and ``startAt``.

    Args:
        issue_key: Issue key.
        start_at: Pagination offset.
        max_results: Max comments to return (default 20).
    """
    return await get_client().jira_get(
        f"issue/{issue_key}/comment",
        params={"startAt": start_at, "maxResults": max_results},
    )


@mcp.tool()
async def add_jira_comment(
    issue_key: str,
    body_text: str,
    internal: bool = False,
    public_override: bool = False,
) -> str:
    """Add a comment to a Jira issue.

    For JSM projects (e.g. SUPPORT), comments default to customer-visible.
    Use internal=true for an internal note. If you intentionally want a
    customer-visible comment on a JSM ticket, pass public_override=true.

    Args:
        issue_key: Issue key.
        body_text: Comment text (markdown, converted to ADF).
        internal: Post as internal note (not visible to customer).
        public_override: Explicitly allow a public comment on JSM projects.
    """
    err = _jsm_guard(issue_key, internal, public_override)
    if err:
        return err
    return await get_client().jira_post(
        f"issue/{issue_key}/comment", body=_comment_body(body_text, internal)
    )


@mcp.tool()
async def update_jira_comment(
    issue_key: str,
    comment_id: str,
    body_text: str,
    internal: bool | None = None,
    public_override: bool = False,
) -> str:
    """Update an existing comment on a Jira issue.

    Args:
        issue_key: Issue key.
        comment_id: Comment ID.
        body_text: New comment text (markdown, converted to ADF).
        internal: Set visibility — true for internal, false for public, omit to leave unchanged.
        public_override: Explicitly allow setting a comment public on JSM projects.
    """
    if internal is not None:
        err = _jsm_guard(issue_key, internal, public_override)
        if err:
            return err
    body: dict = {"body": markdown_to_adf(body_text)}
    if internal is True:
        body["properties"] = [
            {"key": "sd.public.comment", "value": {"internal": True}}
        ]
    elif internal is False:
        body["properties"] = [
            {"key": "sd.public.comment", "value": {"internal": False}}
        ]
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
