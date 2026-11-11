"""Recognize a complete printed 2014 hostile-space ignition rider.

Source names locate the printed paragraph. The combat engine uses only the
generic hostile-space-entry specification and never tests monster identity.
"""
from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.hostile_space_entry_damage import HostileSpaceEntryDamage
from app.domain.recurring_damage import OnHitRecurringDamage
from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)

_PRINTED_FIRE_FORM = (
    "the elemental can move through a space as narrow as 1 inch wide without squeezing. "
    "a creature that touches the elemental or hits it with a melee attack while "
    "within 5 feet of it takes 5 (1d10) fire damage. "
    "in addition, the elemental can enter a hostile creature's space and stop there. "
    "the first time it enters a creature's space on a turn, that creature takes "
    "5 (1d10) fire damage and catches fire; until someone takes an action to "
    "douse the fire, the creature takes 5 (1d10) fire damage at the start of each of its turns."
)


def fire_form_space_entry_2014(monster: SourceMonster2014) -> HostileSpaceEntryDamage | None:
    """Return generic parameters only when every Fire Form source clause agrees."""
    try:
        if "Fire Form" not in monster.trait_names:
            return None
        printed = source_sections_2014(
            monster.source_traits, include_continuations=True,
        ).get("Fire Form", "")
        normalized = " ".join(printed.casefold().replace("’", "'").split())
        if normalized != _PRINTED_FIRE_FORM:
            return None
        return HostileSpaceEntryDamage(
            dice_count=1, dice_size=10, damage_type=DamageType.FIRE,
            recurring_damage=OnHitRecurringDamage(
                effect_id="burning", dice_count=1, dice_size=10,
                damage_type=DamageType.FIRE, tick_timing="target_turn_start",
                stacking="nonstacking", ends_if_source_dead=False,
                removal_action_ids=["douse-fire"],
            ),
        )
    except Exception:
        logger.exception("Failed to bind 2014 source-verified hostile-space ignition for %s.", monster.id)
        raise
