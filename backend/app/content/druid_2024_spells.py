from __future__ import annotations

import logging

from app.content.offensive_spell_effects import cantrip_damage_dice
from app.domain.spells import DefensiveSpellAction, SpellAttackAction, SpellModifierEffect

logger = logging.getLogger(__name__)


def build_poison_spray_2024(attack_bonus: int, character_level: int) -> SpellAttackAction:
    """Explicit 2024 Poison Spray fingerprint."""
    try:
        return SpellAttackAction(
            id="poison-spray",
            name="Poison Spray",
            level=0,
            action_cost="action",
            attack_kind="ranged",
            range_ft=30,
            attack_bonus=attack_bonus,
            damage_dice_count=cantrip_damage_dice(character_level),
            damage_dice_size=12,
            damage_type="poison",
            animation="spell-attack",
            source="D&D Beyond Basic Rules 2024: Poison Spray",
        )
    except Exception:
        logger.exception("Failed to build 2024 Poison Spray at level %s.", character_level)
        raise


def build_longstrider_2024() -> DefensiveSpellAction:
    """Explicit 2024 Longstrider fingerprint."""
    try:
        return DefensiveSpellAction(
            id="longstrider",
            name="Longstrider",
            level=1,
            action_cost="action",
            range_ft=5,
            duration_minutes=60,
            target_policy="friendly",
            target_count=1,
            target_count_per_slot_above=1,
            modifier_effects=[SpellModifierEffect(kind="speed", flat_bonus=10)],
            concentration=False,
            priority=15,
            animation="longstrider",
            source="D&D Beyond Basic Rules 2024: Longstrider",
        )
    except Exception:
        logger.exception("Failed to build 2024 Longstrider.")
        raise
