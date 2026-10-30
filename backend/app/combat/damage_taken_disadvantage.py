from __future__ import annotations

import logging

from app.combat.modifier_stack import add_modifier
from app.domain.damage_types import DamageType
from app.domain.modifiers import CombatModifier, ModifierKind
from app.domain.runtime import CombatantState

logger = logging.getLogger(__name__)


def apply_damage_taken_disadvantage(
    state: CombatantState,
    damage_type: DamageType,
    applied_amount: int,
) -> None:
    """Refresh source-defined roll Disadvantage after actual matching damage."""
    try:
        if applied_amount <= 0:
            return
        rules = [
            rule for rule in state.template.damage_taken_disadvantage_rules
            if rule.damage_type is damage_type
        ]
        for rule in rules:
            expiry = state.turn_serial + 1
            definitions = []
            if rule.attack_roll_disadvantage:
                definitions.append((
                    f"{rule.id}:attack-roll-disadvantage",
                    ModifierKind.ATTACK_ROLL_DISADVANTAGE,
                ))
            if rule.ability_check_disadvantage:
                definitions.append((
                    f"{rule.id}:ability-check-disadvantage",
                    ModifierKind.ABILITY_CHECK_DISADVANTAGE,
                ))
            for modifier_id, kind in definitions:
                state.active_modifiers = [
                    item for item in state.active_modifiers
                    if item.id != modifier_id
                ]
                add_modifier(state, CombatModifier(
                    id=modifier_id,
                    source_id=state.template.id,
                    source_effect_id=rule.id,
                    kind=kind,
                    expires_target_turn_serial=expiry,
                ))
    except Exception as exc:
        logger.exception(
            "Failed damage-taken disadvantage application for %s.",
            state.template.id,
        )
        raise RuntimeError("Damage-taken disadvantage could not be applied.") from exc
