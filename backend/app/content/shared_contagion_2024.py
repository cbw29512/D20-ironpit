from __future__ import annotations

import logging

from app.domain.save_effects import FailedSaveTimedEffect
from app.domain.spell_modifiers import SpellModifierEffect
from app.domain.spells import SpellSaveAction

logger = logging.getLogger(__name__)


def contagion_2024(save_dc: int) -> SpellSaveAction:
    """2024 Contagion: touch Con save, fail-only 11d8 Necrotic, Poisoned, Con-save Disadvantage."""
    try:
        if not 1 <= save_dc <= 40:
            raise ValueError("Contagion requires a certified spell save DC.")
        return SpellSaveAction(
            id="contagion",
            name="Contagion",
            level=5,
            action_cost="action",
            range_ft=5,
            save_ability="constitution",
            dc=save_dc,
            damage_dice_count=11,
            damage_dice_size=8,
            damage_type="necrotic",
            success_damage="none",
            duration_minutes=10080,
            failed_save_timed_effect=FailedSaveTimedEffect(
                effect_id="poisoned",
                duration_rounds=100800,
                expiry_timing="target_turn_end",
                repeat_save_ability="constitution",
                repeat_save_dc=save_dc,
                repeat_save_timing="target_turn_end",
                repeat_save_failures_to_lock=3,
            ),
            failed_save_modifier_effects=[
                SpellModifierEffect(
                    kind="saving-throw-disadvantage",
                    save_ability="constitution",
                ),
            ],
            animation="contagion",
        )
    except Exception:
        logger.exception("Failed to build 2024 Contagion.")
        raise
