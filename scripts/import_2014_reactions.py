from __future__ import annotations

import html
import re


def _plain(value: str | None) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def parse_parry_ac_bonus(source_reactions: str | None) -> int | None:
    text = _plain(source_reactions)
    if not re.search(r"\bParry\b", text, re.I):
        return None
    match = re.search(r"\badds\s+(\d+)\s+to\s+(?:its|his|her)\s+AC\b", text, re.I)
    return int(match.group(1)) if match else None
