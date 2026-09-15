from __future__ import annotations

import html
import re

from app.domain.damage_triggers import DamageTriggeredRollPenalty
from app.domain.weapons import DamageType

_DAMAGE_TYPES = "acid|bludgeoning|cold|fire|force|lightning|necrotic|piercing|poison|psychic|radiant|slashing|thunder"
_ROLL_PENALTY = re.compile(
    rf"(?P<name>[A-Za-z][A-Za-z' -]+)\.\s*If the [A-Za-z' -]+ takes (?P<damage>{_DAMAGE_TYPES}) damage, "
    r"it has disadvantage on attack rolls and ability checks until the end of its next turn\.?",
    re.I,
)


def _plain(value: str | None) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def damage_triggered_roll_penalties_2014(source_traits: str | None) -> list[DamageTriggeredRollPenalty]:
    """Parse source-declared damage triggers that impose temporary roll Disadvantage."""
    profiles: list[DamageTriggeredRollPenalty] = []
    for match in _ROLL_PENALTY.finditer(_plain(source_traits)):
        profiles.append(DamageTriggeredRollPenalty(
            id=_slug(match.group("name")),
            damage_types=[DamageType(match.group("damage").lower())],
            attack_roll_disadvantage=True,
            ability_check_disadvantage=True,
        ))
    return profiles
