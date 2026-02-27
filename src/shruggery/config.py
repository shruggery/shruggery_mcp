"""Settings loaded from environment / .env file."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

_DEFAULT_UA = "Shruggery/0.1.0"


@dataclass(frozen=True)
class Settings:
    email: str
    api_token: str
    site: str
    cloud_id: str | None = None
    user_agent: str = _DEFAULT_UA
    download_dir: Path = field(default_factory=lambda: Path("/tmp/shruggery"))

    @property
    def jira_base(self) -> str:
        return f"https://{self.site}/rest/api/3"

    @property
    def agile_base(self) -> str:
        return f"https://{self.site}/rest/agile/1.0"

    @property
    def confluence_v2_base(self) -> str:
        return f"https://{self.site}/wiki/api/v2"

    @property
    def confluence_v1_base(self) -> str:
        return f"https://{self.site}/wiki/rest/api"

    @property
    def auth(self) -> tuple[str, str]:
        return (self.email, self.api_token)


def load_settings() -> Settings:
    """Load settings from .env then env vars (env vars win)."""
    # Walk up from this file to find .env next to pyproject.toml
    pkg_dir = Path(__file__).resolve().parent
    for ancestor in (pkg_dir, pkg_dir.parent, pkg_dir.parent.parent):
        env_path = ancestor / ".env"
        if env_path.exists():
            load_dotenv(env_path, override=False)
            break

    email = os.environ.get("ATLASSIAN_EMAIL", "")
    api_token = os.environ.get("ATLASSIAN_API_TOKEN", "")
    site = os.environ.get("ATLASSIAN_SITE", "")

    if not all([email, api_token, site]):
        raise RuntimeError(
            "ATLASSIAN_EMAIL, ATLASSIAN_API_TOKEN, and ATLASSIAN_SITE must be set"
        )

    return Settings(
        email=email,
        api_token=api_token,
        site=site,
        cloud_id=os.environ.get("ATLASSIAN_CLOUD_ID") or None,
        user_agent=os.environ.get("USER_AGENT", _DEFAULT_UA),
        download_dir=Path(os.environ.get("SHRUGGERY_DOWNLOAD_DIR", "/tmp/shruggery")),
    )
