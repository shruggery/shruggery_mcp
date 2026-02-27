"""Confluence attachment upload, download, delete."""

from __future__ import annotations

from typing import Any

from shruggery.client import get_client
from shruggery.utils.formatting import error_msg
from shruggery.server import mcp


@mcp.tool()
async def get_confluence_attachments(
    page_id: str,
    limit: int = 25,
    cursor: str | None = None,
) -> str:
    """List attachments on a Confluence page.

    Args:
        page_id: Page ID.
        limit: Max results.
        cursor: Pagination cursor.
    """
    params: dict[str, Any] = {"limit": limit}
    if cursor:
        params["cursor"] = cursor
    return await get_client().confluence_get(
        f"pages/{page_id}/attachments", params=params
    )


@mcp.tool()
async def upload_confluence_attachment(page_id: str, file_path: str) -> str:
    """Upload a file as an attachment to a Confluence page.

    Args:
        page_id: Page ID.
        file_path: Absolute path to the file to upload.
    """
    client = get_client()
    url = f"{client.settings.confluence_v1_base}/content/{page_id}/child/attachment"
    return await client.upload(url, file_path)


@mcp.tool()
async def download_confluence_attachment(attachment_id: str) -> str:
    """Download a Confluence attachment to a local temp file.

    Args:
        attachment_id: Attachment ID (from get_confluence_attachments).

    Returns the local file path where the attachment was saved.
    """
    client = get_client()
    # v2 API for attachment metadata
    status, meta = await client._request(
        "GET", f"{client.settings.confluence_v2_base}/attachments/{attachment_id}"
    )
    if status >= 400:
        return error_msg(status, meta)

    title = meta.get("title", f"attachment_{attachment_id}")
    download_link = meta.get("downloadLink", "")
    if not download_link:
        return error_msg(404, "No download link in attachment metadata")

    # downloadLink is relative to the wiki base
    full_url = f"https://{client.settings.site}/wiki{download_link}"
    return await client.download(full_url, title, subdir="confluence")


@mcp.tool()
async def delete_confluence_attachment(attachment_id: str) -> str:
    """Delete a Confluence attachment.

    Args:
        attachment_id: Attachment ID.
    """
    return await get_client().confluence_delete(f"attachments/{attachment_id}")
