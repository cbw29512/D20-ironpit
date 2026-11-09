"""Universal capacity and size gate for a saving throw that may grapple.

This gate never suppresses the saving throw or its damage. Source card
parameters control the grapple only, so oversized/at-capacity targets
can still take the printed damage.
"""
from __future__ import annotations

import logging

from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import SavingThrowAction
from app.domain.size import CreatureSize, size_at_least, size_at_most

logger = logging.getLogger(__name__)


def _cost(size: CreatureSize, action: SavingThrowAction) -> int:
    return (
        action.grapple_large_target_slot_cost
        if size_at_least(size, CreatureSize.LARGE) else 1
    )


def can_apply_save_grapple(
    actor: EncounterCombatant,
    target: EncounterCombatant,
    action: SavingThrowAction,
    setup: EncounterSetup | None,
) -> bool:
    """Preserve existing links; apply only a source-legal free slot."""
    try:
        if (
            action.grapple_max_target_size is not None
            and not size_at_most(
                target.state.template.size, action.grapple_max_target_size,
            )
        ):
            return False
        if action.grapple_max_active_grapples is None:
            return True
        if setup is None:
            raise ValueError("Capacity-limited save Grapple needs encounter setup.")
        occupied = 0
        for member in [*setup.heroes, *setup.monsters]:
            if member.combatant_id == actor.combatant_id:
                continue
            if not member.state.is_alive or member.state.is_dead:
                continue
            if not any(
                src.source_id == actor.combatant_id
                for src in member.state.grapple_sources
            ):
                continue
            if member.combatant_id == target.combatant_id:
                # Never replace another linked effect's Grapple metadata.
                return False
            occupied += _cost(member.state.template.size, action)
        return occupied + _cost(
            target.state.template.size, action,
        ) <= action.grapple_max_active_grapples
    except Exception:
        logger.exception(
            "Save Grapple capacity failed: %s against %s.",
            actor.combatant_id, target.combatant_id,
        )
        raise
