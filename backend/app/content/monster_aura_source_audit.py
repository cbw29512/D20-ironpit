from __future__ import annotations

import re

from app.domain.auras import EndTurnDamageAura
from app.domain.models import CombatantTemplate

_FIRE_AURA = re.compile(
    r"Fire Aura\. At the end of each of the (?P<owner>[a-z]+)[’']s turns, each creature(?P<choice> of the [a-z]+[’']s choice)? "
    r"in a (?P<radius>\d+)-foot Emanation originating from the [a-z]+ takes \d+ \((?P<count>\d+)d(?P<size>\d+)"
    r"(?:\s*(?P<sign>[+-])\s*(?P<bonus>\d+))?\) (?P<type>Acid|Bludgeoning|Cold|Fire|Force|Lightning|Necrotic|Piercing|Poison|Psychic|Radiant|Slashing|Thunder) damage"
    r"(?P<incap> unless the [a-z]+ has the Incapacitated condition)?\.", re.I,
)


def parse_fire_aura(source_traits: object) -> EndTurnDamageAura | None:
    text = str(source_traits or "")
    if "Fire Aura." not in text:
        return None
    match = _FIRE_AURA.search(text)
    if match is None:
        raise ValueError("Fire Aura source text is outside the supported end-turn damage grammar.")
    tail = text[match.end():].lstrip()
    if tail and not re.match(r"[A-Z][A-Za-z’' -]+\. ", tail):
        raise ValueError("Fire Aura has unsupported trailing semantics.")
    bonus = int(match.group("bonus") or 0) * (-1 if match.group("sign") == "-" else 1)
    return EndTurnDamageAura(
        name="Fire Aura", radius_ft=int(match.group("radius")), dice_count=int(match.group("count")),
        dice_size=int(match.group("size")), damage_bonus=bonus, damage_type=match.group("type").lower(),
        target_mode="enemies" if match.group("choice") else "all_others",
        disabled_while_incapacitated=bool(match.group("incap")),
    )


def aura_issues(template: CombatantTemplate, row: dict[str, object]) -> list[str]:
    try:
        expected = parse_fire_aura(row.get("traits", ""))
    except ValueError:
        return ["aura-source-unsupported:fire-aura"]
    actual = template.end_turn_damage_aura
    if expected is None and actual is None:
        return []
    if expected is None:
        return ["aura-source-missing:fire-aura"]
    if actual is None:
        return ["aura-runtime-missing:fire-aura"]
    return [] if actual == expected else ["aura-runtime-mismatch:fire-aura"]
