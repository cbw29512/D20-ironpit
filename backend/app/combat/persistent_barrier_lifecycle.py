from __future__ import annotations

import logging

from app.domain.encounters import EncounterSetup

logger = logging.getLogger(__name__)


def cleanup_persistent_barriers(setup: EncounterSetup, round_number: int) -> list[str]:
    """Remove expired/dropped barriers and mature full-duration permanent barriers."""
    try:
        members = {member.combatant_id: member for member in [*setup.heroes, *setup.monsters]}
        kept = []
        removed: list[str] = []

        for barrier in setup.persistent_barriers:
            if all(section.destroyed or section.current_hp <= 0 for section in barrier.sections):
                removed.append(barrier.barrier_id)
                continue

            if round_number >= barrier.expires_round:
                if barrier.permanent_after_full_duration:
                    barrier.concentration = False
                    barrier.permanent_after_full_duration = False
                    kept.append(barrier)
                else:
                    removed.append(barrier.barrier_id)
                continue

            if barrier.concentration:
                source = members.get(barrier.source_id)
                current = source.state.concentration if source is not None else None
                if (
                    current is None
                    or current.source_id != barrier.source_id
                    or current.effect_id != barrier.action_id
                ):
                    removed.append(barrier.barrier_id)
                    continue

            kept.append(barrier)

        setup.persistent_barriers = kept
        return removed
    except Exception as exc:
        logger.exception("Failed to clean persistent barriers.")
        raise RuntimeError("Persistent barrier lifecycle could not be cleaned.") from exc
