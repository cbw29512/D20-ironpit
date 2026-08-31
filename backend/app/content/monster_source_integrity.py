from __future__ import annotations

import re

_STRUCTURED_FIELDS = ("traits", "actions", "bonusActions", "reactions", "legendaryActions")
_STAT_BLOCK_HEADER = re.compile(
    r"\bAC\s+\d+(?:\s*\([^)]*\))?\s+Initiative\s+[+-]?\d+\s*\(\d+\)\s+HP\s+\d+",
    re.IGNORECASE,
)


def source_integrity_issues(row: dict[str, object]) -> list[str]:
    """Detect a second stat block swallowed into one parsed monster record."""
    issues: list[str] = []
    for field in _STRUCTURED_FIELDS:
        if _STAT_BLOCK_HEADER.search(str(row.get(field, ""))):
            issues.append(f"embedded-stat-block:{field}")
    raw_text = str(row.get("rawText", ""))
    if len(_STAT_BLOCK_HEADER.findall(raw_text)) > 1:
        issues.append("embedded-stat-block:rawText")
    return issues


def validate_monster_source_integrity(rows: list[dict[str, object]]) -> None:
    failures = {
        str(row.get("name", row.get("id", "unknown"))): source_integrity_issues(row)
        for row in rows
        if source_integrity_issues(row)
    }
    if failures:
        details = "; ".join(f"{name}={','.join(issues)}" for name, issues in failures.items())
        raise RuntimeError(f"SRD monster parser contamination detected: {details}")
