from __future__ import annotations

import logging

from app.domain.damage_triggered_d20 import ActiveDamageTriggeredD20Debuff
from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def _damage_type_key(value) -> str:
    return value.value if hasattr(value, "value") else str(value)


def _applied_damage_of_type(
    amount: int,
    damage_types: set,
    damage_components,
    trigger_damage_type,
) -> int:
    wanted = _damage_type_key(trigger_damage_type)
    components = list(damage_components or [])
    if components:
        return sum(
            max(0, int(component.applied_total or 0))
            for component in components
            if _damage_type_key(component.damage_type) == wanted
        )
    present = {_damage_type_key(item) for item in damage_types}
    if wanted not in present:
        return 0
    if len(present) != 1:
        raise ValueError("Multi-type damage triggers require applied damage components.")
    return max(0, int(amount))


def apply_damage_triggered_d20_debuffs(
    state: CombatantState,
    amount: int,
    damage_types: set,
    damage_components=None,
) -> list[str]:
    """Activate source-declared D20 debuffs after qualifying applied typed damage."""
    try:
        applied: list[str] = []
        for rule in state.template.damage_triggered_d20_debuffs:
            typed_damage = _applied_damage_of_type(
                amount, damage_types, damage_components, rule.trigger_damage_type,
            )
            if typed_damage < rule.trigger_damage_minimum:
                continue
            expires_after = state.turns_started_count + rule.duration_target_turns
            active = ActiveDamageTriggeredD20Debuff(
                source_id=rule.source_id,
                source_name=rule.source_name,
                attack_roll_disadvantage=rule.attack_roll_disadvantage,
                ability_check_disadvantage=rule.ability_check_disadvantage,
                expires_after_target_turn_count=expires_after,
            )
            state.active_damage_triggered_d20_debuffs = [
                item for item in state.active_damage_triggered_d20_debuffs
                if item.source_id != rule.source_id
            ]
            state.active_damage_triggered_d20_debuffs.append(active)
            applied.append(rule.source_name)
        return applied
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed damage-triggered D20 debuff activation for %s.", state.template.name)
        raise RuntimeError("Damage-triggered D20 debuff could not be activated.") from exc


def attack_roll_disadvantage_sources(state: CombatantState) -> int:
    try:
        return sum(
            1 for item in state.active_damage_triggered_d20_debuffs
            if item.attack_roll_disadvantage
        )
    except Exception as exc:
        logger.exception("Failed damage-triggered attack Disadvantage lookup for %s.", state.template.name)
        raise RuntimeError("Damage-triggered attack Disadvantage could not be evaluated.") from exc


def ability_check_disadvantage_sources(state: CombatantState) -> int:
    try:
        return sum(
            1 for item in state.active_damage_triggered_d20_debuffs
            if item.ability_check_disadvantage
        )
    except Exception as exc:
        logger.exception("Failed damage-triggered ability-check Disadvantage lookup for %s.", state.template.name)
        raise RuntimeError("Damage-triggered ability-check Disadvantage could not be evaluated.") from exc


def expire_damage_triggered_d20_debuffs(state: CombatantState) -> list[str]:
    """Expire effects after the affected creature completes the declared next turn count."""
    try:
        expired = [
            item.source_name
            for item in state.active_damage_triggered_d20_debuffs
            if state.turns_started_count >= item.expires_after_target_turn_count
        ]
        state.active_damage_triggered_d20_debuffs = [
            item for item in state.active_damage_triggered_d20_debuffs
            if state.turns_started_count < item.expires_after_target_turn_count
        ]
        return expired
    except Exception as exc:
        logger.exception("Failed damage-triggered D20 debuff expiry for %s.", state.template.name)
        raise RuntimeError("Damage-triggered D20 debuff could not expire.") from exc
