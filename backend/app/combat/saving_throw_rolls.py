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
from app.domain.traits import CombatTrait


def saving_throw_mode(state: CombatantState, ability: str, *, against_magic: bool = False) -> RollMode:
    advantage = int(ability == "strength" and rage_active(state)) + danger_sense_advantage(state, ability)
    advantage += int(against_magic and CombatTrait.MAGIC_RESISTANCE in state.template.combat_traits)
    disadvantage = 1 if ability == "dexterity" and RESTRAINED_EFFECT_ID in state.active_effect_ids else 0
    if (advantage > 0) == (disadvantage > 0):
        return RollMode.NORMAL
    return RollMode.ADVANTAGE if advantage else RollMode.DISADVANTAGE


def resolve_saving_throw(
    state: CombatantState,
    ability: str,
    dc: int,
    dice: DiceProvider,
    *,
    against_magic: bool = False,
) -> tuple[DiceRoll | None, bool]:
    if ability in {"strength", "dexterity"} and automatically_fails_strength_dexterity_save(state):
        return None, False
    if ability not in state.template.saving_throw_bonuses:
        raise ValueError(f"{state.template.name} lacks a certified {ability.title()} saving throw bonus.")
    roll = apply_d20_bonus_dice(
        state,
        ModifierKind.SAVING_THROW_BONUS_DIE,
        roll_d20(dice, state.template.saving_throw_bonuses[ability], saving_throw_mode(state, ability, against_magic=against_magic)),
        dice,
    )
    if roll.total < dc:
        from app.combat.indomitable import use_indomitable

        reroll = use_indomitable(state, ability, dice)
        if reroll is not None:
            roll = reroll
    return roll, roll.total >= dc
