from __future__ import annotations

from app.combat.undead_fortitude import consume_survival_save_log
from app.combat.zero_hp_replacement import consume_zero_hp_replacement_log

import logging

from app.combat.action_economy import is_available, spend
from app.combat.condition_rules import close_hit_is_automatic_critical
from app.combat.conditions import attack_roll_condition_sources
from app.combat.damage_defenses import apply_damage_defenses
from app.combat.encounter_targeting import close_ranged_threat_exists, combatant_distance
from app.combat.heroic_inspiration import reroll_failed_attack_with_heroic_inspiration
from app.combat.next_attack_disadvantage import (
    consume_next_attack_disadvantage,
    next_attack_disadvantage_sources,
)
from app.combat.modifier_stack import (
    add_modifier, apply_d20_bonus_dice, attacks_against_advantage_sources,
    consume_attacks_against_advantage, consume_next_attack_against_advantage,
    effective_armor_class, next_attack_against_advantage_sources,
)
from app.combat.reckless_attack import attacks_against_reckless_advantage
from app.combat.reaction_roll_penalties import apply_reaction_roll_penalty_if_useful
from app.combat.rolls import resolve_roll_mode, roll_d20
from app.combat.sap import consume_sap, sap_disadvantage
from app.combat.spell_cast_effects import apply_spell_cast_timed_resistance
from app.combat.spell_modifiers import build_spell_modifier
from app.combat.spell_range_modifiers import spend_spell_range_modifier
from app.combat.spellcasting import mark_slot_spell_cast
from app.combat.spell_attack_helpers import roll_spell_attack_damage, slot_resource
from app.combat.targeting_wards import blocked_targeting_event, check_targeting_ward
from app.combat.timed_conditions import apply_timed_condition
from app.combat.zero_hp import apply_damage
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent
from app.domain.modifiers import ModifierKind
from app.domain.spell_cast_modifiers import ResourceBackedSpellRangeModifier
from app.domain.spells import SpellAttackAction

logger = logging.getLogger(__name__)



