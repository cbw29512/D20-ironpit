from __future__ import annotations

from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.forced_movement import ForcedMovement
from app.domain.models import BattleEvent
from app.domain.size import size_at_most


def _shift_setup(setup: EncounterSetup, amount: int) -> None:
    for member in [*setup.heroes, *setup.monsters]:
        member.position_ft += amount


def apply_forced_movement(
    source: EncounterCombatant,
    target: EncounterCombatant,
    effect: ForcedMovement | None,
    event: BattleEvent,
    setup: EncounterSetup | None,
) -> int:
    if effect is None or event.hit is not True:
        return 0
    if effect.max_target_size is not None and not size_at_most(target.state.template.size, effect.max_target_size):
        return 0
    before = abs(target.position_ft - source.position_ft)
    if effect.direction == "pull":
        moved = min(effect.distance_ft, before)
        if moved == 0:
            return 0
        direction = -1 if target.position_ft > source.position_ft else 1
        target.position_ft += direction * moved
    else:
        moved = effect.distance_ft
        direction = 1 if target.position_ft >= source.position_ft else -1
        proposed = target.position_ft + direction * moved
        if proposed < 0 and setup is not None:
            _shift_setup(setup, -proposed)
            proposed = 0
        elif proposed < 0:
            proposed = source.position_ft + before + moved
        target.position_ft = proposed
    after = abs(target.position_ft - source.position_ft)
    event.distance_before_ft = before
    event.distance_after_ft = after
    event.movement_ft = moved
    verb = "pushed" if effect.direction == "push" else "pulled"
    event.description += f" {target.state.template.name} is {verb} {moved} feet."
    return moved
