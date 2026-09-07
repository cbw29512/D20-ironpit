from __future__ import annotations

from collections.abc import Iterable

from app.combat.dice import DiceProvider
from app.domain.events import DiceRoll
from app.domain.modifiers import CombatModifier, ModifierKind
from app.domain.runtime import CombatantState


def add_modifier(state: CombatantState, modifier: CombatModifier) -> None:
    existing = next((item for item in state.active_modifiers if item.id == modifier.id), None)
    if existing is not None:
        if existing == modifier:
            return
        raise ValueError(f"Modifier id {modifier.id} already exists with different data.")
    state.active_modifiers.append(modifier)


def remove_source_modifiers(
    states: Iterable[CombatantState], source_id: str, source_effect_id: str, *, concentration_only: bool = False,
) -> int:
    removed = 0
    for state in states:
        before = len(state.active_modifiers)
        state.active_modifiers = [
            item for item in state.active_modifiers
            if not (
                item.source_id == source_id
                and item.source_effect_id == source_effect_id
                and (not concentration_only or item.concentration_required)
            )
        ]
        removed += before - len(state.active_modifiers)
    return removed


def expire_source_turn_modifiers(
    states: Iterable[CombatantState], source_id: str, round_number: int,
) -> int:
    removed = 0
    for state in states:
        before = len(state.active_modifiers)
        state.active_modifiers = [
            item for item in state.active_modifiers
            if not (
                item.source_id == source_id
                and item.expires_source_turn_end_round is not None
                and item.expires_source_turn_end_round <= round_number
            )
        ]
        removed += before - len(state.active_modifiers)
    return removed


def expire_target_turn_modifiers(state: CombatantState) -> int:
    """Expire modifiers whose duration ends at the end of the affected creature's turn."""
    before = len(state.active_modifiers)
    state.active_modifiers = [item for item in state.active_modifiers if not item.expires_at_end_of_target_turn]
    return before - len(state.active_modifiers)


def effective_armor_class(state: CombatantState) -> int:
    return max(0, state.template.armor_class + sum(
        item.flat_bonus for item in state.active_modifiers if item.kind is ModifierKind.ARMOR_CLASS
    ))


def effective_speed(state: CombatantState) -> int:
    return max(0, state.template.speed_ft + sum(
        item.flat_bonus for item in state.active_modifiers if item.kind is ModifierKind.SPEED
    ))


def attacks_against_advantage_sources(state: CombatantState) -> int:
    return sum(1 for item in state.active_modifiers if item.kind is ModifierKind.ATTACKS_AGAINST_ADVANTAGE)


def consume_attacks_against_advantage(state: CombatantState) -> int:
    before = len(state.active_modifiers)
    state.active_modifiers = [
        item for item in state.active_modifiers
        if not (item.kind is ModifierKind.ATTACKS_AGAINST_ADVANTAGE and item.consume_on_attack_against)
    ]
    return before - len(state.active_modifiers)


def next_attack_against_advantage_sources(state: CombatantState, target_id: str) -> int:
    return sum(
        1 for item in state.active_modifiers
        if item.kind is ModifierKind.NEXT_ATTACK_AGAINST_ADVANTAGE and item.target_id == target_id
    )


def consume_next_attack_against_advantage(state: CombatantState, target_id: str) -> int:
    before = len(state.active_modifiers)
    state.active_modifiers = [
        item for item in state.active_modifiers
        if not (item.kind is ModifierKind.NEXT_ATTACK_AGAINST_ADVANTAGE and item.target_id == target_id)
    ]
    return before - len(state.active_modifiers)


def next_attack_disadvantage_sources(state: CombatantState) -> int:
    return sum(1 for item in state.active_modifiers if item.kind is ModifierKind.NEXT_ATTACK_DISADVANTAGE)


def consume_next_attack_disadvantage(state: CombatantState) -> int:
    before = len(state.active_modifiers)
    state.active_modifiers = [item for item in state.active_modifiers if item.kind is not ModifierKind.NEXT_ATTACK_DISADVANTAGE]
    return before - len(state.active_modifiers)


def _die_modifiers(state: CombatantState, kind: ModifierKind) -> list[CombatModifier]:
    if kind not in {ModifierKind.ATTACK_ROLL_BONUS_DIE, ModifierKind.SAVING_THROW_BONUS_DIE}:
        raise ValueError(f"{kind.value} is not a D20 bonus-die modifier.")
    return [item for item in state.active_modifiers if item.kind is kind]


def apply_d20_bonus_dice(
    state: CombatantState, kind: ModifierKind, roll: DiceRoll, dice: DiceProvider,
) -> DiceRoll:
    modifiers = _die_modifiers(state, kind)
    if not modifiers:
        return roll
    bonus_rolls = [dice.roll(item.dice_size) for item in modifiers for _ in range(item.dice_count)]
    notation = " + ".join([roll.notation, *(f"{item.dice_count}d{item.dice_size}" for item in modifiers)])
    return roll.model_copy(update={
        "notation": notation,
        "rolls": [*roll.rolls, *bonus_rolls],
        "total": roll.total + sum(bonus_rolls),
    })


def bonus_damage_modifiers(state: CombatantState, target_id: str | None) -> list[CombatModifier]:
    return [
        item for item in state.active_modifiers
        if item.kind is ModifierKind.BONUS_DAMAGE and (item.target_id is None or item.target_id == target_id)
    ]
