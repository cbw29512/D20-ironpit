from __future__ import annotations

from app.domain.encounters import EncounterSetup


def source_grapple_count(setup: EncounterSetup, source_id: str) -> int:
    """Count currently held distinct targets, independent of creature identity."""
    if setup is None:
        raise ValueError("A limited grapple requires its active encounter setup.")
    return sum(
        target.combatant_id != source_id and not target.state.is_dead
        and target.state.is_alive
        and any(grapple.source_id == source_id for grapple in target.state.grapple_sources)
        for target in [*setup.heroes, *setup.monsters]
    )


def source_has_active_grapple(setup: EncounterSetup, source_id: str) -> bool:
    return source_grapple_count(setup, source_id) > 0
