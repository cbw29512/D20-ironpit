from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.domain.damage_sources import DamageTakenTimedEffect
from app.domain.weapons import DamageType

logger = logging.getLogger(__name__)
_FIRE_DISADVANTAGE_TRAITS = {
    "Fear of Fire": "fear-of-fire",
    "Aversion of Fire": "aversion-of-fire",
}


def _fire_disadvantage_source_matches(monster: SourceMonster2014, trait_name: str) -> bool:
    text = " ".join((monster.source_traits or "").casefold().split())
    return all(fragment in text for fragment in (
        trait_name.casefold(),
        "takes fire damage",
        "disadvantage on attack rolls and ability checks",
        "until the end of its next turn",
    ))


def damage_taken_timed_effects_2014(monster: SourceMonster2014) -> list[DamageTakenTimedEffect]:
    """Bind exact printed typed-damage triggers to universal timed roll scopes."""
    try:
        matched = [
            (trait_name, source_slug)
            for trait_name, source_slug in _FIRE_DISADVANTAGE_TRAITS.items()
            if trait_name in monster.trait_names
        ]
        effects: list[DamageTakenTimedEffect] = []
        for trait_name, source_slug in matched:
            if not _fire_disadvantage_source_matches(monster, trait_name):
                raise ValueError(
                    f"{monster.name} {trait_name} source text does not match supported semantics."
                )
            effects.append(DamageTakenTimedEffect(
                source_id=f"{monster.id}-{source_slug}",
                source_name=trait_name,
                trigger_damage_type=DamageType.FIRE,
                effect_id="damage-triggered-disadvantage",
                target_turns=1,
                attack_roll_disadvantage=True,
                ability_check_disadvantage=True,
            ))
        return effects
    except Exception:
        logger.exception("Failed to bind 2014 typed-damage timed effects for %s.", monster.name)
        raise
