from __future__ import annotations

from app.combat.barbarian import rage_active
from app.combat.condition_rules import automatically_fails_strength_dexterity_save
from app.combat.dice import DiceProvider
from app.combat.grapple import RESTRAINED_EFFECT_ID
from app.combat.rolls import roll_d20
from app.combat.support_effects import bless_bonus
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
    if ability in {"strength", "dexterity"} and automatically_fails_strength_dexterity_save(state):
        return None, False
    if ability not in state.template.saving_throw_bonuses:
        raise ValueError(f"{state.template.name} lacks a certified {ability.title()} saving throw bonus.")
    roll = roll_d20(dice, state.template.saving_throw_bonuses[ability], saving_throw_mode(state, ability))
    blessing = bless_bonus(state, dice)
    if blessing:
        roll.notation += "+1d4"
        roll.rolls.append(blessing)
        roll.total += blessing
    return roll, roll.total >= dc
