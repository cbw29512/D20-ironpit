from __future__ import annotations

from app.combat.barbarian import rage_active
from app.combat.condition_rules import automatically_fails_strength_dexterity_save
from app.combat.danger_sense import danger_sense_advantage
from app.combat.dice import DiceProvider
from app.combat.grapple import RESTRAINED_EFFECT_ID
from app.combat.modifier_stack import apply_d20_bonus_dice
from app.combat.rolls import roll_d20
from app.domain.models import CombatantState, DiceRoll, RollMode
from app.domain.modifiers import ModifierKind


def saving_throw_mode(state: CombatantState, ability: str) -> RollMode:
    advantage = int(ability == "strength" and rage_active(state)) + danger_sense_advantage(state, ability)
    disadvantage = 1 if ability == "dexterity" and RESTRAINED_EFFECT_ID in state.active_effect_ids else 0
    if (advantage > 0) == (disadvantage > 0):
        return RollMode.NORMAL
    return RollMode.ADVANTAGE if advantage else RollMode.DISADVANTAGE


def _indomitable_resource(state: CombatantState):
    return next((resource for resource in state.resources if resource.id == "indomitable"), None)


def _save_bonus_dice_max(state: CombatantState) -> int:
    return sum(
        item.dice_count * item.dice_size
        for item in state.active_modifiers
        if item.kind is ModifierKind.SAVING_THROW_BONUS_DIE
    )


def _roll_save(state: CombatantState, ability: str, modifier: int, dice: DiceProvider) -> DiceRoll:
    return apply_d20_bonus_dice(
        state,
        ModifierKind.SAVING_THROW_BONUS_DIE,
        roll_d20(dice, modifier, saving_throw_mode(state, ability)),
        dice,
    )


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
    base_bonus = state.template.saving_throw_bonuses[ability]
    roll = _roll_save(state, ability, base_bonus, dice)
    if roll.total >= dc:
        return roll, True

    indomitable_bonus = state.template.progression_features.indomitable_bonus
    resource = _indomitable_resource(state)
    maximum = 20 + base_bonus + indomitable_bonus + _save_bonus_dice_max(state)
    if indomitable_bonus <= 0 or resource is None or resource.current_uses <= 0 or maximum < dc:
        return roll, False

    resource.current_uses -= 1
    reroll = _roll_save(state, ability, base_bonus + indomitable_bonus, dice)
    reroll = reroll.model_copy(update={"notation": f"{reroll.notation} [Indomitable +{indomitable_bonus}]"})
    return reroll, reroll.total >= dc
