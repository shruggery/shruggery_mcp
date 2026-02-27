"""Jira attachment upload, download, delete."""

from __future__ import annotations

import json

from shruggery.client import get_client
from shruggery.utils.formatting import error_msg, fmt
from shruggery.server import mcp


@mcp.tool()
async def get_jira_attachments(issue_key: str) -> str:
    """List attachments on a Jira issue.

    Args:
        issue_key: Issue key.
    """
    client = get_client()
    result = await client.jira_get(f"issue/{issue_key}", params={"fields": "attachment"})
    try:
        data = json.loads(result)
        if "fields" in data and "attachment" in data["fields"]:
            return fmt(data["fields"]["attachment"])
    except (json.JSONDecodeError, KeyError):
        pass
    return result


@mcp.tool()
async def upload_jira_attachment(issue_key: str, file_path: str) -> str:
    """Upload a file as an attachment to a Jira issue.

    Args:
        issue_key: Issue key.
        file_path: Absolute path to the file to upload.
    """
    client = get_client()
    url = f"{client.settings.jira_base}/issue/{issue_key}/attachments"
    return await client.upload(url, file_path)


@mcp.tool()
async def download_jira_attachment(attachment_id: str) -> str:
    """Download a Jira attachment to a local temp file.

    Args:
        attachment_id: Attachment ID (from get_jira_attachments).

    Returns the local file path where the attachment was saved.
    """
    client = get_client()
    # First, get attachment metadata for the filename and download URL
    status, meta = await client._request(
        "GET", f"{client.settings.jira_base}/attachment/{attachment_id}"
    )
    if status >= 400:
        return error_msg(status, meta)

    filename = meta.get("filename", f"attachment_{attachment_id}")
    content_url = meta.get("content", "")
    if not content_url:
        return error_msg(404, "No download URL in attachment metadata")

    return await client.download(content_url, filename, subdir="jira")


@mcp.tool()
async def delete_jira_attachment(attachment_id: str) -> str:
    """Delete a Jira attachment.

    Args:
        attachment_id: Attachment ID.
    """
    return await get_client().jira_delete(f"attachment/{attachment_id}")
