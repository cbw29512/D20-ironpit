"""2014 Fire Aura: source-turn-start emanation + contact/melee-hit retaliation.

Universal binding driven by printed source text. No monster-name dispatch.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.domain.timed_aura_components import TimedEmanationDamage
from app.domain.timed_self_buffs import MeleeHitRetaliation, TimedSelfBuffAction
from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)

_AURA = re.compile(
    r"At the start of each of the .+? turns, each creature within "
    r"(?P<radius>\d+) feet of it takes \d+ \((?P<count>\d+)d(?P<size>\d+)\) "
    r"(?P<type>fire|acid) damage",
    re.IGNORECASE,
)
_CONTACT = re.compile(
    r"A creature that touches the .+? or hits it with a melee attack "
    r"while within (?P<reach>\d+) feet of it takes "
    r"\d+ \((?P<count>\d+)d(?P<size>\d+)\) (?P<type>fire|acid) damage\b",
    re.IGNORECASE,
)


def fire_aura_action_2014(monster: SourceMonster2014) -> list[TimedSelfBuffAction]:
    """Bind a complete Fire Aura trait to passive emanation + contact retaliation."""
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
        aura = _AURA.search(body)
        contact = _CONTACT.search(body)
        if aura is None or contact is None:
            return []
        if aura.group("type").lower() != contact.group("type").lower():
            return []
        damage_type = DamageType(aura.group("type").lower())
        return [TimedSelfBuffAction(
            id="fire-aura",
            name="Fire Aura",
            activation_timing="passive",
            melee_hit_retaliation=MeleeHitRetaliation(
                range_ft=int(contact.group("reach")),
                dice_count=int(contact.group("count")),
                dice_size=int(contact.group("size")),
                damage_type=damage_type,
                on_contact=True,
            ),
            start_turn_emanation_damage=TimedEmanationDamage(
                trigger="source_turn_start",
                radius_ft=int(aura.group("radius")),
                dice_count=int(aura.group("count")),
                dice_size=int(aura.group("size")),
                damage_type=damage_type,
            ),
        )]
    except Exception:
        logger.exception("Failed 2014 Fire Aura binding for %s.", monster.name)
        raise
