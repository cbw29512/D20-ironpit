from __future__ import annotations

import logging
import re

from app.content.monster_source_boundaries import (
    STRUCTURED_FIELDS,
    ends_with_heading,
    longest_terminal_monster_name,
    terminal_bare_heading,
)

logger = logging.getLogger(__name__)
_STAT_BLOCK_HEADER = re.compile(
    r"\bAC\s+\d+(?:\s*\([^)]*\))?\s+Initiative\s+[+-]?\d+\s*\(\d+\)\s+HP\s+\d+",
    re.IGNORECASE,
)


def source_integrity_issues(row: dict[str, object]) -> list[str]:
    """Detect a second stat block swallowed into one parsed monster record."""
    issues: list[str] = []
    for field in STRUCTURED_FIELDS:
        if _STAT_BLOCK_HEADER.search(str(row.get(field, ""))):
            issues.append(f"embedded-stat-block:{field}")
    raw_text = str(row.get("rawText", ""))
    if len(_STAT_BLOCK_HEADER.findall(raw_text)) > 1:
        issues.append("embedded-stat-block:rawText")
    return issues


def neighbor_name_bleed_issues(row: dict[str, object], monster_names: set[str]) -> list[str]:
    """Detect the longest exact monster heading copied onto raw and structured source text."""
    own_name = str(row.get("name", "")).strip()
    heading = longest_terminal_monster_name(
        row.get("rawText", ""), monster_names, exclude_name=own_name
    )
    if heading is None:
        return []
    if any(ends_with_heading(row.get(field, ""), heading) for field in STRUCTURED_FIELDS):
        return [f"neighbor-name-bleed:{heading}"]
    return []


def terminal_heading_bleed_issues(row: dict[str, object], monster_names: set[str]) -> list[str]:
    """Detect non-monster headings such as source section labels left at a stat-block boundary."""
    own_name = str(row.get("name", "")).strip()
    if longest_terminal_monster_name(row.get("rawText", ""), monster_names, exclude_name=own_name):
        return []
    heading = terminal_bare_heading(row.get("rawText", ""))
    if heading is None:
        return []
    matching = any(
        terminal_bare_heading(row.get(field, "")) == heading for field in STRUCTURED_FIELDS
    )
    return [f"terminal-heading-bleed:{heading}"] if matching else []


def validate_monster_source_integrity(rows: list[dict[str, object]]) -> None:
    """Fail closed when vendored SRD records contain parser contamination."""
    try:
        monster_names = {str(row.get("name", "")).strip() for row in rows if str(row.get("name", "")).strip()}
        failures: dict[str, list[str]] = {}
        for row in rows:
            issues = source_integrity_issues(row)
            issues.extend(neighbor_name_bleed_issues(row, monster_names))
            issues.extend(terminal_heading_bleed_issues(row, monster_names))
            if issues:
                name = str(row.get("name", row.get("id", "unknown")))
                failures[name] = issues
        if failures:
            details = "; ".join(f"{name}={','.join(issues)}" for name, issues in failures.items())
            raise RuntimeError(f"SRD monster parser contamination detected: {details}")
    except RuntimeError:
        raise
    except Exception as exc:
        logger.exception("Failed while validating SRD monster source integrity.")
        raise RuntimeError("SRD monster source integrity validation failed.") from exc
