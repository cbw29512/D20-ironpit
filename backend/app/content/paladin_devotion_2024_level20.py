from __future__ import annotations

import logging

from app.content.character_math import proficiency_bonus
from app.domain.progression import SavingThrowAdvantageGrant
from app.domain.resource_conversion import ResourceConversionAction
from app.domain.timed_self_buffs import TimedEmanationDamage, TimedSelfBuffAction
from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)

_ALL_SAVES = (
    "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma",
)


def holy_nimbus_2024(level: int, charisma_modifier: int) -> TimedSelfBuffAction:
    """2024 Holy Nimbus: Bonus Action, 10 minutes, CHA+PB radiant, Fiend/Undead Holy Ward."""
    try:
        return TimedSelfBuffAction(
            id="holy-nimbus",
            name="Holy Nimbus",
            action_cost="bonus_action",
            resource_id="holy-nimbus",
            resource_cost=1,
            duration_rounds=100,
            saving_throw_advantage_grants=[
                SavingThrowAdvantageGrant(
                    source_id="holy-nimbus",
                    source_name="Holy Nimbus",
                    abilities=list(_ALL_SAVES),
                    requires_spell_effect=False,
                    source_creature_types=["fiend", "undead"],
                ),
            ],
            start_turn_emanation_damage=TimedEmanationDamage(
                trigger="enemy_turn_start",
                radius_ft=30 if level >= 18 else 10,
                fixed_damage=charisma_modifier + proficiency_bonus(level),
                damage_type=DamageType.RADIANT,
            ),
            expiry_timing="source_turn_start",
            priority=120,
            animation="holy-nimbus",
        )
    except Exception:
        logger.exception("Failed to build 2024 Holy Nimbus at level %s.", level)
        raise


def holy_nimbus_restore_2024() -> ResourceConversionAction:
    try:
        return ResourceConversionAction(
            id="holy-nimbus-restore",
            name="Holy Nimbus",
            action_cost="none",
            source_resource_id="spell-slot-5",
            source_cost=1,
            target_resource_id="holy-nimbus",
            target_gain=1,
            requires_target_empty=True,
            automation="when-target-empty",
            source="D&D Beyond Basic Rules 2024: Oath of Devotion, Holy Nimbus",
        )
    except Exception:
        logger.exception("Failed to build 2024 Holy Nimbus slot restore.")
        raise
