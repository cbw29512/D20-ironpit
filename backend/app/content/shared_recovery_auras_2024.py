from __future__ import annotations

import logging

from app.domain.friendly_combat_auras import (
    TimedFriendlyRecoveryAura,
    TimedFriendlyWeaponDamageAura,
)
from app.domain.timed_self_buffs import TimedSelfBuffAction
from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)


def crusaders_mantle_2024() -> TimedSelfBuffAction:
    """2024 Crusader's Mantle: 30-ft emanation, extra 1d4 Radiant on weapon/Unarmed hits."""
    try:
        return TimedSelfBuffAction(
            id="crusaders-mantle",
            name="Crusader's Mantle",
            action_cost="action",
            resource_id="spell-slot-3",
            duration_rounds=10,
            concentration=True,
            friendly_weapon_damage_aura=TimedFriendlyWeaponDamageAura(
                radius_ft=30,
                dice_count=1,
                dice_size=4,
                damage_type=DamageType.RADIANT,
            ),
            animation="buff",
        )
    except Exception:
        logger.exception("Failed to build 2024 Crusader's Mantle.")
        raise


def aura_of_vitality_2024() -> TimedSelfBuffAction:
    """2024 Aura of Vitality: 30-ft emanation, 2d6 HP on create and each source turn start."""
    try:
        return TimedSelfBuffAction(
            id="aura-of-vitality",
            name="Aura of Vitality",
            action_cost="action",
            resource_id="spell-slot-3",
            duration_rounds=10,
            concentration=True,
            friendly_recovery_aura=TimedFriendlyRecoveryAura(
                radius_ft=30,
                heal_dice_count=2,
                heal_dice_size=6,
                heal_on_create=True,
                heal_on_source_turn_start=True,
            ),
            animation="healing",
        )
    except Exception:
        logger.exception("Failed to build 2024 Aura of Vitality.")
        raise


def aura_of_life_2024() -> TimedSelfBuffAction:
    """2024 Aura of Life: necrotic Resistance, HP-max lock, 0-HP ally start-of-turn 1 HP."""
    try:
        return TimedSelfBuffAction(
            id="aura-of-life",
            name="Aura of Life",
            action_cost="action",
            resource_id="spell-slot-4",
            duration_rounds=100,
            concentration=True,
            damage_resistances=[DamageType.NECROTIC],
            friendly_recovery_aura=TimedFriendlyRecoveryAura(
                radius_ft=30,
                zero_hp_ally_start_heal=1,
                necrotic_resistance=True,
                prevent_hp_maximum_reduction=True,
            ),
            animation="buff",
        )
    except Exception:
        logger.exception("Failed to build 2024 Aura of Life.")
        raise


def paladin_2024_recovery_auras(level: int) -> list[TimedSelfBuffAction]:
    try:
        auras: list[TimedSelfBuffAction] = []
        if level >= 9:
            auras.append(aura_of_vitality_2024())
        if level >= 11:
            auras.append(crusaders_mantle_2024())
        if level >= 15:
            auras.append(aura_of_life_2024())
        return auras
    except Exception:
        logger.exception("Failed to build 2024 Paladin recovery auras at level %s.", level)
        raise
