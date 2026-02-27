<p align="center">
  <img src="logo.png" alt="Shruggery" width="200">
</p>

# Shruggery

Local Atlassian MCP server — full Jira Cloud v3 + Confluence Cloud v2 REST API coverage with attachment upload/download.

Named after *Atlas Shrugged* — because when Atlassian's official MCP shrugs off your needs, you build your own.

## Why

The hosted Atlassian MCP (`mcp.atlassian.com/v1/sse`) covers basic Jira/Confluence operations but lacks attachment handling and has limited API surface. Shruggery replaces it with a local stdio MCP server exposing **75 tools** across nearly every Jira and Confluence REST endpoint.

## Tech Stack

- **Python 3.11+**
- **FastMCP 3.x** — `@mcp.tool()` decorator pattern
- **httpx** — async HTTP client
- **python-dotenv** — `.env` loading
- **pydantic** — models / validation

## Setup

### 1. Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

```env
ATLASSIAN_EMAIL=you@example.com
ATLASSIAN_API_TOKEN=your-api-token          # https://id.atlassian.com/manage-profile/security/api-tokens
ATLASSIAN_SITE=yoursite.atlassian.net
ATLASSIAN_CLOUD_ID=                         # optional, auto-discovered if omitted
USER_AGENT=Mozilla/5.0 (...)                # optional, defaults to Firefox UA
SHRUGGERY_DOWNLOAD_DIR=/tmp/shruggery       # where attachments are saved
```

### 2. Install

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
```

Or just run `./run_mcp.sh` — it creates the venv automatically on first run.

### 3. Verify

```bash
.venv/bin/python -m shruggery.server
```

### 4. Register in Claude Code

Add to your `.claude.json` or project `.mcp.json`:

```json
{
  "mcpServers": {
    "shruggery": {
      "type": "stdio",
      "command": "/path/to/shruggery/run_mcp.sh",
      "env": {
        "ATLASSIAN_EMAIL": "you@example.com",
        "ATLASSIAN_API_TOKEN": "your-api-token",
        "ATLASSIAN_SITE": "yoursite.atlassian.net"
      }
    }
  }
}
```

Env vars in Claude config override `.env` values.

## Project Structure

```
shruggery/
├── pyproject.toml
├── run_mcp.sh                  # venv wrapper for Claude Code stdio
├── .env                        # credentials (git-ignored)
├── .env.example
├── .gitignore
└── src/shruggery/
    ├── __init__.py
    ├── server.py               # FastMCP app, tool registration, entry point
    ├── client.py               # AtlassianClient — shared httpx async client
    ├── config.py               # Env loading, Settings dataclass
    ├── models.py               # Shared Pydantic models
    ├── tools/
    │   ├── jira_issues.py              # CRUD, transitions, assign, changelog
    │   ├── jira_search.py              # JQL search
    │   ├── jira_comments.py            # Issue comments CRUD
    │   ├── jira_attachments.py         # Upload/download/delete
    │   ├── jira_worklogs.py            # Time tracking
    │   ├── jira_links.py              # Issue links + remote links
    │   ├── jira_watchers.py            # Watchers + votes
    │   ├── jira_projects.py            # Projects, components, versions
    │   ├── jira_boards.py              # Boards, sprints (Agile API)
    │   ├── jira_fields.py              # Field metadata
    │   ├── jira_filters.py             # Saved filters CRUD
    │   ├── jira_users.py               # User lookup, groups
    │   ├── jira_workflows.py           # Workflow metadata
    │   ├── confluence_pages.py         # Pages CRUD, versions
    │   ├── confluence_search.py        # CQL search
    │   ├── confluence_comments.py      # Footer + inline comments
    │   ├── confluence_attachments.py   # Upload/download/delete
    │   ├── confluence_spaces.py        # Spaces, page listing
    │   ├── confluence_labels.py        # Label management
    │   ├── confluence_properties.py    # Content properties
    │   └── confluence_templates.py     # Page templates
    └── utils/
        ├── pagination.py       # Pagination helpers
        └── formatting.py       # Response formatting, truncation, markdown→ADF
