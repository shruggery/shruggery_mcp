"""Shared async HTTP client for Atlassian REST APIs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx

from shruggery.config import Settings, load_settings
from shruggery.utils.formatting import error_msg, fmt

_client: AtlassianClient | None = None


class AtlassianClient:
    """Thin async wrapper around httpx for Jira + Confluence APIs."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._http = httpx.AsyncClient(
            auth=(settings.email, settings.api_token),
            headers={
                "User-Agent": settings.user_agent,
                "Accept": "application/json",
                "X-Atlassian-Token": "no-check",
            },
            timeout=httpx.Timeout(30.0, connect=10.0),
            follow_redirects=True,
        )

    # ── URL builders ────────────────────────────────────────────

    def _jira_url(self, path: str) -> str:
        return f"{self.settings.jira_base}/{path}"

    def _agile_url(self, path: str) -> str:
        return f"{self.settings.agile_base}/{path}"

    def _confluence_v2_url(self, path: str) -> str:
        return f"{self.settings.confluence_v2_base}/{path}"

    def _confluence_v1_url(self, path: str) -> str:
        return f"{self.settings.confluence_v1_base}/{path}"

    # ── Generic HTTP verbs ──────────────────────────────────────

    async def _request(
        self,
        method: str,
        url: str,
        *,
        params: dict | None = None,
        json_body: Any = None,
        headers: dict | None = None,
    ) -> tuple[int, Any]:
        """Execute request, return (status, parsed_body)."""
        resp = await self._http.request(
            method,
            url,
            params=params,
            json=json_body,
            headers=headers,
        )
        if resp.status_code == 204:
            return 204, None
        try:
            body = resp.json()
        except Exception:
            body = resp.text
        return resp.status_code, body

    async def _ok_or_error(
        self,
        method: str,
        url: str,
        *,
        params: dict | None = None,
        json_body: Any = None,
        headers: dict | None = None,
    ) -> str:
        """Make request; return formatted JSON on success, error string on failure."""
        status, body = await self._request(
            method, url, params=params, json_body=json_body, headers=headers
        )
        if 200 <= status < 300:
            if body is None:
                return json.dumps({"ok": True})
            return fmt(body)
        return error_msg(status, body)

    # ── Jira convenience ────────────────────────────────────────

    async def jira_get(self, path: str, *, params: dict | None = None) -> str:
        return await self._ok_or_error("GET", self._jira_url(path), params=params)

    async def jira_post(
        self, path: str, *, body: Any = None, params: dict | None = None
    ) -> str:
        return await self._ok_or_error(
            "POST", self._jira_url(path), json_body=body, params=params
        )

    async def jira_put(
        self, path: str, *, body: Any = None, params: dict | None = None
    ) -> str:
        return await self._ok_or_error(
            "PUT", self._jira_url(path), json_body=body, params=params
        )

    async def jira_delete(self, path: str, *, params: dict | None = None) -> str:
        return await self._ok_or_error("DELETE", self._jira_url(path), params=params)

    # ── Agile convenience ───────────────────────────────────────

    async def agile_get(self, path: str, *, params: dict | None = None) -> str:
        return await self._ok_or_error("GET", self._agile_url(path), params=params)

    # ── Confluence v2 convenience ───────────────────────────────

    async def confluence_get(self, path: str, *, params: dict | None = None) -> str:
        return await self._ok_or_error(
            "GET", self._confluence_v2_url(path), params=params
        )

    async def confluence_post(
        self, path: str, *, body: Any = None, params: dict | None = None
    ) -> str:
        return await self._ok_or_error(
            "POST", self._confluence_v2_url(path), json_body=body, params=params
        )

    async def confluence_put(
        self, path: str, *, body: Any = None, params: dict | None = None
    ) -> str:
        return await self._ok_or_error(
            "PUT", self._confluence_v2_url(path), json_body=body, params=params
        )

    async def confluence_delete(
        self, path: str, *, params: dict | None = None
    ) -> str:
        return await self._ok_or_error(
            "DELETE", self._confluence_v2_url(path), params=params
        )

    # ── Confluence v1 fallback ──────────────────────────────────

    async def confluence_v1_get(
        self, path: str, *, params: dict | None = None
    ) -> str:
        return await self._ok_or_error(
            "GET", self._confluence_v1_url(path), params=params
        )

    async def confluence_v1_post(
        self, path: str, *, body: Any = None, params: dict | None = None
    ) -> str:
        return await self._ok_or_error(
            "POST", self._confluence_v1_url(path), json_body=body, params=params
        )

    # ── File upload (multipart) ─────────────────────────────────

    async def upload(
        self, url: str, file_path: str, *, field_name: str = "file"
    ) -> str:
        """Upload a file via multipart form. Returns formatted JSON."""
        p = Path(file_path)
        if not p.exists():
            return error_msg(400, f"File not found: {file_path}")

        with open(p, "rb") as f:
            resp = await self._http.post(
                url,
                files={field_name: (p.name, f)},
                headers={
                    "X-Atlassian-Token": "no-check",
                    "Accept": "application/json",
                },
            )
        if 200 <= resp.status_code < 300:
            try:
                return fmt(resp.json())
            except Exception:
                return json.dumps({"ok": True})
        try:
            body = resp.json()
        except Exception:
            body = resp.text
        return error_msg(resp.status_code, body)

    # ── File download (stream to disk) ──────────────────────────

    async def download(self, url: str, filename: str, subdir: str = "") -> str:
        """Stream-download a file. Returns the local path."""
        dl_dir = self.settings.download_dir
        if subdir:
            dl_dir = dl_dir / subdir
        dl_dir.mkdir(parents=True, exist_ok=True)
        dest = dl_dir / filename

        async with self._http.stream("GET", url) as resp:
            if resp.status_code >= 400:
                await resp.aread()
                return error_msg(resp.status_code, "Download failed")
            with open(dest, "wb") as f:
                async for chunk in resp.aiter_bytes(8192):
                    f.write(chunk)
        return str(dest)

    # ── Lifecycle ───────────────────────────────────────────────

    async def close(self) -> None:
        await self._http.aclose()


def get_client() -> AtlassianClient:
    """Return the singleton client, creating it on first call."""
    global _client
    if _client is None:
        _client = AtlassianClient(load_settings())
    return _client
