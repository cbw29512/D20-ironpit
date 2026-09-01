from __future__ import annotations

from app.combat.encounter_targeting import combatant_distance, select_nearest_target
from app.combat.grapple import speed_is_zero
from app.combat.policy import preferred_approach_distance
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent


def apply_critical_closing_move(
    attacker: EncounterCombatant,
    setup: EncounterSetup | None,
    event: BattleEvent,
) -> BattleEvent:
    """Use granted post-critical movement only to close, never to kite or retreat."""
    fraction = attacker.state.template.progression_features.critical_move_fraction
    if not event.critical or setup is None or fraction <= 0 or speed_is_zero(attacker.state):
        return event
    target = select_nearest_target(attacker, setup)
    if target is None:
        return event
    before = combatant_distance(attacker, target)
    desired = preferred_approach_distance(attacker.state)
    moved = min(max(0, before - desired), int(attacker.state.template.speed_ft * fraction))
    if moved <= 0:
        return event
    direction = 1 if attacker.position_ft < target.position_ft else -1
    attacker.position_ft += direction * moved
    event.distance_before_ft = before
    event.distance_after_ft = combatant_distance(attacker, target)
    event.movement_ft = moved
    event.description += (
        f" {attacker.state.template.name} uses Remarkable Athlete to close {moved} feet "
        "without provoking Opportunity Attacks."
    )
    return event