```

## Tool Reference

### Jira (38 tools)

#### Issues
| Tool | Description |
|------|-------------|
| `get_jira_issue` | Get issue by key, with optional field/expand selection |
| `create_jira_issue` | Create issue with ADF description support |
| `update_jira_issue` | Update fields or apply operations |
| `delete_jira_issue` | Delete issue (optionally with subtasks) |
| `get_jira_transitions` | List available status transitions |
| `transition_jira_issue` | Move issue to new status |
| `assign_jira_issue` | Assign/unassign issue |
| `get_jira_issue_changelog` | View issue change history |

#### Search
| Tool | Description |
|------|-------------|
| `search_jira_jql` | Search issues with JQL, pagination, field selection |

#### Comments
| Tool | Description |
|------|-------------|
| `get_jira_comments` | List comments on an issue |
| `add_jira_comment` | Add a comment (markdown → ADF) |
| `update_jira_comment` | Edit an existing comment |
| `delete_jira_comment` | Delete a comment |

#### Attachments
| Tool | Description |
|------|-------------|
| `get_jira_attachments` | List attachments on an issue |
| `upload_jira_attachment` | Upload a local file to an issue |
| `download_jira_attachment` | Download attachment to local temp file |
| `delete_jira_attachment` | Delete an attachment |

#### Worklogs
| Tool | Description |
|------|-------------|
| `get_jira_worklogs` | List worklog entries |
| `add_jira_worklog` | Log time (e.g. "2h 30m") |
| `update_jira_worklog` | Edit a worklog entry |
| `delete_jira_worklog` | Delete a worklog entry |

#### Links
| Tool | Description |
|------|-------------|
| `create_jira_link` | Link two issues (Blocks, Relates, etc.) |
| `delete_jira_link` | Remove an issue link |
| `get_jira_link_types` | List available link types |
| `get_jira_remote_links` | List remote links on an issue |
| `create_jira_remote_link` | Add external URL link to an issue |

#### Watchers & Votes
| Tool | Description |
|------|-------------|
| `get_jira_watchers` | List watchers |
| `add_jira_watcher` | Add a watcher |
| `remove_jira_watcher` | Remove a watcher |
| `get_jira_votes` | Get vote count and voters |
| `add_jira_vote` | Vote for an issue |

#### Projects
| Tool | Description |
|------|-------------|
| `get_jira_projects` | List visible projects |
| `get_jira_project` | Get single project details |
| `get_jira_components` | List project components |
| `get_jira_versions` | List project versions |

#### Boards & Sprints (Agile API)
| Tool | Description |
|------|-------------|
| `get_jira_boards` | List boards (scrum/kanban/simple) |
| `get_jira_board` | Get single board |
| `get_jira_sprints` | List sprints (active/closed/future) |
| `get_jira_sprint_issues` | Get issues in a sprint |
| `get_jira_backlog` | Get backlog issues |

#### Metadata
| Tool | Description |
|------|-------------|
| `get_jira_fields` | All system + custom fields |
| `get_jira_filter` | Get saved filter by ID |
| `get_jira_favorite_filters` | List favorite filters |
| `create_jira_filter` | Create a saved filter |
| `find_jira_users` | Search users by name/email |
| `get_jira_user` | Get user by account ID |
| `get_jira_user_groups` | Get user's group memberships |
| `get_jira_workflows` | List all workflows |

### Confluence (27 tools)

#### Pages
| Tool | Description |
|------|-------------|
| `get_confluence_page` | Get page by ID with body content |
| `get_confluence_pages` | List pages with filters |
| `create_confluence_page` | Create page (storage XHTML or ADF) |
| `update_confluence_page` | Update page content and title |
| `delete_confluence_page` | Trash a page |
| `get_confluence_page_versions` | Version history |
| `get_confluence_page_by_title` | Find page by exact title in a space |

#### Search
| Tool | Description |
|------|-------------|
| `search_confluence_cql` | Search with CQL |

#### Comments
| Tool | Description |
|------|-------------|
| `get_confluence_comments` | List footer comments |
| `get_confluence_inline_comments` | List inline comments |
| `create_confluence_comment` | Add footer comment |
| `create_confluence_inline_comment` | Add inline comment anchored to text |
| `delete_confluence_comment` | Delete a comment |

#### Attachments
| Tool | Description |
|------|-------------|
| `get_confluence_attachments` | List page attachments |
| `upload_confluence_attachment` | Upload local file to a page |
| `download_confluence_attachment` | Download to local temp file |
| `delete_confluence_attachment` | Delete an attachment |

#### Spaces
| Tool | Description |
|------|-------------|
| `get_confluence_spaces` | List spaces (global/personal) |
| `get_confluence_space` | Get space by ID |
| `get_confluence_space_pages` | List pages in a space |

#### Labels
| Tool | Description |
|------|-------------|
| `get_confluence_labels` | List labels on a page |
| `add_confluence_labels` | Add labels to a page |
| `remove_confluence_label` | Remove a label |

#### Properties
| Tool | Description |
|------|-------------|
| `get_confluence_properties` | List content properties |
| `set_confluence_property` | Set/update a property |
| `delete_confluence_property` | Delete a property |

#### Templates
| Tool | Description |
|------|-------------|
| `get_confluence_templates` | List page templates |

## Attachment Handling

The key feature missing from the official Atlassian MCP.

**Download:** Tool receives an attachment ID → `client.download()` streams the file to `SHRUGGERY_DOWNLOAD_DIR/{jira|confluence}/{filename}` → returns the local file path.

**Upload:** Tool receives a local file path + target issue/page → `client.upload()` sends multipart/form-data with `X-Atlassian-Token: no-check` → returns attachment metadata.

## Architecture Notes

- **Single shared httpx client** with basic auth, configurable User-Agent, 30s timeout
- **URL builders** for Jira v3, Confluence v2, Agile 1.0, and Confluence v1 fallback
- **All tools return JSON strings** — formatted with `json.dumps(indent=2)`, truncated at 80K chars
- **Error responses** are structured: `{"error": true, "status": 400, "detail": ...}`
- **Markdown → ADF conversion** for comments/descriptions: headings, lists, tables, code blocks, blockquotes, bold/italic/links are converted to Atlassian Document Format — no external dependencies
