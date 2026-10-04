from __future__ import annotations

import logging

from app.domain.environment_context import TimedEnvironmentContextAura
from app.domain.models import DamageType
from app.domain.progression import SavingThrowAdvantageGrant
from app.domain.resource_conversion import ResourceConversionAction
from app.domain.timed_self_buffs import TimedEmanationDamage, TimedSelfBuffAction

logger = logging.getLogger(__name__)


def holy_nimbus_2024(charisma_modifier: int, proficiency_bonus: int) -> TimedSelfBuffAction:
    """Compose the 2024 Devotion capstone entirely from universal mechanics."""
    try:
        return TimedSelfBuffAction(
            id="holy-nimbus-2024",
            name="Holy Nimbus",
            action_cost="bonus_action",
            resource_id="holy-nimbus",
            resource_cost=1,
            duration_rounds=100,
            saving_throw_advantage_grants=[
                SavingThrowAdvantageGrant(
                    source_id="holy-nimbus-2024",
                    source_name="Holy Nimbus",
                    abilities=[
                        "strength", "dexterity", "constitution",
                        "intelligence", "wisdom", "charisma",
                    ],
                    source_creature_types=["fiend", "undead"],
                ),
            ],
            environment_context_aura=TimedEnvironmentContextAura(
                radius_ft=30,
                context_tags=["sunlight"],
            ),
            start_turn_emanation_damage=TimedEmanationDamage(
                trigger="enemy_turn_start",
                radius_ft=30,
                fixed_damage=charisma_modifier + proficiency_bonus,
                damage_type=DamageType.RADIANT,
            ),
            inactive_while_source_incapacitated=True,
            expiry_timing="source_turn_start",
            priority=130,
            animation="holy-nimbus",
        )
    except Exception:
        logger.exception("Failed to compose 2024 Holy Nimbus.")
        raise


def holy_nimbus_resource_conversions_2024() -> list[ResourceConversionAction]:
    try:
        return [ResourceConversionAction(
            id="restore-holy-nimbus-2024",
            name="Holy Nimbus (Restore Use)",
            action_cost="none",
            source_resource_id="spell-slot-5",
            source_cost=1,
            target_resource_id="holy-nimbus",
            target_gain=1,
            requires_target_empty=True,
            priority=120,
            source="D&D Beyond Basic Rules 2024: Oath of Devotion 20 — Holy Nimbus",
        )]
    except Exception:
        logger.exception("Failed to compose 2024 Holy Nimbus resource restoration.")
        raise
