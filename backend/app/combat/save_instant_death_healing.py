"""Universal save-failure execution with source-conditional healing.

The card supplies required target state and healing dice. Standard instant
death prevention, typed save resolution, and HP recovery own the behavior.
"""
from __future__ import annotations

import logging

from app.combat.instant_death import apply_instant_death
from app.combat.zero_hp import restore_hit_points
from app.domain.encounters import EncounterCombatant
from app.domain.models import DiceRoll, SavingThrowAction
from app.domain.runtime import CombatantState

logger = logging.getLogger(__name__)


def resolve_save_finisher(
    actor: EncounterCombatant,
    target: EncounterCombatant,
    action: SavingThrowAction,
    succeeded: bool,
    dice,
    affected_states: list[CombatantState] | None = None,
) -> tuple[DiceRoll | None, int, bool]:
    """Return (healing roll, actual HP restored, newly dead) after a save."""
    try:
        if not action.instant_death_on_failed_save or succeeded:
            return None, 0, False
        if (not action.requires_target_zero_hp_alive
                or target.state.current_hp != 0
                or not target.state.is_alive or target.state.is_dead):
            raise ValueError(f"{action.name} requires a living target at zero HP.")
        was_dead = target.state.is_dead
        apply_instant_death(target.state, affected_states=affected_states)
        newly_dead = target.state.is_dead and not was_dead
        if not newly_dead:
            return None, 0, False
        rolls = [
            dice.roll(action.heal_source_on_kill_dice_size)
            for _ in range(action.heal_source_on_kill_dice_count)
        ]
        total = sum(rolls)
        healed = restore_hit_points(actor.state, total)
        return DiceRoll(
            notation=f"{len(rolls)}d{action.heal_source_on_kill_dice_size}",
            rolls=rolls, modifier=0, total=total,
        ), healed, True
    except Exception:
        logger.exception("Save finisher failed: %s", action.id)
        raise
