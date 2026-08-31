from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

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


def _ends_with_monster_name(value: object, monster_name: str) -> bool:
    """Match a leaked terminal monster heading without treating interior references as contamination."""
    text = str(value).strip()
    if not text:
        return False
    return bool(re.search(rf"(?:^|\s){re.escape(monster_name)}\s*$", text, re.IGNORECASE))


def neighbor_name_bleed_issues(row: dict[str, object], monster_names: set[str]) -> list[str]:
    """Detect a bare neighboring monster heading copied onto both raw and structured source text."""
    own_name = str(row.get("name", "")).strip()
    raw_text = row.get("rawText", "")
    issues: list[str] = []
    for candidate in monster_names:
        if not candidate or candidate.casefold() == own_name.casefold():
            continue
        if not _ends_with_monster_name(raw_text, candidate):
            continue
        if any(_ends_with_monster_name(row.get(field, ""), candidate) for field in _STRUCTURED_FIELDS):
            issues.append(f"neighbor-name-bleed:{candidate}")
    return sorted(issues)


def validate_monster_source_integrity(rows: list[dict[str, object]]) -> None:
    """Fail closed when vendored SRD records contain parser contamination."""
    try:
        monster_names = {str(row.get("name", "")).strip() for row in rows if str(row.get("name", "")).strip()}
        failures: dict[str, list[str]] = {}
        for row in rows:
            issues = source_integrity_issues(row)
            issues.extend(neighbor_name_bleed_issues(row, monster_names))
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
