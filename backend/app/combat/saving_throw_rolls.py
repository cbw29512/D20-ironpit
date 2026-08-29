from __future__ import annotations

from app.combat.barbarian import rage_active
from app.combat.dice import DiceProvider
from app.combat.grapple import RESTRAINED_EFFECT_ID
from app.combat.rolls import roll_d20
from app.domain.models import CombatantState, DiceRoll, RollMode


def saving_throw_mode(state: CombatantState, ability: str) -> RollMode:
    advantage = 1 if ability == "strength" and rage_active(state) else 0
    disadvantage = 1 if ability == "dexterity" and RESTRAINED_EFFECT_ID in state.active_effect_ids else 0
    if (advantage > 0) == (disadvantage > 0):
        return RollMode.NORMAL
    return RollMode.ADVANTAGE if advantage else RollMode.DISADVANTAGE


def resolve_saving_throw(
    state: CombatantState,
    ability: str,
    dc: int,
    dice: DiceProvider,
) -> tuple[DiceRoll | None, bool]:
    if state.is_unconscious and ability in {"strength", "dexterity"}:
        return None, False
    if ability not in state.template.saving_throw_bonuses:
        raise ValueError(f"{state.template.name} lacks a certified {ability.title()} saving throw bonus.")
    roll = roll_d20(
        dice,
        state.template.saving_throw_bonuses[ability],
        saving_throw_mode(state, ability),
    )
    return roll, roll.total >= dc
