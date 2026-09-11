from __future__ import annotations

import re

_HEADING = re.compile(
    r"^(?P<name>[A-Z][A-Za-z0-9’'\-]*(?:\s+(?:[A-Z][A-Za-z0-9’'\-]*|of|the|and|or)){0,5})"
    r"(?:\s+\((?P<limit>Recharge\s+\d(?:\s*[-–]\s*\d)?|\d+\s*/\s*Day)\))?$"
)


def promoted_save_heading(name: str, limit: str | None, lead: str | None) -> tuple[str, str | None, str]:
    """Prefer a nearer title-like sentence when the save regex began one sentence too early."""
    lead_text = str(lead or "").strip()
    match = _HEADING.fullmatch(lead_text)
    if match is None:
        return name.strip(), limit, lead_text
    return match.group("name").strip(), match.group("limit"), ""
