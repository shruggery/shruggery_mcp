"""Smoke test — server imports and registers tools."""

from __future__ import annotations

import asyncio


def test_server_registers_tools(monkeypatch):
    monkeypatch.setenv("ATLASSIAN_EMAIL", "x@example.com")
    monkeypatch.setenv("ATLASSIAN_API_TOKEN", "dummy")
    monkeypatch.setenv("ATLASSIAN_SITE", "example.atlassian.net")

    from shruggery import server

    server._register_tools()
    tools = asyncio.get_event_loop().run_until_complete(server.mcp.list_tools())
    assert len(tools) > 50, f"expected 50+ tools registered, got {len(tools)}"
