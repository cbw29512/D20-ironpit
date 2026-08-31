from __future__ import annotations

from app.domain.encounters import EncounterCombatant, EncounterSetup

_OPENING_TRAIT_FEATURES = (("Running Leap", "running-leap"),)


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
    """Allow one opener only in round 1 after a strict initiative sweep."""
    return round_number == 1 and setup is not None and wins_initiative_over_all_enemies(attacker, setup)


def opening_feature_id(
    round_number: int, attacker: EncounterCombatant, setup: EncounterSetup | None,
) -> str | None:
    """Label source-backed movement openers that modify no printed attack math."""
    if not opening_burst_available(round_number, attacker, setup):
        return None
    names = set(attacker.state.template.source_trait_names)
    return next((feature for source, feature in _OPENING_TRAIT_FEATURES if source in names), None)
