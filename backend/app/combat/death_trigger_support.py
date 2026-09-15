from __future__ import annotations

import logging

from app.combat.grid_geometry import footprint_distance_ft
from app.domain.actions import SavingThrowAction
from app.domain.death_triggers import DeathTriggeredSaveEffect
from app.domain.encounters import EncounterCombatant

logger = logging.getLogger(__name__)


def compile_action(effect: DeathTriggeredSaveEffect) -> SavingThrowAction:
    """Compile immutable death-trigger data into the shared save-action shape."""
    try:
        return SavingThrowAction(
            id=effect.id,
            name=effect.name,
            save_ability=effect.save_ability,
            dc=effect.dc,
            range_ft=effect.radius_ft,
            damage_dice_count=effect.damage_dice_count,
            damage_dice_size=effect.damage_dice_size,
            damage_bonus=effect.damage_bonus,
            damage_type=effect.damage_type.value,
            success_damage="half" if effect.half_damage_on_success else "none",
            animation="death-trigger",
        )
    except Exception:
        logger.exception("Failed to compile death-trigger effect %s.", effect.id)
        raise


def distance_ft(source: EncounterCombatant, target: EncounterCombatant) -> int:
    """Return authoritative footprint distance for a death-trigger target check."""
    try:
        if source.state.position is None or target.state.position is None:
            raise ValueError("Death-trigger resolution requires authoritative grid positions.")
        return footprint_distance_ft(
            source.state.position,
            source.state.template.size,
            target.state.position,
            target.state.template.size,
        )
    except Exception:
        logger.exception(
            "Failed death-trigger distance check: %s -> %s.",
            source.combatant_id,
            target.combatant_id,
        )
        raise
