from __future__ import annotations

import logging
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def applied_damage_total(event: BattleEvent) -> int:
    """Measure damage actually applied after defenses and Temporary HP."""
    try:
        components = list(event.damage_components)
        if components and all(part.applied_total is not None for part in components):
            return sum(int(part.applied_total or 0) for part in components)

        hp_known = event.hp_before is not None and event.hp_after is not None
        temporary_hp_known = (
            event.temporary_hp_before is not None and event.temporary_hp_after is not None
        )
        hp_loss = max(0, event.hp_before - event.hp_after) if hp_known else 0
        temporary_hp_loss = (
            max(0, event.temporary_hp_before - event.temporary_hp_after)
            if temporary_hp_known
            else 0
        )
        # Snapshot state is authoritative even when it proves that zero damage landed.
        # Falling through to the raw damage roll here would incorrectly trigger reactions
        # after immunity, absorption, or another defense reduced applied damage to zero.
        if hp_known or temporary_hp_known:
            return hp_loss + temporary_hp_loss
        return max(0, event.damage_roll.total) if event.damage_roll is not None else 0
    except Exception as exc:
        logger.exception("Failed to measure applied damage for event %s.", event.sequence)
        raise RuntimeError("Applied damage could not be measured.") from exc


def _member_by_id(setup: EncounterSetup, combatant_id: str | None) -> EncounterCombatant | None:
    try:
        if combatant_id is None:
            return None
        return next(
            (
                member
                for member in [*setup.heroes, *setup.monsters]
                if member.combatant_id == combatant_id
            ),
            None,
        )
    except Exception as exc:
        logger.exception("Failed to resolve encounter member %s for damage reaction.", combatant_id)
        raise RuntimeError("Damage reaction encounter member could not be resolved.") from exc


