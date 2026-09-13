from __future__ import annotations

import re

from app.domain.start_turn_damage import StartTurnRelationshipDamage

_BARBS = re.compile(
    r"Barbed Hide\.\s*At the start of each of its turns, the [^.]+ deals (?P<avg>\d+) "
    r"\((?P<count>\d+)d(?P<size>\d+)(?:\s*\+\s*(?P<bonus>\d+))?\) (?P<dtype>\w+) damage "
    r"to any creature grappling it\.",
    re.I,
)


def start_turn_relationship_damage_2014(source_traits: str | None) -> list[StartTurnRelationshipDamage]:
    if not source_traits or "Barbed Hide." not in source_traits:
        return []
    text = re.sub(r"<[^>]+>", "", source_traits)
    match = _BARBS.search(text)
    if match is None:
        raise ValueError("Barbed Hide source text is not a supported start-turn damage shape.")
    return [StartTurnRelationshipDamage(
        id="barbed-hide", name="Barbed Hide", target_relationship="grapplers",
        dice_count=int(match.group("count")), dice_size=int(match.group("size")),
        damage_bonus=int(match.group("bonus") or 0), damage_type=match.group("dtype").lower(),
    )]
