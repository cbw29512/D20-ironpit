from __future__ import annotations

import logging

from app.combat.action_economy import is_available
from app.combat.resources import resource_available, spend_resource
from app.combat.spellcasting import legal_slot_levels, mark_slot_spell_cast
from app.domain.models import CombatantState, WeaponAttack
from app.domain.post_hit_damage import ResourceBackedPostHitDamage
from app.domain.post_hit_spell import PostHitSpellOption

logger = logging.getLogger(__name__)


def _slot_payment(state: CombatantState, min_level: int, max_level: int, turn_key: str) -> int | None:
    levels = [
        level
        for level in legal_slot_levels(state, turn_key, min_level, higher_slot_scaling=True)
        if level <= max_level
    ]
    return max(levels) if levels else None


def expected_post_hit_dice(rule: ResourceBackedPostHitDamage | PostHitSpellOption, slot_level: int) -> float:
    extra = max(0, slot_level - rule.level if isinstance(rule, PostHitSpellOption) else slot_level - rule.printed_spell_level)
    count = rule.base_dice_count + extra * rule.dice_per_slot_above
    return count * (rule.dice_size + 1) / 2


def choose_post_hit_spell(
    attacker: CombatantState,
    attack: WeaponAttack,
    turn_key: str,
) -> tuple[PostHitSpellOption, int] | None:
    """Choose the highest-damage legal extra smite that can spend its Bonus Action and slot."""
    try:
        if not is_available(attacker, "bonus_action"):
            return None
        best: tuple[float, PostHitSpellOption, int] | None = None
        for option in attacker.template.progression_features.post_hit_spell_options:
            if attack.id not in option.trigger_attack_ids:
                continue
            slot = _slot_payment(attacker, option.level, option.max_slot_level, turn_key)
            if slot is None:
                continue
            score = expected_post_hit_dice(option, slot)
            if best is None or score > best[0]:
                best = (score, option, slot)
        return None if best is None else (best[1], best[2])
    except Exception:
        logger.exception("Failed extra-smite choice for %s.", attacker.template.name)
        raise


def divine_smite_expected(attacker: CombatantState, turn_key: str) -> float:
    rule = attacker.template.progression_features.resource_backed_post_hit_damage
    if rule is None:
        return 0.0
    scores = []
    if rule.free_resource_id and resource_available(attacker, rule.free_resource_id, 1):
        scores.append(expected_post_hit_dice(rule, rule.printed_spell_level))
    slot = _slot_payment(attacker, rule.printed_spell_level, rule.max_slot_level, turn_key)
    if slot is not None:
        scores.append(expected_post_hit_dice(rule, slot))
    return max(scores) if scores else 0.0


def extra_smite_beats_divine(
    attacker: CombatantState,
    attack: WeaponAttack,
    turn_key: str,
) -> bool:
    choice = choose_post_hit_spell(attacker, attack, turn_key)
    if choice is None:
        return False
    option, slot = choice
    return expected_post_hit_dice(option, slot) > divine_smite_expected(attacker, turn_key)


def pay_post_hit_spell(
    attacker: CombatantState,
    option: PostHitSpellOption,
    slot_level: int,
    turn_key: str,
) -> None:
    try:
        from app.combat.action_economy import spend
        spend(attacker, option.action_cost)
        mark_slot_spell_cast(attacker, turn_key)
        spend_resource(attacker, f"spell-slot-{slot_level}", 1)
        attacker.feature_last_turn_keys[option.id] = turn_key
        attacker.feature_last_turn_keys["paid-post-hit-spell"] = option.id
        attacker.feature_last_turn_keys["paid-post-hit-slot"] = str(slot_level)
    except Exception:
        logger.exception("Failed to pay extra smite %s.", option.id)
        raise
