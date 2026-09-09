from __future__ import annotations

from app.combat.encounter_targeting import combatant_distance
from app.combat.forced_movement import apply_forced_movement
from app.domain.actions import HitControlEffect
from app.domain.encounters import EncounterCombatant
from app.domain.models import BattleEvent


def apply_event_forced_movement(
    source: EncounterCombatant,
    target: EncounterCombatant,
    control: HitControlEffect | None,
    event: BattleEvent,
) -> BattleEvent:
    if (
        control is None
        or control.forced_movement is None
        or target.state.is_dead
        or not target.state.is_alive
    ):
        return event
    before_distance = combatant_distance(source, target)
    result = apply_forced_movement(
        source,
        target,
        control.forced_movement,
        max_target_size=control.max_target_size,
    )
    if result is None:
        return event
    after_distance = combatant_distance(source, target)
    event.distance_before_ft = before_distance
    event.distance_after_ft = after_distance
    event.movement_ft = result.moved_ft
    verb = "pushed" if control.forced_movement.direction == "push" else "pulled"
    if result.moved_ft:
        event.description += f" {target.state.template.name} is {verb} {result.moved_ft} feet."
    else:
        event.description += f" {target.state.template.name} cannot be {verb} farther in the Pit."
    return event
