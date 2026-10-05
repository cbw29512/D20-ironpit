from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.resources import resource_available, spend_resource
from app.combat.spellcasting import legal_slot_levels, mark_slot_spell_cast
from app.content.monster_creature_types import base_creature_type
from app.domain.models import CombatantState, DamageType, WeaponAttack
from app.domain.post_hit_damage import ResourceBackedPostHitDamage

logger = logging.getLogger(__name__)
BonusDamageSpec = tuple[str, int, int, int, DamageType, str]


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
        if target is None or target.current_hp <= 0 or target.is_dead or not target.is_alive:
            return None
        features = attacker.template.progression_features
        if (
            not features.post_hit_spell_options
            and features.resource_backed_post_hit_damage is None
        ):
            return None
        if not turn_key:
            raise ValueError("Post-hit resource damage requires the active turn key.")
        from app.combat.post_hit_spell_policy import (
            choose_post_hit_spell,
            extra_smite_beats_divine,
            pay_post_hit_spell,
        )
        extra = choose_post_hit_spell(attacker, attack, turn_key)
        rule = attacker.template.progression_features.resource_backed_post_hit_damage
        divine_ready = (
            rule is not None
            and attack.id in rule.trigger_attack_ids
            and is_available(attacker, rule.action_cost)
            and _payment(attacker, rule, turn_key) is not None
        )
        if extra is not None and (not divine_ready or extra_smite_beats_divine(attacker, attack, turn_key)):
            option, slot_level = extra
            pay_post_hit_spell(attacker, option, slot_level, turn_key)
            count = option.base_dice_count + option.dice_per_slot_above * (slot_level - option.level)
            return option.name, count, option.dice_size, 0, DamageType(option.damage_type), option.id
        if not divine_ready:
            return None
        payment = _payment(attacker, rule, turn_key)
        if payment is None:
            return None
        resource_id, slot_level, expends_slot = payment

        spend(attacker, rule.action_cost)
        if expends_slot:
            mark_slot_spell_cast(attacker, turn_key)
        spend_resource(attacker, resource_id, 1)

        count = rule.base_dice_count + rule.dice_per_slot_above * (
            slot_level - rule.printed_spell_level
        )
        if base_creature_type(target.template.creature_type) in rule.bonus_target_creature_types:
            count += rule.bonus_target_dice_count
        return rule.source_name, count, rule.dice_size, 0, DamageType(rule.damage_type), rule.source_id
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Post-hit resource damage failed for %s.", attacker.template.name)
        raise RuntimeError("Post-hit resource damage could not be resolved.") from exc
