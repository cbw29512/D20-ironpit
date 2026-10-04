from __future__ import annotations

import logging

from app.content.hero_combat_feature_registry import compile_progression_feature_fields
from app.content.ranger_hunter_2014_level3 import colossus_slayer_2014
from app.domain.progression import ProgressionCombatFeatures, SavingThrowAdvantageGrant
from app.domain.reactions import IncomingDamageTypeResistanceReaction

logger = logging.getLogger(__name__)
_ABILITIES = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]


def build_ranger_2024_progression(level: int) -> ProgressionCombatFeatures:
    try:
        boon = compile_progression_feature_fields(
            ["boon-combat-prowess"] if level >= 19 else [], level,
        )
        return ProgressionCombatFeatures(
            once_per_turn_weapon_hit_damage_rider=colossus_slayer_2014() if level >= 3 else None,
            opportunity_attacks_against_disadvantage=level >= 7,
            concentration_damage_immune_effect_ids=["hunters-mark"] if level >= 13 else [],
            hunters_mark_splash_range_ft=30 if level >= 11 else 0,
            advantage_against_marked_effect_id="hunters-mark" if level >= 17 else None,
            saving_throw_advantage_grants=[
                SavingThrowAdvantageGrant(
                    source_id="fey-ancestry",
                    source_name="Fey Ancestry",
                    abilities=_ABILITIES,
                    required_effect_tags=["charm"],
                ),
            ],
            **boon,
        )
    except Exception:
        logger.exception("Failed to build 2024 Ranger progression at level %s.", level)
        raise


def superior_hunters_defense_2024(level: int) -> IncomingDamageTypeResistanceReaction | None:
    try:
        if level < 15:
            return None
        return IncomingDamageTypeResistanceReaction(
            source_id="superior-hunters-defense",
            source_name="Superior Hunter's Defense",
        )
    except Exception:
        logger.exception("Failed to compile Superior Hunter's Defense at level %s.", level)
        raise
