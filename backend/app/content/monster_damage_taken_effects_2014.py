from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.domain.damage_taken_effects import DamageTakenTimedEffect
from app.domain.weapons import DamageType

logger = logging.getLogger(__name__)
_FEAR_OF_FIRE = "Fear of Fire"


def _fear_of_fire_source_matches(monster: SourceMonster2014) -> bool:
    text = " ".join((monster.source_traits or "").casefold().split())
    return all(fragment in text for fragment in (
        "fear of fire",
        "takes fire damage",
        "disadvantage on attack rolls and ability checks",
        "until the end of its next turn",
    ))


def damage_taken_timed_effects_2014(monster: SourceMonster2014) -> list[DamageTakenTimedEffect]:
    """Bind exact printed typed-damage triggers to universal timed roll scopes."""
    try:
        if _FEAR_OF_FIRE not in monster.trait_names:
            return []
        if not _fear_of_fire_source_matches(monster):
            raise ValueError(f"{monster.name} Fear of Fire source text does not match supported semantics.")
        return [DamageTakenTimedEffect(
            source_id=f"{monster.id}-fear-of-fire",
            source_name=_FEAR_OF_FIRE,
            trigger_damage_type=DamageType.FIRE,
            effect_id="damage-triggered-disadvantage",
            target_turns=1,
            attack_roll_disadvantage=True,
            ability_check_disadvantage=True,
        )]
    except Exception:
        logger.exception("Failed to bind 2014 typed-damage timed effects for %s.", monster.name)
        raise
