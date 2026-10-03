from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.resources import resource_available, spend_resource
from app.combat.spellcasting import legal_slot_levels, mark_slot_spell_cast
from app.content.monster_creature_types import base_creature_type
from app.domain.models import CombatantState, DamageType, WeaponAttack
from app.domain.runtime import TimedEffect
from app.domain.post_hit_damage import ResourceBackedPostHitDamage

logger = logging.getLogger(__name__)


def _activate_on_use_self_effect(state: CombatantState, rule: ResourceBackedPostHitDamage, turn_key: str) -> None:
    if rule.on_use_self_effect_id is None:
        return
    try:
        round_text, source_id = turn_key.split(":", 1)
        round_number = int(round_text)
        if not source_id:
            raise ValueError("Timed self-effect activation requires a source id in the turn key.")
        state.timed_effects = [
            effect for effect in state.timed_effects
            if not (
                effect.source_id == source_id
                and effect.source_effect_id == rule.on_use_self_effect_id
            )
        ]
        state.timed_effects.append(TimedEffect(
            effect_id=rule.on_use_self_effect_id,
            source_id=source_id,
            source_effect_id=rule.on_use_self_effect_id,
            applied_round=round_number,
            expiry_timing="source_turn_start",
        ))
    except (TypeError, ValueError):
        raise
    except Exception as exc:
        logger.exception("Failed to activate post-hit timed self effect %s.", rule.on_use_self_effect_id)
        raise RuntimeError("Post-hit timed self effect could not be activated.") from exc


BonusDamageSpec = tuple[str, int, int, int, DamageType]


def _payment(
    state: CombatantState,
    rule: ResourceBackedPostHitDamage,
    turn_key: str,
) -> tuple[str, int, bool] | None:
    if rule.free_resource_id and resource_available(state, rule.free_resource_id, 1):
        return rule.free_resource_id, rule.printed_spell_level, False
    levels = [
        level
        for level in legal_slot_levels(
            state,
            turn_key,
            rule.printed_spell_level,
            higher_slot_scaling=True,
        )
        if level <= rule.max_slot_level
    ]
    if not levels:
        return None
    level = max(levels)
    return f"spell-slot-{level}", level, True


def post_hit_resource_bonus_damage(
    attacker: CombatantState,
    target: CombatantState | None,
    attack: WeaponAttack,
    turn_key: str | None,
) -> BonusDamageSpec | None:
    """Pay for and return damage that becomes part of a confirmed attack hit."""
    try:
        rule = attacker.template.progression_features.resource_backed_post_hit_damage
        if rule is None or attack.id not in rule.trigger_attack_ids:
            return None
        if target is None or target.current_hp <= 0 or target.is_dead or not target.is_alive:
            return None
        if not turn_key:
            raise ValueError("Post-hit resource damage requires the active turn key.")
        if not is_available(attacker, rule.action_cost):
            return None
        payment = _payment(attacker, rule, turn_key)
        if payment is None:
            return None
        resource_id, slot_level, expends_slot = payment

        spend(attacker, rule.action_cost)
        if expends_slot:
            mark_slot_spell_cast(attacker, turn_key)
        spend_resource(attacker, resource_id, 1)
        _activate_on_use_self_effect(attacker, rule, turn_key)

        count = rule.base_dice_count + rule.dice_per_slot_above * (
            slot_level - rule.printed_spell_level
        )
        if base_creature_type(target.template.creature_type) in rule.bonus_target_creature_types:
            count += rule.bonus_target_dice_count
        return rule.source_name, count, rule.dice_size, 0, DamageType(rule.damage_type)
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Post-hit resource damage failed for %s.", attacker.template.name)
        raise RuntimeError("Post-hit resource damage could not be resolved.") from exc
