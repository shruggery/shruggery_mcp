"""FastMCP application — tool registration and entry point."""

from __future__ import annotations

from fastmcp import FastMCP

mcp = FastMCP("shruggery")


def _register_tools() -> None:
    """Import all tool modules so their @mcp.tool() decorators run."""
    from shruggery.tools import (  # noqa: F401
        jira_issues,
        jira_search,
        jira_comments,
        jira_attachments,
        jira_worklogs,
        jira_links,
        jira_watchers,
        jira_projects,
        jira_boards,
        jira_fields,
        jira_filters,
        jira_users,
        jira_workflows,
        confluence_pages,
        confluence_search,
        confluence_comments,
        confluence_attachments,
        confluence_spaces,
        confluence_labels,
        confluence_properties,
        confluence_templates,
    )


def main() -> None:
    _register_tools()
    mcp.run()


if __name__ == "__main__":
    main()