def resolve_spell_attack(
    sequence: int, round_number: int, caster: EncounterCombatant, target: EncounterCombatant,
    spell: SpellAttackAction, setup: EncounterSetup, turn_key: str, dice,
    *, distance_override_ft: int | None = None,
    range_modifier: ResourceBackedSpellRangeModifier | None = None,
    cast_slot_level: int | None = None,
    spend_cast_costs: bool = True,
) -> BattleEvent:
    try:
        if spell.action_cost == "reaction":
            raise ValueError(f"{spell.name} cannot be cast in this action window.")
        if spend_cast_costs and not is_available(caster.state, spell.action_cost):
            raise ValueError(f"{spell.name} cannot be cast in this action window.")
        if target.side == caster.side or target.state.is_dead or not target.state.is_alive:
            raise ValueError(f"{spell.name} requires a living enemy target.")
        distance = combatant_distance(caster, target) if distance_override_ft is None else distance_override_ft
        allowed_range = spell.range_ft * (range_modifier.range_multiplier if range_modifier is not None else 1)
        if distance > allowed_range:
            raise ValueError(f"{spell.name} target is out of range.")
        resource = None
        if spend_cast_costs and spell.level > 0:
            if cast_slot_level is None:
                resource = slot_resource(caster, spell, turn_key)
            else:
                if cast_slot_level < spell.level or cast_slot_level > 9:
                    raise ValueError(f"Illegal slot level {cast_slot_level} for {spell.name}.")
                resource = next(
                    (
                        item for item in caster.state.resources
                        if item.id == f"spell-slot-{cast_slot_level}" and item.current_uses > 0
                    ),
                    None,
                )
            if resource is None:
                requested = cast_slot_level if cast_slot_level is not None else spell.level
                raise ValueError(f"No level {requested} spell slot remains for {spell.name}.")
        ward = check_targeting_ward(caster, target, dice)
        if ward is not None and not ward.succeeded:
            if resource is not None:
                mark_slot_spell_cast(caster.state, turn_key); resource.current_uses -= 1
            if spend_cast_costs:
                spend(caster.state, spell.action_cost)
            range_remaining = (
                spend_spell_range_modifier(caster.state, range_modifier)
                if spend_cast_costs else None
            )
            if spend_cast_costs:
                apply_spell_cast_timed_resistance(caster, spell, round_number)
            event = blocked_targeting_event(sequence, round_number, caster, target, spell.name, ward)
            event.resource_remaining = resource.current_uses if resource is not None else range_remaining
            if range_modifier is not None:
                event.description += f" {caster.state.template.name} uses {range_modifier.name}."
            return event
        condition_advantage, condition_disadvantage = attack_roll_condition_sources(
            caster.state, target.state, distance, target.combatant_id,
        )
        advantage = condition_advantage + attacks_against_advantage_sources(target.state)
        advantage += attacks_against_reckless_advantage(target.state)
        advantage += int(
            spell.advantage_if_target_wearing_metal_armor
            and target.state.template.wearing_metal_armor
        )
        advantage += next_attack_against_advantage_sources(caster.state, target.combatant_id)
        close_threat = spell.attack_kind == "ranged" and close_ranged_threat_exists(caster, setup)
        mode = resolve_roll_mode(
            advantage,
            condition_disadvantage
            + sap_disadvantage(caster.state)
            + next_attack_disadvantage_sources(caster.state)
            + int(close_threat),
        )
        target_ac = effective_armor_class(target.state)
        base_roll = roll_d20(dice, spell.attack_bonus, mode)
        base_roll, heroic_reroll = reroll_failed_attack_with_heroic_inspiration(caster.state, base_roll, target_ac, dice)
        attack_roll = apply_d20_bonus_dice(caster.state, ModifierKind.ATTACK_ROLL_BONUS_DIE, base_roll, dice)
        reaction_penalty = apply_reaction_roll_penalty_if_useful(
            caster, setup, "attack", attack_roll, dice, threshold=target_ac,
        )
        if reaction_penalty is not None:
            attack_roll = reaction_penalty.roll
        consume_next_attack_against_advantage(caster.state, target.combatant_id)
        consume_next_attack_disadvantage(caster.state)
        consume_sap(caster.state); consume_attacks_against_advantage(target.state)
        if resource is not None:
            mark_slot_spell_cast(caster.state, turn_key); resource.current_uses -= 1
        if spend_cast_costs:
            spend(caster.state, spell.action_cost)
        range_remaining = (
            spend_spell_range_modifier(caster.state, range_modifier)
            if spend_cast_costs else None
        )
        if spend_cast_costs:
            apply_spell_cast_timed_resistance(caster, spell, round_number)
        natural = attack_roll.selected_roll or 0
        hit = natural != 1 and (natural == 20 or attack_roll.total >= target_ac)
        critical = bool(hit and (natural == 20 or (close_hit_is_automatic_critical(target.state) and distance <= 5)))
        hp_before = target.state.current_hp; temporary_hp_before = target.state.temporary_hp
        death_success_before = target.state.death_save_successes; death_failure_before = target.state.death_save_failures
        concentration_before = target.state.concentration.effect_id if target.state.concentration else None
        damage_roll = None; damage_components = []; applied_conditions: list[str] = []
        if hit:
            damage_roll, rolled = roll_spell_attack_damage(
                spell, critical, dice, attacker=caster.state, target_event_id=target.combatant_id,
            )
            applied_total, damage_components = apply_damage_defenses(target.state, rolled); damage_roll.total = applied_total
            affected_states = [entry.state for entry in [*setup.heroes, *setup.monsters]]
            apply_damage(target.state, applied_total, critical=critical,
                         damage_types={part.damage_type for part in damage_components if part.applied_total}, dice=dice, affected_states=affected_states)
            if target.state.is_alive and not target.state.is_dead:
                for index, effect in enumerate(spell.on_hit_modifier_effects):
                    add_modifier(target.state, build_spell_modifier(
                        caster.combatant_id, target.combatant_id, spell.id, effect, index, spell.name, round_number=round_number,
                    ))
                for effect in spell.on_hit_timed_effects:
                    applied = apply_timed_condition(
                        target.state,
                        effect.effect_id,
                        caster.combatant_id,
                        source_effect_id=spell.id,
                        source_template=caster.state.template,
                        source_is_magical=effect.source_is_magical,
                        suppress_action=effect.suppress_action,
                        suppress_bonus_action=effect.suppress_bonus_action,
                        suppress_reactions=effect.suppress_reactions,
                        suppress_movement=effect.suppress_movement,
                        next_attack_disadvantage=effect.next_attack_disadvantage,
                        applied_round=round_number,
                        expires_round=round_number + effect.duration_rounds,
                        expiry_timing=effect.expiry_timing,
                        affected_states=affected_states,
                        use_default_poison_recovery=False,
                    )
                    if applied is not None:
                        applied_conditions.append(applied)
        remaining = resource.current_uses if resource is not None else None
        outcome = "CRITICAL HIT" if critical else "HIT" if hit else "MISS"
        description = f"{caster.state.template.name}: {outcome} with {spell.name}."
        if range_modifier is not None:
            description += f" {caster.state.template.name} uses {range_modifier.name}."
        if heroic_reroll:
            description += " Heroic Inspiration rerolls one d20."
        if reaction_penalty is not None:
            description += (
                f" {reaction_penalty.source_name} uses {reaction_penalty.action_id} "
                f"to subtract {reaction_penalty.penalty_total} from the attack roll."
            )
        if ward is not None:
            description += f" {caster.state.template.name} succeeds against {ward.gate.source_effect_id}."
        event = BattleEvent(
            sequence=sequence, round_number=round_number, event_type="attack", actor_id=caster.combatant_id, actor_name=caster.state.template.name,
            target_id=target.combatant_id, target_name=target.state.template.name, attack_name=spell.name, target_ac=target_ac,
            attack_roll=attack_roll, damage_roll=damage_roll, damage_components=damage_components,
            applied_condition_ids=applied_conditions, hit=hit, critical=critical,
            hp_before=hp_before, hp_after=target.state.current_hp, temporary_hp_before=temporary_hp_before, temporary_hp_after=target.state.temporary_hp,
            death_save_successes_before=death_success_before, death_save_failures_before=death_failure_before,
            death_save_successes=target.state.death_save_successes, death_save_failures=target.state.death_save_failures,
            is_stable=target.state.is_stable, is_dead=target.state.is_dead, feature_id=spell.id,
            resource_remaining=remaining if resource is not None else range_remaining,
            concentration_ended_effect_id=concentration_before if concentration_before and target.state.concentration is None else None,
            animation=spell.animation, description=description + consume_survival_save_log(target.state) + consume_zero_hp_replacement_log(target.state),
        )
        if ward is not None and event.saving_throw_roll is None:
            event.saving_throw_roll = ward.roll
            event.save_ability = ward.gate.save_ability
            event.save_dc = ward.gate.save_dc
            event.save_succeeded = True
        return event
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Spell attack failed: %s -> %s with %s.", caster.combatant_id, target.combatant_id, spell.id)
        raise RuntimeError("Spell attack could not be resolved.") from exc
