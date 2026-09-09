from __future__ import annotations

from collections.abc import Iterable

from app.combat.modifier_stack import add_modifier
from app.domain.hit_modifiers import HitModifierEffect
from app.domain.modifiers import CombatModifier, ModifierKind
from app.domain.runtime import CombatantState
from app.domain.weapons import WeaponAttack

_SUPPORTED_MODIFIERS = {
    ModifierKind.ATTACKS_AGAINST_ADVANTAGE,
    ModifierKind.SPEED,
}


def apply_modifier_effects(
    state: CombatantState,
    source_id: str,
    source_effect_id: str,
    effects: Iterable[HitModifierEffect],
) -> None:
    """Apply source-neutral modifier effects declared by any combat action."""
    for index, effect in enumerate(effects):
        kind = ModifierKind(effect.kind)
        if kind not in _SUPPORTED_MODIFIERS:
            raise ValueError(f"Unsupported modifier kind: {effect.kind}.")
        add_modifier(state, CombatModifier(
            id=f"{source_id}:{source_effect_id}:modifier:{index}",
            source_id=source_id,
            source_effect_id=source_effect_id,
            kind=kind,
            flat_bonus=effect.flat_bonus,
            consume_on_attack_against=effect.consume_on_attack_against,
            expires_at_start_of_source_turn=effect.expires_at_start_of_source_turn,
            expires_at_end_of_target_turn=effect.expires_at_end_of_target_turn,
        ))


def apply_hit_modifier_effects(state: CombatantState, source_id: str, attack: WeaponAttack) -> None:
    """Backward-compatible attack wrapper around the universal modifier path."""
    apply_modifier_effects(state, source_id, attack.id, attack.on_hit_modifier_effects)


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
