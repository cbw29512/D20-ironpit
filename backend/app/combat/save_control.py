from __future__ import annotations

from dataclasses import dataclass, field

from app.combat.control_effects import apply_control_effect
from app.combat.encounter_forced_movement import apply_event_forced_movement
from app.domain.actions import HitControlEffect, SavingThrowAction
from app.domain.encounters import EncounterCombatant
from app.domain.models import BattleEvent
from app.domain.runtime import CombatantState


@dataclass(frozen=True)
class SaveControlResult:
    control: HitControlEffect | None
    applied_conditions: list[str] = field(default_factory=list)


def failure_control(action: SavingThrowAction) -> HitControlEffect | None:
    if action.failure_control is not None:
        return action.failure_control
    if action.grapple_escape_dc is None:
        return None
    return HitControlEffect(
        max_target_size=action.target_max_size,
        grapple_escape_dc=action.grapple_escape_dc,
        restrains_while_grappled=action.restrains_while_grappled,
    )


def resolve_failed_save_control(
    actor: EncounterCombatant,
    target: EncounterCombatant,
    action: SavingThrowAction,
    round_number: int,
    affected_states: list[CombatantState] | None,
) -> SaveControlResult:
    control = failure_control(action)
    applied = apply_control_effect(
        target.state,
        actor.combatant_id,
        action.id,
        control,
        range_ft=action.range_ft,
        round_number=round_number,
        affected_states=affected_states,
    )
    return SaveControlResult(control=control, applied_conditions=applied)


def apply_save_forced_movement(
    actor: EncounterCombatant,
    target: EncounterCombatant,
    result: SaveControlResult,
    event: BattleEvent,
) -> BattleEvent:
    return apply_event_forced_movement(actor, target, result.control, event)
