from __future__ import annotations

from app.domain.encounters import EncounterCombatant, EncounterSetup


def wins_initiative_over_all_enemies(attacker: EncounterCombatant, setup: EncounterSetup) -> bool:
    """Require a strict initiative-total win over every enemy; tie-breakers do not qualify."""
    total = attacker.state.initiative_total
    if total is None:
        return False
    enemies = setup.monsters if attacker.side == "heroes" else setup.heroes
    if not enemies:
        return False
    return all(
        enemy.state.initiative_total is not None and total > enemy.state.initiative_total
        for enemy in enemies
    )


def opening_burst_available(
    round_number: int, attacker: EncounterCombatant, setup: EncounterSetup | None,
) -> bool:
    """Iron Pit opener policy: special run-up/leap/charge logic exists only on round 1 after an initiative sweep."""
    return round_number == 1 and setup is not None and wins_initiative_over_all_enemies(attacker, setup)
