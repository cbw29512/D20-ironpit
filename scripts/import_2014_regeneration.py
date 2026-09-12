from __future__ import annotations

import html
import re

_DAMAGE_TYPES = {
    "acid", "bludgeoning", "cold", "fire", "force", "lightning", "necrotic",
    "piercing", "poison", "psychic", "radiant", "slashing", "thunder",
}
_TRAIT = re.compile(r"<strong>\s*Regeneration\.\s*</strong>(.*?)(?=</p>|<strong>|$)", re.I | re.S)
_AMOUNT = re.compile(r"regains\s+(\d+)\s+hit points? at the start of (?:its|his|her) turn", re.I)
_SUPPRESSION = re.compile(r"takes\s+([^.]*)damage[^.]*trait doesn't function at the start of", re.I)


def _plain(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def parse_regeneration(source_traits: str | None) -> dict | None:
    raw = source_traits or ""
    match = _TRAIT.search(raw)
    if match is None:
        return None
    text = _plain(match.group(1))
    amount = _AMOUNT.search(text)
    if amount is None:
        return None
    suppression = _SUPPRESSION.search(text)
    damage_types = []
    if suppression:
        lowered = suppression.group(1).lower()
        damage_types = sorted(kind for kind in _DAMAGE_TYPES if re.search(rf"\b{kind}\b", lowered))
    return {
        "amount": int(amount.group(1)),
        "requires_positive_hp": bool(re.search(r"if (?:it|the [a-z' -]+) has at least 1 hit point", text, re.I)),
        "suppressed_by_damage_types": damage_types,
        "survives_zero_until_turn": bool(re.search(r"dies only if it starts its turn with 0 hit points and doesn't regenerate", text, re.I)),
    }
