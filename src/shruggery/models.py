"""Shared Pydantic models."""

from __future__ import annotations

from pydantic import BaseModel


class PaginatedResponse(BaseModel):
    """Generic wrapper for paginated API results."""

    results: list[dict]
    total: int | None = None
    start_at: int | None = None
    max_results: int | None = None
    next_cursor: str | None = None


class ErrorResponse(BaseModel):
    """Structured error from Atlassian API."""

    status_code: int
    message: str
    errors: list[str] = []
