from __future__ import annotations

from app.domain.encounters import EncounterSetup
from app.domain.traits import CombatTrait


def refresh_reactive_reactions(setup: EncounterSetup) -> int:
    """Refresh creatures that can take one reaction on every combat turn."""
    refreshed = 0
    for member in [*setup.heroes, *setup.monsters]:
        if (
            member.state.is_alive
            and not member.state.is_dead
            and CombatTrait.REACTIVE in member.state.template.combat_traits
        ):
            member.state.reaction_available = True
            refreshed += 1
    return refreshed
