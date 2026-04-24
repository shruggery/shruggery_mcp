"""Path-traversal hardening for AtlassianClient.download()."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from shruggery.client import AtlassianClient
from shruggery.config import Settings


def _client(tmp_path: Path) -> AtlassianClient:
    settings = Settings(
        email="x@example.com",
        api_token="t",
        site="example.atlassian.net",
        download_dir=tmp_path,
    )
    return AtlassianClient(settings)


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def _is_error(result: str) -> bool:
    try:
        parsed = json.loads(result)
    except json.JSONDecodeError:
        return False
    return bool(parsed.get("error"))


@pytest.mark.parametrize(
    "filename",
    ["../escape.txt", "../../etc/passwd", "/abs/path.txt", "..", "."],
)
def test_download_rejects_traversal_filename(tmp_path, filename):
    c = _client(tmp_path)
    try:
        result = _run(c.download("https://example.com/x", filename))
        assert _is_error(result), f"expected error for {filename!r}, got {result}"
    finally:
        _run(c.close())


@pytest.mark.parametrize("subdir", ["../out", "../../out", "/abs", "a/../../b"])
def test_download_rejects_traversal_subdir(tmp_path, subdir):
    c = _client(tmp_path)
    try:
        result = _run(c.download("https://example.com/x", "ok.txt", subdir=subdir))
        assert _is_error(result), f"expected error for subdir {subdir!r}, got {result}"
    finally:
        _run(c.close())


def test_download_strips_path_components_in_filename(tmp_path, monkeypatch):
    """A filename containing path separators is reduced to its basename."""
    c = _client(tmp_path)

    class _FakeStreamCtx:
        def __init__(self):
            self.status_code = 404

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def aread(self):
            return b""

    monkeypatch.setattr(c._http, "stream", lambda *a, **kw: _FakeStreamCtx())

    try:
        # "subdir/inner.txt" → basename "inner.txt"; download will fail at HTTP layer
        # but the important assertion is that no traversal error is returned for the
        # basename-only case.
        result = _run(c.download("https://example.com/x", "subdir/inner.txt"))
        # 404 path returns an error_msg; ensure it's the HTTP one, not our 400 guard.
        parsed = json.loads(result)
        assert parsed.get("status") != 400
    finally:
        _run(c.close())
