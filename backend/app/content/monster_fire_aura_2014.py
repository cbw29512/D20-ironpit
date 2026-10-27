from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.domain.timed_aura_components import TimedEmanationDamage
from app.domain.timed_self_buffs import MeleeHitRetaliation, TimedSelfBuffAction
from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)

_START = re.compile(
    r"At the start of each of the .+? turns, each creature within (?P<radius>\d+) feet of it takes "
    r"\d+ \((?P<count>\d+)d(?P<size>\d+)\) (?P<type>fire) damage",
    re.IGNORECASE | re.DOTALL,
)
_CONTACT = re.compile(
    r"A creature that touches the .+? or hits it with a melee attack "
    r"while within (?P<reach>\d+) feet of it takes "
    r"\d+ \((?P<count>\d+)d(?P<size>\d+)\) (?P<type>fire) damage",
    re.IGNORECASE | re.DOTALL,
)


def fire_aura_2014(monster: SourceMonster2014) -> list[TimedSelfBuffAction]:
    """Bind printed Fire Aura as passive start-turn emanation + contact retaliation."""
    try:
        if "Fire Aura" not in monster.trait_names:
            return []
        source = monster.source_traits or ""
        heading = re.compile(
            r"<strong>Fire Aura\.</strong>(?P<body>.*?)(?=<strong>|\Z)",
            re.IGNORECASE | re.DOTALL,
        )
        section = heading.search(source)
        if section is None:
            return []
        body = section.group("body")
        start = _START.search(body)
        contact = _CONTACT.search(body)
        if start is None or contact is None or start.group("type") != "fire" or contact.group("type") != "fire":
            return []
        if start.group("radius") != contact.group("reach") or start.group("count") != contact.group("count") or start.group("size") != contact.group("size"):
            return []
        radius = int(start.group("radius"))
        return [TimedSelfBuffAction(
            id="fire-aura",
            name="Fire Aura",
            activation_timing="passive",
            start_turn_emanation_damage=TimedEmanationDamage(
                trigger="enter_or_start",
                radius_ft=radius,
                dice_count=int(start.group("count")),
                dice_size=int(start.group("size")),
                damage_type=DamageType.FIRE,
            ),
            melee_hit_retaliation=MeleeHitRetaliation(
                range_ft=radius,
                dice_count=int(contact.group("count")),
                dice_size=int(contact.group("size")),
                damage_type=DamageType.FIRE,
                on_contact=True,
            ),
        )]
    except Exception:
        logger.exception("Failed 2014 Fire Aura binding for %s.", monster.name)
        raise
