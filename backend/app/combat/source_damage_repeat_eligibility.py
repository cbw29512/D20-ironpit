"""Universal event-only repeat-save eligibility for source-owned harm effects.

No ability-specific logic: data selects a damage trigger, and encounter membership
determines who caused harm. This is shared by all owners and conditions.
"""
from __future__ import annotations

import logging

from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.timed_effects import TimedEffect

logger = logging.getLogger(__name__)


def damage_triggers_repeat_save(
    effect: TimedEffect,
    damage_source: EncounterCombatant,
    setup: EncounterSetup,
) -> bool:
    try:
        trigger = effect.damage_repeat_save_trigger
        if trigger == "none":
            return False
        if trigger == "any_damage_source":
            return True
        if trigger == "other_than_effect_source":
            return damage_source.combatant_id != effect.source_id
        if trigger == "source_or_allies":
            owner = next((
                member for member in [*setup.heroes, *setup.monsters]
                if member.combatant_id == effect.source_id
            ), None)
            # No source member means no demonstrated source-side harmful action.
            return owner is not None and damage_source.side == owner.side
        raise ValueError(f"Unrecognized event-only repeat-save trigger: {trigger!r}")
    except Exception:
        logger.exception("Failed to qualify source-owned damage repeat save.")
        raise
