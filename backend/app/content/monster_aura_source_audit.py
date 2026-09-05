from __future__ import annotations

import re

from app.domain.auras import EndTurnDamageAura, RollAdvantageAura
from app.domain.models import CombatantTemplate

_FIRE_AURA = re.compile(
    r"Fire Aura\. At the end of each of the (?P<owner>[a-z]+)[’']s turns, each creature(?P<choice> of the [a-z]+[’']s choice)? "
    r"in a (?P<radius>\d+)-foot Emanation originating from the [a-z]+ takes \d+ \((?P<count>\d+)d(?P<size>\d+)"
    r"(?:\s*(?P<sign>[+-])\s*(?P<bonus>\d+))?\) (?P<type>Acid|Bludgeoning|Cold|Fire|Force|Lightning|Necrotic|Piercing|Poison|Psychic|Radiant|Slashing|Thunder) damage"
    r"(?P<incap> unless the [a-z]+ has the Incapacitated condition)?\.", re.I,
)
_AUTHORITY_AURA = re.compile(
    r"Aura of Authority\. While in a (?P<radius>\d+)-foot Emanation originating from the (?P<owner>[a-z]+), "
    r"the (?P=owner) and its allies have Advantage on attack rolls and saving throws, provided the (?P=owner) doesn[’']t have the Incapacitated condition\.",
    re.I,
)
_CONNECTORS = frozenset({"a", "an", "and", "of", "or", "the", "to"})


def _starts_new_trait(tail: str) -> bool:
    sentence = tail.split(". ", 1)[0].rstrip(".").strip()
    words = sentence.split()
    return bool(words) and all(
        word.lower() in _CONNECTORS or re.fullmatch(r"[A-Z][A-Za-z’'\-]*", word)
        for word in words
    )


def parse_fire_aura(source_traits: object) -> EndTurnDamageAura | None:
    text = str(source_traits or "")
    if "Fire Aura." not in text:
        return None
    match = _FIRE_AURA.search(text)
    if match is None:
        raise ValueError("Fire Aura source text is outside the supported end-turn damage grammar.")
    tail = text[match.end():].lstrip()
    if tail and not _starts_new_trait(tail):
        raise ValueError("Fire Aura has unsupported trailing semantics.")
    bonus = int(match.group("bonus") or 0) * (-1 if match.group("sign") == "-" else 1)
    return EndTurnDamageAura(
        name="Fire Aura", radius_ft=int(match.group("radius")), dice_count=int(match.group("count")),
        dice_size=int(match.group("size")), damage_bonus=bonus, damage_type=match.group("type").lower(),
        target_mode="enemies" if match.group("choice") else "all_others",
        disabled_while_incapacitated=bool(match.group("incap")),
    )


def parse_authority_aura(source_traits: object) -> RollAdvantageAura | None:
    text = str(source_traits or "")
    if "Aura of Authority." not in text:
        return None
    match = _AUTHORITY_AURA.search(text)
    if match is None:
        raise ValueError("Aura of Authority source text is outside the supported roll-advantage grammar.")
    tail = text[match.end():].lstrip()
    if tail and not _starts_new_trait(tail):
        raise ValueError("Aura of Authority has unsupported trailing semantics.")
    return RollAdvantageAura(
        name="Aura of Authority", radius_ft=int(match.group("radius")),
        grants_attack_roll_advantage=True, grants_saving_throw_advantage=True,
        disabled_while_incapacitated=True,
    )


def _pair_issues(expected, actual, slug: str) -> list[str]:
    if expected is None and actual is None:
        return []
    if expected is None:
        return [f"aura-source-missing:{slug}"]
    if actual is None:
        return [f"aura-runtime-missing:{slug}"]
    return [] if actual == expected else [f"aura-runtime-mismatch:{slug}"]


def aura_issues(template: CombatantTemplate, row: dict[str, object]) -> list[str]:
    traits = row.get("traits", "")
    try:
        fire = parse_fire_aura(traits)
    except ValueError:
        return ["aura-source-unsupported:fire-aura"]
    try:
        authority = parse_authority_aura(traits)
    except ValueError:
        return ["aura-source-unsupported:aura-of-authority"]
    return [
        *_pair_issues(fire, template.end_turn_damage_aura, "fire-aura"),
        *_pair_issues(authority, template.roll_advantage_aura, "aura-of-authority"),
    ]
