from __future__ import annotations

from app.combat.modifier_stack import add_modifier
from app.domain.models import CombatantState
from app.domain.modifiers import CombatModifier, ModifierKind

STUDIED_ATTACKS_EFFECT_ID = "studied-attacks"


def studied_attacks_active(attacker: CombatantState) -> bool:
    return attacker.template.progression_features.studied_attacks


def apply_studied_attack_miss(
    attacker: CombatantState,
    attacker_id: str,
    target_id: str,
    round_number: int,
) -> bool:
    """Prime RAW Studied Attacks after the attack's final result is a miss."""
    if not studied_attacks_active(attacker):
        return False
    add_modifier(attacker, CombatModifier(
        id=f"{attacker_id}:{STUDIED_ATTACKS_EFFECT_ID}:{target_id}",
        source_id=attacker_id,
        source_effect_id=STUDIED_ATTACKS_EFFECT_ID,
        kind=ModifierKind.NEXT_ATTACK_AGAINST_ADVANTAGE,
        target_id=target_id,
        expires_source_turn_end_round=round_number + 1,
    ))
    return True
