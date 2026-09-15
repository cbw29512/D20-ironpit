from __future__ import annotations

from app.domain.encounters import EncounterSetup


def source_has_active_grapple(setup: EncounterSetup, source_id: str) -> bool:
    """Return whether source currently holds any living combatant in a grapple."""
    for target in [*setup.heroes, *setup.monsters]:
        if target.combatant_id == source_id or target.state.is_dead:
            continue
        if any(grapple.source_id == source_id for grapple in target.state.grapple_sources):
            return True
    return False
