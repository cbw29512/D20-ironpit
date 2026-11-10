"""2014 Fire Aura composes existing passive damage mechanics from exact source."""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.timed_aura_components import TimedEmanationDamage
from app.domain.timed_self_buffs import MeleeHitRetaliation, TimedSelfBuffAction
from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)

_FULL_SOURCE = re.compile(
    r"At the start of each of the (?P<owner>[A-Za-z][A-Za-z' -]*)'s turns, "
    r"each creature within (?P<radius>\d+) feet of it takes (?P<average>\d+) "
    r"\((?P<count>\d+)d(?P<size>\d+)\) (?P<type>fire|acid) damage, and "
    r"flammable objects in the aura that aren't being worn or carried ignite\. "
    r"A creature that touches the (?P=owner) or hits it with a melee attack "
    r"while within (?P<reach>\d+) feet of it takes (?P<contact_average>\d+) "
    r"\((?P<contact_count>\d+)d(?P<contact_size>\d+)\) "
    r"(?P<contact_type>fire|acid) damage\.",
    re.IGNORECASE,
)


def fire_aura_action_2014(monster: SourceMonster2014) -> list[TimedSelfBuffAction]:
    """Prove both clauses; source retains the object ignition metadata."""
    try:
        label = "Fire Aura"
        if label not in monster.trait_names:
            return []
        printed = source_sections_2014(
            monster.source_traits, include_continuations=True,
        ).get(label, "")
        match = _FULL_SOURCE.fullmatch(printed)
        if match is None:
            return []
        m = match.groupdict()
        count, size = int(m["count"]), int(m["size"])
        contact_count, contact_size = int(m["contact_count"]), int(m["contact_size"])
        if (
            not 1 <= count <= 40 or not 2 <= size <= 100
            or not 1 <= contact_count <= 40 or not 2 <= contact_size <= 100
            or int(m["average"]) != count * (size + 1) // 2
            or int(m["contact_average"]) != contact_count * (contact_size + 1) // 2
            or m["type"].casefold() != m["contact_type"].casefold()
        ):
            return []
        damage_type = DamageType(m["type"].casefold())
        return [TimedSelfBuffAction(
            id="fire-aura", name=label, activation_timing="passive",
            melee_hit_retaliation=MeleeHitRetaliation(
                range_ft=int(m["reach"]), dice_count=contact_count,
                dice_size=contact_size, damage_type=damage_type, on_contact=True,
            ),
            start_turn_emanation_damage=TimedEmanationDamage(
                trigger="source_turn_start", radius_ft=int(m["radius"]),
                dice_count=count, dice_size=size, damage_type=damage_type,
            ),
        )]
    except Exception:
        logger.exception("2014 Fire Aura source binding failed for %s.", monster.id)
        raise
