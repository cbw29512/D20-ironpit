from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.condition_rules import close_hit_is_automatic_critical
from app.combat.conditions import attack_roll_condition_sources
from app.combat.damage_defenses import apply_damage_defenses
from app.combat.encounter_targeting import close_ranged_threat_exists, combatant_distance
from app.combat.heroic_inspiration import reroll_failed_attack_with_heroic_inspiration
from app.combat.modifier_stack import (
    add_modifier, apply_d20_bonus_dice, attacks_against_advantage_sources,
    consume_attacks_against_advantage, consume_next_attack_against_advantage,
    effective_armor_class, next_attack_against_advantage_sources,
)
from app.combat.reckless_attack import attacks_against_reckless_advantage
from app.combat.rolls import attack_roll_hits, resolve_roll_mode, roll_d20
from app.combat.sap import consume_sap, sap_disadvantage
from app.combat.spell_modifiers import build_spell_modifier
from app.combat.spellcasting import mark_slot_spell_cast, slot_spell_available
from app.combat.zero_hp import apply_damage
from app.domain.combatants import DamageType
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent, DamageRollComponent, DiceRoll
from app.domain.modifiers import ModifierKind
from app.domain.spells import SpellAttackAction

logger = logging.getLogger(__name__)


def _slot_resource(caster: EncounterCombatant, spell: SpellAttackAction, turn_key: str):
    if spell.level == 0 or not slot_spell_available(caster.state, turn_key):
        return None
    return next((item for item in caster.state.resources if item.id == f"spell-slot-{spell.level}" and item.current_uses > 0), None)


def _damage(spell: SpellAttackAction, critical: bool, dice):
    count = spell.damage_dice_count * (2 if critical else 1)
    rolls = [dice.roll(spell.damage_dice_size) for _ in range(count)]
    total = sum(rolls) + spell.damage_bonus; notation = f"{count}d{spell.damage_dice_size}+{spell.damage_bonus}"
    damage_type = DamageType(spell.damage_type) if spell.damage_type else None
    if damage_type is None:
        return DiceRoll(notation=notation, rolls=rolls, modifier=spell.damage_bonus, total=total), []
    component = DamageRollComponent(source=spell.name, notation=notation, rolls=rolls, modifier=spell.damage_bonus, damage_type=damage_type, total=total)
    return DiceRoll(notation=notation, rolls=rolls, modifier=spell.damage_bonus, total=total), [component]


def resolve_spell_attack(
    sequence: int, round_number: int, caster: EncounterCombatant, target: EncounterCombatant,
    spell: SpellAttackAction, setup: EncounterSetup, turn_key: str, dice,
) -> BattleEvent:
    try:
        if spell.action_cost == "reaction" or not is_available(caster.state, spell.action_cost):
            raise ValueError(f"{spell.name} cannot be cast in this action window.")
        if target.side == caster.side or target.state.is_dead or not target.state.is_alive:
            raise ValueError(f"{spell.name} requires a living enemy target.")
        distance = combatant_distance(caster, target)
        if distance > spell.range_ft:
            raise ValueError(f"{spell.name} target is out of range.")
        resource = _slot_resource(caster, spell, turn_key)
        if spell.level > 0 and resource is None:
            raise ValueError(f"No level {spell.level} spell slot remains for {spell.name}.")
        condition_advantage, condition_disadvantage = attack_roll_condition_sources(
            caster.state, target.state, distance, target.combatant_id,
        )
        advantage = condition_advantage + attacks_against_advantage_sources(target.state)
        advantage += attacks_against_reckless_advantage(target.state)
        advantage += next_attack_against_advantage_sources(caster.state, target.combatant_id)
        close_threat = spell.attack_kind == "ranged" and close_ranged_threat_exists(caster, setup)
        mode = resolve_roll_mode(advantage, condition_disadvantage + sap_disadvantage(caster.state) + int(close_threat))
        target_ac = effective_armor_class(target.state)
        base_roll = roll_d20(dice, spell.attack_bonus, mode)
        base_roll, heroic_reroll = reroll_failed_attack_with_heroic_inspiration(caster.state, base_roll, target_ac, dice)
        attack_roll = apply_d20_bonus_dice(caster.state, ModifierKind.ATTACK_ROLL_BONUS_DIE, base_roll, dice)
        consume_next_attack_against_advantage(caster.state, target.combatant_id)
        consume_sap(caster.state); consume_attacks_against_advantage(target.state)
        if resource is not None:
            mark_slot_spell_cast(caster.state, turn_key); resource.current_uses -= 1
        spend(caster.state, spell.action_cost)
        natural = attack_roll.selected_roll or 0
        hit = attack_roll_hits(natural, attack_roll.total, target_ac)
        critical = bool(hit and (natural == 20 or (close_hit_is_automatic_critical(target.state) and distance <= 5)))
        hp_before = target.state.current_hp; temporary_hp_before = target.state.temporary_hp
        death_success_before = target.state.death_save_successes; death_failure_before = target.state.death_save_failures
        concentration_before = target.state.concentration.effect_id if target.state.concentration else None
        damage_roll = None; damage_components = []
        if hit:
            damage_roll, rolled = _damage(spell, critical, dice)
            applied_total, damage_components = apply_damage_defenses(target.state, rolled); damage_roll.total = applied_total
            affected_states = [entry.state for entry in [*setup.heroes, *setup.monsters]]
            apply_damage(target.state, applied_total, critical=critical,
                         damage_types={part.damage_type for part in damage_components if part.applied_total}, dice=dice, affected_states=affected_states)
            if target.state.is_alive and not target.state.is_dead:
                for index, effect in enumerate(spell.on_hit_modifier_effects):
                    add_modifier(target.state, build_spell_modifier(
                        caster.combatant_id, target.combatant_id, spell.id, effect, index, round_number=round_number,
                    ))
        remaining = resource.current_uses if resource is not None else None
        outcome = "CRITICAL HIT" if critical else "HIT" if hit else "MISS"
        description = f"{caster.state.template.name}: {outcome} with {spell.name}."
        if heroic_reroll:
            description += " Heroic Inspiration rerolls one d20."
        return BattleEvent(
            sequence=sequence, round_number=round_number, event_type="attack", actor_id=caster.combatant_id, actor_name=caster.state.template.name,
            target_id=target.combatant_id, target_name=target.state.template.name, attack_name=spell.name, target_ac=target_ac,
            attack_roll=attack_roll, damage_roll=damage_roll, damage_components=damage_components, hit=hit, critical=critical,
            hp_before=hp_before, hp_after=target.state.current_hp, temporary_hp_before=temporary_hp_before, temporary_hp_after=target.state.temporary_hp,
            death_save_successes_before=death_success_before, death_save_failures_before=death_failure_before,
            death_save_successes=target.state.death_save_successes, death_save_failures=target.state.death_save_failures,
            is_stable=target.state.is_stable, is_dead=target.state.is_dead, feature_id=spell.id, resource_remaining=remaining,
            concentration_ended_effect_id=concentration_before if concentration_before and target.state.concentration is None else None,
            animation=spell.animation, description=description,
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Spell attack failed: %s -> %s with %s.", caster.combatant_id, target.combatant_id, spell.id)
        raise RuntimeError("Spell attack could not be resolved.") from exc
