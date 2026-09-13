from __future__ import annotations

import html
import re

_RELENTLESS = re.compile(
    r"Relentless\s*\(Recharges after a Short or Long Rest\).*?takes\s+(\d+)\s+damage or less\s+"
    r"that would reduce it to 0 hit points, it is reduced to 1 hit point instead",
    re.I | re.S,
)


def parse_zero_hp_prevention(source_traits: str | None) -> dict | None:
    text = re.sub(r"<[^>]+>", " ", html.unescape(source_traits or ""))
    text = re.sub(r"\s+", " ", text).strip()
    match = _RELENTLESS.search(text)
    if not match:
        return None
    return {
        "resource_id": "relentless",
        "max_trigger_damage": int(match.group(1)),
        "resulting_hp": 1,
    }
