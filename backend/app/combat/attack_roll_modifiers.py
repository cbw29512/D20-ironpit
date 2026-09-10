from __future__ import annotations

from app.domain.modifiers import ModifierKind
from app.domain.runtime import CombatantState


def next_attack_advantage_sources(state: CombatantState) -> int:
    """Count source-neutral modifiers that grant Advantage on this creature's next attack."""
    return sum(1 for item in state.active_modifiers if item.kind is ModifierKind.NEXT_ATTACK_ADVANTAGE)


def next_attack_disadvantage_sources(state: CombatantState) -> int:
    """Count source-neutral modifiers that impose Disadvantage on this creature's next attack."""
    return sum(1 for item in state.active_modifiers if item.kind is ModifierKind.NEXT_ATTACK_DISADVANTAGE)


def _consume(state: CombatantState, kind: ModifierKind) -> int:
    before = len(state.active_modifiers)
    state.active_modifiers = [item for item in state.active_modifiers if item.kind is not kind]
    return before - len(state.active_modifiers)


def consume_next_attack_advantage(state: CombatantState) -> int:
    return _consume(state, ModifierKind.NEXT_ATTACK_ADVANTAGE)


def consume_next_attack_disadvantage(state: CombatantState) -> int:
    return _consume(state, ModifierKind.NEXT_ATTACK_DISADVANTAGE)
