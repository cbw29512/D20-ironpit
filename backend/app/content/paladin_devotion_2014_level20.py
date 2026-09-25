from __future__ import annotations

from app.domain.progression import SavingThrowAdvantageGrant
from app.domain.timed_self_buffs import TimedEmanationDamage, TimedSelfBuffAction
from app.domain.weapons_base import DamageType

_ALL_SAVES = (
    "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma",
)


def holy_nimbus_2014() -> TimedSelfBuffAction:
    """Oath of Devotion capstone expressed entirely through timed universal primitives."""
    return TimedSelfBuffAction(
        id="holy-nimbus",
        name="Holy Nimbus",
        action_cost="action",
        resource_id="holy-nimbus",
        resource_cost=1,
        duration_rounds=10,
        saving_throw_advantage_grants=[
            SavingThrowAdvantageGrant(
                source_id="holy-nimbus",
                source_name="Holy Nimbus",
                abilities=list(_ALL_SAVES),
                requires_spell_effect=True,
                source_creature_types=["fiend", "undead"],
            ),
        ],
        start_turn_emanation_damage=TimedEmanationDamage(
            trigger="enemy_turn_start",
            radius_ft=30,
            fixed_damage=10,
            damage_type=DamageType.RADIANT,
        ),
        expiry_timing="source_turn_start",
        priority=120,
        animation="holy-nimbus",
    )
