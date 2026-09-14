from __future__ import annotations

import html
import re

from app.domain.reactive_damage import MeleeHitReactiveDamage

_HEATED_BODY = re.compile(
    r"Heated Body\.\s*A creature that touches the [A-Za-z' -]+ or hits it with a melee attack while within "
    r"(?P<range>\d+) feet of it takes \d+ \((?P<count>\d+)d(?P<size>\d+)(?:\s*([+-])\s*(\d+))?\) "
    r"(?P<damage_type>[A-Za-z]+) damage",
    re.I,
)


def _plain(value: str | None) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def reactive_melee_damage_2014(source_traits: str | None) -> list[MeleeHitReactiveDamage]:
    match = _HEATED_BODY.search(_plain(source_traits))
    if match is None:
        return []
    sign, bonus = match.group(4), match.group(5)
    modifier = int(bonus or 0) * (-1 if sign == "-" else 1)
    return [MeleeHitReactiveDamage(
        id="heated-body", range_ft=int(match.group("range")),
        dice_count=int(match.group("count")), dice_size=int(match.group("size")),
        damage_bonus=modifier, damage_type=match.group("damage_type").lower(),
    )]
