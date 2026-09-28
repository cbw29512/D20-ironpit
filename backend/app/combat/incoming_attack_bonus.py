from __future__ import annotations

from app.domain.modifiers import ModifierKind
from app.domain.runtime import CombatantState


def next_incoming_attack_roll_flat_bonus(defender: CombatantState, attacker_id: str) -> int:
    """Return one-shot flat bonuses to attacks against this defender by other creatures."""
    return max(
        (
            item.flat_bonus for item in defender.active_modifiers
            if item.kind is ModifierKind.NEXT_INCOMING_ATTACK_ROLL_FLAT
            and item.source_id != attacker_id
        ),
        default=0,
    )


def consume_next_incoming_attack_roll_flat_bonus(defender: CombatantState, attacker_id: str) -> int:
    """Consume only bonuses that this attacker is eligible to receive."""
    before = len(defender.active_modifiers)
    defender.active_modifiers = [
        item for item in defender.active_modifiers
        if not (
            item.kind is ModifierKind.NEXT_INCOMING_ATTACK_ROLL_FLAT
            and item.source_id != attacker_id
        )
    ]
    return before - len(defender.active_modifiers)
