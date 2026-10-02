from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.damage_defenses import apply_damage_defenses
from app.combat.resources import resource_available, spend_resource
from app.combat.spellcasting import legal_slot_levels, mark_slot_spell_cast
from app.combat.zero_hp import apply_damage
from app.content.monster_creature_types import base_creature_type
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent, DamageRollComponent, DiceRoll
from app.domain.models import DamageType
from app.domain.post_hit_damage import ResourceBackedPostHitDamage

logger = logging.getLogger(__name__)


def _payment(state, rule: ResourceBackedPostHitDamage, turn_key: str) -> tuple[str, int, bool] | None:
    if rule.free_resource_id and resource_available(state, rule.free_resource_id, 1):
        return rule.free_resource_id, rule.printed_spell_level, False
    levels = [
        level for level in legal_slot_levels(
            state, turn_key, rule.printed_spell_level, higher_slot_scaling=True,
        )
        if level <= rule.max_slot_level
    ]
    if not levels:
        return None
    level = max(levels)
    return f"spell-slot-{level}", level, True


def resolve_post_hit_damage(
    sequence: int,
    round_number: int,
    source: EncounterCombatant,
    target: EncounterCombatant,
    attack_id: str,
    critical: bool,
    setup: EncounterSetup,
    dice,
    turn_key: str,
) -> BattleEvent | None:
    """Resolve one optional post-hit damage rule after the triggering attack is complete."""
    try:
        rule = source.state.template.progression_features.resource_backed_post_hit_damage
        if rule is None or attack_id not in rule.trigger_attack_ids:
            return None
        if target.state.current_hp <= 0 or target.state.is_dead or not target.state.is_alive:
            return None
        if not is_available(source.state, rule.action_cost):
            return None
        payment = _payment(source.state, rule, turn_key)
        if payment is None:
            return None
        resource_id, slot_level, expends_slot = payment

        spend(source.state, rule.action_cost)
        if expends_slot:
            mark_slot_spell_cast(source.state, turn_key)
        remaining = spend_resource(source.state, resource_id, 1)

        count = rule.base_dice_count + rule.dice_per_slot_above * (slot_level - rule.printed_spell_level)
        target_type = base_creature_type(target.state.template.creature_type)
        if target_type in rule.bonus_target_creature_types:
            count += rule.bonus_target_dice_count
        rolled_count = count * (2 if critical and rule.doubles_on_critical else 1)
        rolls = [dice.roll(rule.dice_size) for _ in range(rolled_count)]
        damage_type = DamageType(rule.damage_type)
        raw = DamageRollComponent(
            source=rule.source_name,
            notation=f"{rolled_count}d{rule.dice_size}",
            rolls=rolls,
            modifier=0,
            damage_type=damage_type,
            total=sum(rolls),
        )
        applied_total, components = apply_damage_defenses(target.state, [raw])
        hp_before = target.state.current_hp
        temp_before = target.state.temporary_hp
        if applied_total:
            apply_damage(
                target.state,
                applied_total,
                critical=critical,
                damage_types={damage_type},
                dice=dice,
                affected_states=[member.state for member in [*setup.heroes, *setup.monsters]],
            )
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=source.combatant_id,
            actor_name=source.state.template.name,
            target_id=target.combatant_id,
            target_name=target.state.template.name,
            feature_id=rule.source_id,
            damage_roll=DiceRoll(
                notation=f"{rolled_count}d{rule.dice_size}",
                rolls=rolls,
                modifier=0,
                total=applied_total,
            ),
            damage_components=components,
            hp_before=hp_before,
            hp_after=target.state.current_hp,
            temporary_hp_before=temp_before,
            temporary_hp_after=target.state.temporary_hp,
            resource_remaining=remaining,
            animation="radiant",
            description=(
                f"{source.state.template.name} casts {rule.source_name} after the hit, "
                f"dealing {applied_total} {rule.damage_type} damage."
            ),
        )
    except Exception:
        logger.exception("Post-hit damage resolution failed for %s.", source.combatant_id)
        raise
