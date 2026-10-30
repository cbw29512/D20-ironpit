from __future__ import annotations

from collections.abc import Iterable

from app.combat.modifier_stack import add_modifier
from app.domain.hit_modifiers import CombatModifierEffect
from app.domain.modifiers import CombatModifier, ModifierKind
from app.domain.runtime import CombatantState
from app.domain.weapons import WeaponAttack

_SUPPORTED_EFFECT_MODIFIERS = {
    ModifierKind.ATTACKS_AGAINST_ADVANTAGE,
    ModifierKind.NEXT_ATTACK_ADVANTAGE,
    ModifierKind.NEXT_ATTACK_DISADVANTAGE,
    ModifierKind.SPEED,
}


def apply_modifier_effect(
    state: CombatantState,
    source_id: str,
    source_effect_id: str,
    effect: CombatModifierEffect,
    index: int,
    *,
    trigger: str,
    round_number: int | None = None,
) -> None:
    """Apply one source-neutral modifier effect with trigger-specific identity."""
    try:
        kind = ModifierKind(effect.kind)
        if kind not in _SUPPORTED_EFFECT_MODIFIERS:
            raise ValueError(f"Unsupported combat modifier effect kind: {effect.kind}.")
        if effect.expires_at_end_of_source_turn and round_number is None:
            raise ValueError("End-of-source-turn modifier requires the current round.")
        add_modifier(state, CombatModifier(
            id=f"{source_id}:{source_effect_id}:{trigger}-modifier:{index}",
            source_id=source_id,
            source_effect_id=source_effect_id,
            kind=kind,
            flat_bonus=effect.flat_bonus,
            consume_on_attack_against=effect.consume_on_attack_against,
            expires_at_start_of_source_turn=effect.expires_at_start_of_source_turn,
            expires_at_end_of_target_turn=effect.expires_at_end_of_target_turn,
            expires_source_turn_end_round=round_number if effect.expires_at_end_of_source_turn else None,
        ))
    except Exception:
        import logging
        logging.getLogger(__name__).exception("Failed to apply combat modifier %s.", source_effect_id)
        raise


def apply_hit_modifier_effects(
    state: CombatantState,
    source_id: str,
    attack: WeaponAttack,
    round_number: int | None = None,
) -> None:
    """Apply target-owned modifier riders after a successful weapon hit."""
    try:
        for index, effect in enumerate(attack.on_hit_modifier_effects):
            apply_modifier_effect(
                state, source_id, attack.id, effect, index,
                trigger="hit", round_number=round_number,
            )
    except Exception:
        import logging
        logging.getLogger(__name__).exception("Failed target hit modifiers for %s.", attack.id)
        raise


def apply_self_hit_modifier_effects(
    state: CombatantState,
    source_id: str,
    attack: WeaponAttack,
    round_number: int,
) -> None:
    """Apply source-owned modifier riders created by this creature's successful hit."""
    try:
        for index, effect in enumerate(attack.on_hit_self_modifier_effects):
            apply_modifier_effect(
                state, source_id, attack.id, effect, index,
                trigger="self-hit", round_number=round_number,
            )
    except Exception:
        import logging
        logging.getLogger(__name__).exception("Failed source hit modifiers for %s.", attack.id)
        raise


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
