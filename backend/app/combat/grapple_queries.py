from __future__ import annotations

from app.domain.encounters import EncounterSetup


def source_has_active_grapple(setup: EncounterSetup, source_id: str) -> bool:
    return any(
        target.combatant_id != source_id
        and not target.state.is_dead
        and any(grapple.source_id == source_id for grapple in target.state.grapple_sources)
        for target in [*setup.heroes, *setup.monsters]
    )
