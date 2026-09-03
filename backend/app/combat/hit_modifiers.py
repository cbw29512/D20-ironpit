from __future__ import annotations

from collections.abc import Iterable

from app.combat.modifier_stack import add_modifier
from app.domain.modifiers import CombatModifier, ModifierKind
from app.domain.runtime import CombatantState
from app.domain.weapons import WeaponAttack


def apply_hit_modifier_effects(state: CombatantState, source_id: str, attack: WeaponAttack) -> None:
    """Apply generic modifier riders to a living target after a successful hit."""
    for index, effect in enumerate(attack.on_hit_modifier_effects):
        if effect.kind != ModifierKind.ATTACKS_AGAINST_ADVANTAGE.value:
            raise ValueError(f"Unsupported on-hit modifier kind: {effect.kind}.")
        add_modifier(state, CombatModifier(
            id=f"{source_id}:{attack.id}:hit-modifier:{index}",
            source_id=source_id,
            source_effect_id=attack.id,
            kind=ModifierKind.ATTACKS_AGAINST_ADVANTAGE,
            consume_on_attack_against=effect.consume_on_attack_against,
            expires_at_start_of_source_turn=effect.expires_at_start_of_source_turn,
        ))


def expire_source_turn_start_modifiers(states: Iterable[CombatantState], source_id: str) -> int:
    """Expire modifiers whose RAW duration ends at the start of their source's turn."""
    removed = 0
    for state in states:
        before = len(state.active_modifiers)
        state.active_modifiers = [item for item in state.active_modifiers if not (
            item.source_id == source_id and item.expires_at_start_of_source_turn
        )]
        removed += before - len(state.active_modifiers)
    return removed
