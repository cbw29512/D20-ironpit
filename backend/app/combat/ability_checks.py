from __future__ import annotations

from app.combat.barbarian import rage_active
from app.combat.condition_rules import has_condition
from app.combat.d20_effects import strength_d20_disadvantage
from app.combat.dice import DiceProvider
from app.combat.rolls import roll_d20
from app.combat.timed_roll_effects import ability_check_disadvantage
from app.domain.actions import AbilityName
from app.domain.models import CombatantState, DiceRoll, RollMode


def ability_check_mode(state: CombatantState, ability: AbilityName) -> RollMode:
    advantage = int(ability == "strength" and rage_active(state))
    disadvantage = (
        int(has_condition(state, "poisoned") or has_condition(state, "frightened"))
        + int(bool(ability_check_disadvantage(state)))
        + int(ability == "strength") * int(bool(strength_d20_disadvantage(state)))
    )
    if (advantage > 0) == (disadvantage > 0):
        return RollMode.NORMAL
    return RollMode.ADVANTAGE if advantage else RollMode.DISADVANTAGE


def roll_ability_check(
    state: CombatantState,
    ability: AbilityName,
    dice: DiceProvider,
) -> DiceRoll:
    scores = state.template.ability_scores
    if scores is None:
        raise ValueError(f"{state.template.name} lacks certified ability scores.")
    return roll_d20(dice, scores.modifier(ability), ability_check_mode(state, ability))
