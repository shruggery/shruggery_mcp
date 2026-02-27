"""Response formatting, content truncation, and Markdown-to-ADF conversion."""

from __future__ import annotations

import json
import re
from typing import Any

MAX_RESPONSE_LEN = 80_000


def fmt(data: Any) -> str:
    """Format API response data as indented JSON string, truncated if needed."""
    text = json.dumps(data, indent=2, default=str)
    if len(text) > MAX_RESPONSE_LEN:
        return text[:MAX_RESPONSE_LEN] + "\n... (truncated)"
    return text


def error_msg(status: int, body: Any) -> str:
    """Format an error response."""
    return json.dumps(
        {"error": True, "status": status, "detail": body}, indent=2, default=str
    )


# ---------------------------------------------------------------------------
# Markdown -> Atlassian Document Format (ADF) converter
# ---------------------------------------------------------------------------

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)(?:\s+#+\s*)?$")
_RULE_RE = re.compile(r"^(\s*[-*_]\s*){3,}$")
_BULLET_RE = re.compile(r"^(\s*)[-*+]\s+(.*)")
_ORDERED_RE = re.compile(r"^(\s*)\d+[.)]\s+(.*)")
_QUOTE_RE = re.compile(r"^>\s?(.*)")
_FENCE_OPEN_RE = re.compile(r"^`{3,}(\w*)\s*$")
_FENCE_CLOSE_RE = re.compile(r"^`{3,}\s*$")

# Inline patterns — order matters (longest/most-specific first).
_INLINE_RE = re.compile(
    r"\*\*\*(.+?)\*\*\*"  # 1: bold italic
    r"|\*\*(.+?)\*\*"  # 2: bold
    r"|__(.+?)__"  # 3: bold underscore
    r"|(?<!\*)\*([^*]+?)\*(?!\*)"  # 4: italic
    r"|(?<!\w)_([^_]+?)_(?!\w)"  # 5: italic underscore
    r"|`([^`]+)`"  # 6: inline code
    r"|~~(.+?)~~"  # 7: strikethrough
    r"|\[([^\]]+)\]\(([^)]+)\)"  # 8,9: link text + href
)


# -- Inline parsing ---------------------------------------------------------


def _parse_inline(text: str) -> list[dict[str, Any]]:
    """Convert inline markdown to a list of ADF text nodes with marks."""
    if not text:
        return [{"type": "text", "text": ""}]

    nodes: list[dict[str, Any]] = []
    pos = 0

    for m in _INLINE_RE.finditer(text):
        # Plain text before this match
        if m.start() > pos:
            nodes.append({"type": "text", "text": text[pos : m.start()]})

        if m.group(1) is not None:  # ***bold italic***
            node: dict[str, Any] = {
                "type": "text",
                "text": m.group(1),
                "marks": [{"type": "strong"}, {"type": "em"}],
            }
        elif m.group(2) is not None:  # **bold**
            node = {
                "type": "text",
                "text": m.group(2),
                "marks": [{"type": "strong"}],
            }
        elif m.group(3) is not None:  # __bold__
            node = {
                "type": "text",
                "text": m.group(3),
                "marks": [{"type": "strong"}],
            }
        elif m.group(4) is not None:  # *italic*
            node = {
                "type": "text",
                "text": m.group(4),
                "marks": [{"type": "em"}],
            }
        elif m.group(5) is not None:  # _italic_
            node = {
                "type": "text",
                "text": m.group(5),
                "marks": [{"type": "em"}],
            }
        elif m.group(6) is not None:  # `code`
            node = {
                "type": "text",
                "text": m.group(6),
                "marks": [{"type": "code"}],
            }
        elif m.group(7) is not None:  # ~~strike~~
            node = {
                "type": "text",
                "text": m.group(7),
                "marks": [{"type": "strike"}],
            }
        elif m.group(8) is not None:  # [text](url)
            node = {
                "type": "text",
                "text": m.group(8),
                "marks": [{"type": "link", "attrs": {"href": m.group(9)}}],
            }
        else:
            node = {"type": "text", "text": m.group(0)}

        nodes.append(node)
        pos = m.end()

    # Trailing plain text
    if pos < len(text):
        nodes.append({"type": "text", "text": text[pos:]})

    return nodes or [{"type": "text", "text": text}]


# -- Block helpers -----------------------------------------------------------


def _is_table_sep(line: str) -> bool:
    """Check whether *line* is a markdown table separator (e.g. ``| --- | --- |``)."""
    s = line.strip()
    return bool(re.match(r"^[\s|:-]+$", s)) and "-" in s and "|" in s


def _is_block_start(line: str) -> bool:
    """Return True if *line* begins a new block-level element."""
    s = line.strip()
    return bool(
        _HEADING_RE.match(line)
        or _RULE_RE.match(s)
        or _BULLET_RE.match(line)
        or _ORDERED_RE.match(line)
        or _QUOTE_RE.match(s)
        or _FENCE_OPEN_RE.match(s)
        or (s.startswith("|") and "|" in s[1:])
    )


def _parse_table(lines: list[str], start: int) -> tuple[dict[str, Any], int]:
    """Parse a markdown table starting at *start*. Returns ``(node, next_index)``."""
    header_cells = [c.strip() for c in lines[start].strip().strip("|").split("|")]
    i = start + 2  # skip header + separator

    rows: list[dict[str, Any]] = [
        {
            "type": "tableRow",
            "content": [
                {
                    "type": "tableHeader",
                    "content": [
                        {"type": "paragraph", "content": _parse_inline(h)}
                    ],
                }
                for h in header_cells
            ],
        }
    ]

    while i < len(lines) and "|" in lines[i] and lines[i].strip():
        cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
        rows.append(
            {
                "type": "tableRow",
                "content": [
                    {
                        "type": "tableCell",
                        "content": [
                            {"type": "paragraph", "content": _parse_inline(c)}
                        ],
                    }
                    for c in cells
                ],
            }
        )
        i += 1

    return {"type": "table", "content": rows}, i


def _parse_list(
    lines: list[str], start: int, ordered: bool
) -> tuple[list[dict[str, Any]], int]:
    """Parse a bullet or ordered list (with nesting). Returns ``(items, next_index)``."""
    items: list[dict[str, Any]] = []
    pat = _ORDERED_RE if ordered else _BULLET_RE

    first_m = pat.match(lines[start])
    if not first_m:
        return items, start

    base_indent = len(first_m.group(1))
    i = start

    while i < len(lines):
        line = lines[i]

        # Blank line — list ends unless a subsequent line continues it
        if not line.strip():
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and (
                _BULLET_RE.match(lines[j]) or _ORDERED_RE.match(lines[j])
            ):
                indent_m = re.match(r"^(\s*)", lines[j])
                if indent_m and len(indent_m.group(1)) >= base_indent:
                    i = j
                    continue
            break

        m = pat.match(line)
        bm = _BULLET_RE.match(line)
        om = _ORDERED_RE.match(line)

        if m:
            indent = len(m.group(1))
            if indent < base_indent:
                break
            if indent > base_indent:
                # Nested list of same type
                nested, i = _parse_list(lines, i, ordered)
                lt = "orderedList" if ordered else "bulletList"
                if items:
                    items[-1]["content"].append({"type": lt, "content": nested})
                continue
            # Same-level item
            items.append(
                {
                    "type": "listItem",
                    "content": [
                        {"type": "paragraph", "content": _parse_inline(m.group(2))}
                    ],
                }
            )
            i += 1
        elif bm or om:
            # Different list type — could be nested
            any_m = bm or om
            indent = len(any_m.group(1))  # type: ignore[union-attr]
            if indent > base_indent:
                is_ord = om is not None
                nested, i = _parse_list(lines, i, is_ord)
                lt = "orderedList" if is_ord else "bulletList"
                if items:
                    items[-1]["content"].append({"type": lt, "content": nested})
                continue
            break
        else:
            break

    return items, i


# -- Top-level block parser --------------------------------------------------


def _parse_blocks(lines: list[str]) -> list[dict[str, Any]]:
    """Parse lines of markdown into a list of ADF block nodes."""
    content: list[dict[str, Any]] = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Blank line — skip
        if not stripped:
            i += 1
            continue

        # Fenced code block
        fm = _FENCE_OPEN_RE.match(stripped)
        if fm:
            lang = fm.group(1)
            code_lines: list[str] = []
            i += 1
            while i < len(lines) and not _FENCE_CLOSE_RE.match(lines[i].strip()):
                code_lines.append(lines[i])
                i += 1
            if i < len(lines):
                i += 1  # skip closing fence
            node: dict[str, Any] = {
                "type": "codeBlock",
                "content": [{"type": "text", "text": "\n".join(code_lines)}],
            }
            if lang:
                node["attrs"] = {"language": lang}
            content.append(node)
            continue

        # Horizontal rule
        if _RULE_RE.match(stripped):
            content.append({"type": "rule"})
            i += 1
            continue

        # Heading
        hm = _HEADING_RE.match(line)
        if hm:
            content.append(
                {
                    "type": "heading",
                    "attrs": {"level": len(hm.group(1))},
                    "content": _parse_inline(hm.group(2)),
                }
            )
            i += 1
            continue

        # Blockquote
        if _QUOTE_RE.match(stripped):
            qlines: list[str] = []
            while i < len(lines) and _QUOTE_RE.match(lines[i].strip()):
                qm = _QUOTE_RE.match(lines[i].strip())
                qlines.append(qm.group(1) if qm else "")
                i += 1
            inner = _parse_blocks(qlines)
            content.append(
                {
                    "type": "blockquote",
                    "content": inner
                    or [
                        {
                            "type": "paragraph",
                            "content": [{"type": "text", "text": ""}],
                        }
                    ],
                }
            )
            continue

        # Table (header row followed by separator row)
        if "|" in line and i + 1 < len(lines) and _is_table_sep(lines[i + 1]):
            tbl, i = _parse_table(lines, i)
            content.append(tbl)
            continue

        # Bullet list
        if _BULLET_RE.match(line):
            items, i = _parse_list(lines, i, ordered=False)
            if items:
                content.append({"type": "bulletList", "content": items})
            continue

        # Ordered list
        if _ORDERED_RE.match(line):
            items, i = _parse_list(lines, i, ordered=True)
            if items:
                content.append({"type": "orderedList", "content": items})
            continue

        # Paragraph (default) — collect consecutive non-blank, non-block-start lines
        para_lines: list[str] = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not _is_block_start(lines[i]):
            para_lines.append(lines[i])
            i += 1
        content.append(
            {
                "type": "paragraph",
                "content": _parse_inline(
                    " ".join(l.strip() for l in para_lines)
                ),
            }
        )

    return content


# -- Public API --------------------------------------------------------------


def markdown_to_adf(text: str) -> dict[str, Any]:
    """Convert a markdown string to an Atlassian Document Format document.

    Handles headings, paragraphs, bullet/ordered lists (nested), fenced code
    blocks, blockquotes, horizontal rules, tables, and common inline marks
    (bold, italic, code, strikethrough, links).

    Returns a complete ADF dict: ``{"type": "doc", "version": 1, ...}``.
    """
    if not text or not text.strip():
        return {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": text or ""}],
                }
            ],
        }

    blocks = _parse_blocks(text.split("\n"))
    if not blocks:
        blocks = [
            {"type": "paragraph", "content": [{"type": "text", "text": text}]}
        ]

    return {"type": "doc", "version": 1, "content": blocks}
