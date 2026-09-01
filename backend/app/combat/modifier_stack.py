from __future__ import annotations

from collections.abc import Iterable

from app.combat.dice import DiceProvider
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
    states: Iterable[CombatantState],
    source_id: str,
    source_effect_id: str,
    *,
    concentration_only: bool = False,
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


def effective_armor_class(state: CombatantState) -> int:
    bonus = sum(
        item.flat_bonus for item in state.active_modifiers
        if item.kind is ModifierKind.ARMOR_CLASS
    )
    return max(0, state.template.armor_class + bonus)


def effective_speed(state: CombatantState) -> int:
    bonus = sum(
        item.flat_bonus for item in state.active_modifiers
        if item.kind is ModifierKind.SPEED
    )
    return max(0, state.template.speed_ft + bonus)


def attacks_against_advantage_sources(state: CombatantState) -> int:
    return sum(
        1 for item in state.active_modifiers
        if item.kind is ModifierKind.ATTACKS_AGAINST_ADVANTAGE
    )


def roll_bonus_dice(state: CombatantState, kind: ModifierKind, dice: DiceProvider) -> tuple[int, list[int]]:
    if kind not in {ModifierKind.ATTACK_ROLL_BONUS_DIE, ModifierKind.SAVING_THROW_BONUS_DIE}:
        raise ValueError(f"{kind.value} is not a D20 bonus-die modifier.")
    rolls: list[int] = []
    for item in state.active_modifiers:
        if item.kind is not kind:
            continue
        rolls.extend(dice.roll(item.dice_size) for _ in range(item.dice_count))
    return sum(rolls), rolls


def bonus_damage_modifiers(state: CombatantState, target_id: str | None) -> list[CombatModifier]:
    return [
        item for item in state.active_modifiers
        if item.kind is ModifierKind.BONUS_DAMAGE
        and (item.target_id is None or item.target_id == target_id)
    ]
