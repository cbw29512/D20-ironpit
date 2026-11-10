"""Universal no-save HP-pool spell cast: existing economy, pool, and timed effect."""
from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.alternate_spell_casts import spend_alternate_cast
from app.combat.defensive_modifier_rules import remove_owner_attack_ending_modifiers
from app.combat.hit_point_pool import PoolCandidate, allocate_hit_point_pool
from app.combat.hit_point_pool_spell_policy import PoolSpellChoice, eligible_pool_target
from app.combat.owner_action_expiry import expire_on_owner_event
from app.combat.spell_area import best_area_placement
from app.combat.spellcasting import mark_slot_spell_cast, slot_spell_available
from app.combat.suppression_zone_geometry import verbal_casting_blocked
from app.combat.timed_conditions import apply_timed_condition
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent, DiceRoll

logger = logging.getLogger(__name__)


def resolve_hp_pool_spell(
    sequence: int, round_number: int, caster: EncounterCombatant,
    setup: EncounterSetup, choice: PoolSpellChoice, turn_key: str, dice,
) -> tuple[list[BattleEvent], int]:
    """Spend the declared spell cast, roll one pool, then apply generic conditions."""
    try:
        action = choice.action
        if action not in caster.state.template.hit_point_pool_spell_actions:
            raise ValueError("HP-pool spell choice is not declared by caster.")
        if action.action_cost == "reaction" or not is_available(caster.state, action.action_cost):
            raise ValueError(f"{action.name} requires an available casting Action.")
        if verbal_casting_blocked(caster, setup):
            raise ValueError(f"{action.name} cannot be cast inside Silence.")
        if not action.level <= choice.slot_level <= 9:
            raise ValueError("Illegal HP-pool cast level.")
        enemies = setup.monsters if caster.side == "heroes" else setup.heroes
        eligible_ids = {
            member.combatant_id for member in enemies
            if eligible_pool_target(caster, member, action, setup)
        }
        expected_placement = best_area_placement(
            caster, setup, action.area_radius_ft, action.range_ft,
            eligible_enemy_ids=eligible_ids,
        )
        if expected_placement is None or expected_placement != choice.placement:
            raise ValueError("HP-pool spell placement is no longer a legal ally-safe area.")
        members = [*setup.heroes, *setup.monsters]
        by_id = {member.combatant_id: member for member in members}
        candidates = [
            PoolCandidate(
                combatant_id=target_id,
                current_hp=by_id[target_id].state.current_hp,
                eligible=eligible_pool_target(caster, by_id[target_id], action, setup),
            )
            for target_id in choice.placement.enemy_ids
        ]
        if not any(item.eligible for item in candidates):
            raise ValueError("HP-pool spell no longer has an eligible creature.")
        resource = None
        remaining = None
        if choice.alternate_cast is not None:
            grant = choice.alternate_cast
            if grant.spell_id != action.id or grant.cast_level != choice.slot_level:
                raise ValueError("Wrong alternate spell grant for HP-pool casting.")
            # Generic alternate-cast spender validates daily uses.
            remaining = spend_alternate_cast(caster.state, grant)
        else:
            if not slot_spell_available(caster.state, turn_key):
                raise ValueError("A spell slot has already been used this turn.")
            resource = next(
                (entry for entry in caster.state.resources
                 if entry.id == f"spell-slot-{choice.slot_level}" and entry.current_uses > 0), None,
            )
            if resource is None:
                raise ValueError(f"No level {choice.slot_level} slot for {action.name}.")
            mark_slot_spell_cast(caster.state, turn_key)
            resource.current_uses -= 1
            remaining = resource.current_uses

        expire_on_owner_event(caster.state, "spell_cast", [m.state for m in members])
        spend(caster.state, action.action_cost)
        remove_owner_attack_ending_modifiers(caster.state)

        dice_count = action.pool_dice_count + (
            choice.slot_level - action.level
        ) * action.extra_dice_per_upcast_level
        rolls = [dice.roll(action.pool_dice_size) for _ in range(dice_count)]
        affected, leftover = allocate_hit_point_pool(sum(rolls), candidates)
        resource_name = (
            choice.alternate_cast.source_name if choice.alternate_cast is not None
            else f"level {choice.slot_level} slot"
        )
        events = [BattleEvent(
            sequence=sequence, round_number=round_number, event_type="feature",
            actor_id=caster.combatant_id, actor_name=caster.state.template.name,
            feature_id=action.id, resource_remaining=remaining,
            feature_roll=DiceRoll(
                notation=f"{dice_count}d{action.pool_dice_size}",
                rolls=rolls, modifier=0, total=sum(rolls),
            ),
            animation=action.animation,
            description=(
                f"{caster.state.template.name} casts {action.name} using {resource_name}: "
                f"{sum(rolls)} HP in the pool; {leftover} HP unused."
            ),
        )]
        sequence += 1
        for target_id in affected:
            target = by_id[target_id]
            applied = apply_timed_condition(
                target.state, action.condition_id, caster.combatant_id,
                source_effect_id=action.id,
                source_template=caster.state.template,
                source_is_magical=True, affected_states=[m.state for m in members],
                target_actor=target, setup=setup,
                applied_round=round_number,
                expires_round=round_number + action.duration_rounds,
                expiry_timing=action.expiry_timing,
                ends_on_damage=action.ends_on_damage,
                allowed_removal_action_ids=list(action.allowed_removal_action_ids),
                use_default_poison_recovery=False,
            )
            events.append(BattleEvent(
                sequence=sequence, round_number=round_number, event_type="feature",
                actor_id=caster.combatant_id, actor_name=caster.state.template.name,
                target_id=target.combatant_id, target_name=target.state.template.name,
                feature_id=action.id,
                applied_condition_ids=[applied] if applied else [],
                animation=action.animation,
                description=(
                    f"{target.state.template.name} is affected by {action.name} "
                    f"and becomes {action.condition_id}."
                    if applied else f"{target.state.template.name} resists {action.name}."
                ),
            ))
            sequence += 1
        return events, sequence
    except ValueError:
        raise
    except Exception:
        logger.exception("HP-pool cast failed: %s by %s.", choice.action.id, caster.combatant_id)
        raise
