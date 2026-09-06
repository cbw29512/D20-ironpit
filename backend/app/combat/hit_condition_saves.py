from __future__ import annotations

from dataclasses import dataclass

from app.combat.dice import DiceProvider
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.timed_conditions import apply_timed_condition
from app.domain.actions import HitControlEffect
from app.domain.models import CombatantState, DiceRoll, WeaponAttack


@dataclass(frozen=True)
class HitConditionOutcome:
    applied: list[str]
    save_roll: DiceRoll | None = None
    save_ability: str | None = None
    save_dc: int | None = None
    save_succeeded: bool | None = None


def _normalized_type(state: CombatantState) -> str:
    return (state.template.creature_type or "").split("(", 1)[0].strip().lower()


def target_eligible(control: HitControlEffect, target: CombatantState) -> bool:
    if _normalized_type(target) in {item.lower() for item in control.excluded_creature_types}:
        return False
    species = (target.template.species_id or "").lower()
    return species not in {item.lower() for item in control.excluded_species_ids}


def resolve_save_gated_hit_condition(
    attack: WeaponAttack,
    defender: CombatantState,
    source_id: str,
    round_number: int | None,
    dice: DiceProvider,
    affected_states: list[CombatantState] | None = None,
) -> HitConditionOutcome:
    control = attack.control_effect
    if control is None or control.condition_id is None or control.initial_save_ability is None:
        return HitConditionOutcome([])
    if defender.is_dead or not defender.is_alive or not target_eligible(control, defender):
        return HitConditionOutcome([])
    roll, succeeded = resolve_saving_throw(defender, control.initial_save_ability, int(control.initial_save_dc), dice)
    if succeeded:
        return HitConditionOutcome([], roll, control.initial_save_ability, control.initial_save_dc, True)
    timed = apply_timed_condition(
        defender, control.condition_id, source_id,
        source_effect_id=attack.id, applied_round=round_number,
        expires_at_start_of_source_turn=control.expires_at_start_of_source_turn,
        expiry_timing=control.expiry_timing,
        repeat_save_ability=control.repeat_save_ability, repeat_save_dc=control.repeat_save_dc,
        repeat_save_timing=control.repeat_save_timing,
        allowed_removal_action_ids=control.allowed_removal_action_ids,
        affected_states=affected_states,
    )
    applied = [timed] if timed is not None else []
    return HitConditionOutcome(applied, roll, control.initial_save_ability, control.initial_save_dc, False)
