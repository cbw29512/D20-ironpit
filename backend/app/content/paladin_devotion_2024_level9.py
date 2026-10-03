from __future__ import annotations

import logging

from app.domain.actions import SavingThrowAction
from app.domain.effect_removal import EffectRemovalAction
from app.domain.save_effects import FailedSaveTimedEffect
from app.domain.spells import DefensiveSpellAction, SpellModifierEffect

logger = logging.getLogger(__name__)
_SOURCE = "D&D Beyond Basic Rules 2024"


def abjure_foes_2024(save_dc: int, charisma_modifier: int) -> SavingThrowAction:
    """Build the source-neutral data binding for 2024 Paladin Abjure Foes."""
    try:
        return SavingThrowAction(
            id="abjure-foes",
            name="Abjure Foes",
            action_cost="action",
            save_ability="wisdom",
            dc=save_dc,
            range_ft=60,
            max_targets=max(1, charisma_modifier),
            resource_id="channel-divinity",
            resource_cost=1,
            requires_target_sight=True,
            magical_effect=True,
            effect_tags=["frightened"],
            failed_save_timed_effect=FailedSaveTimedEffect(
                effect_id="frightened",
                duration_rounds=10,
                expiry_timing="source_turn_start",
                turn_behavior="single_activity",
                ends_on_damage=True,
            ),
            animation="frighten",
        )
    except Exception:
        logger.exception("Failed to build 2024 Abjure Foes.")
        raise


def beacon_of_hope_2024() -> DefensiveSpellAction:
    """Explicit 2024 Beacon of Hope fingerprint."""
    try:
        return DefensiveSpellAction(
            id="beacon-of-hope",
            name="Beacon of Hope",
            level=3,
            action_cost="action",
            range_ft=30,
            duration_minutes=1,
            target_policy="friendly",
            target_count=20,
            concentration=True,
            priority=60,
            modifier_effects=[
                SpellModifierEffect(kind="saving-throw-advantage", save_ability="wisdom"),
                SpellModifierEffect(kind="death-save-advantage"),
                SpellModifierEffect(kind="healing-maximize"),
            ],
            animation="beacon-of-hope",
            source=f"{_SOURCE}: Beacon of Hope",
        )
    except Exception:
        logger.exception("Failed to build 2024 Beacon of Hope.")
        raise


def dispel_magic_2024_paladin() -> EffectRemovalAction:
    """Explicit 2024 Dispel Magic using the Paladin's Charisma spellcasting ability."""
    try:
        return EffectRemovalAction(
            id="dispel-magic",
            name="Dispel Magic",
            level=3,
            action_cost="action",
            range_ft=120,
            casting_ability="charisma",
            target_mode="enemy",
            auto_remove_max_level=3,
            resource_id="spell-slot-3",
            resource_cost=1,
            expends_spell_slot=True,
            animation="dispel-magic",
        )
    except Exception:
        logger.exception("Failed to build 2024 Paladin Dispel Magic.")
        raise
