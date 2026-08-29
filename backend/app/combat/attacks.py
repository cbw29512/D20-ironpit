from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.barbarian import end_rage_if_incapacitated, extend_rage_from_attack
from app.combat.bloodied import bloodied_fury_advantage
from app.combat.concentration import concentration_after_damage
from app.combat.condition_rules import close_hit_is_automatic_critical
from app.combat.conditions import apply_hit_conditions, attack_roll_condition_sources
from app.combat.damage import BonusDamageSpec, resolve_weapon_damage
from app.combat.damage_defenses import apply_damage_defenses
from app.combat.dice import DiceProvider
from app.combat.range import resolve_attack_roll_mode
from app.combat.rolls import roll_d20
from app.combat.sanctuary import sanctuary_targeting_save
from app.combat.support_effects import bless_bonus, end_sanctuary
from app.combat.zero_hp import apply_damage
from app.domain.models import BattleEvent, CombatantState, EncounterSetup, WeaponAttack

logger = logging.getLogger(__name__)


def resolve_attack(
    sequence: int, round_number: int, attacker: CombatantState, defender: CombatantState,
    attack: WeaponAttack, distance_ft: int, dice: DiceProvider,
    actor_event_id: str | None = None, target_event_id: str | None = None,
    spend_action: bool = True, advantage_sources: int = 0, other_disadvantage_sources: int = 0,
    feature_id: str | None = None, turn_key: str | None = None,
    bonus_damage: BonusDamageSpec | None = None, encounter_setup: EncounterSetup | None = None,
) -> BattleEvent:
    try:
        if spend_action and not is_available(attacker, "action"):
            raise ValueError("Action is not available for an attack.")
        weapon = attack.weapon
        defender_id = target_event_id or defender.template.id
        attacker_id = actor_event_id or attacker.template.id
        ward_roll, ward_ok, ward_dc = sanctuary_targeting_save(attacker, defender, dice)
        if not ward_ok:
            if spend_action:
                spend(attacker, "action")
            return BattleEvent(
                sequence=sequence, round_number=round_number, event_type="attack",
                actor_id=attacker_id, actor_name=attacker.template.name,
                target_id=defender_id, target_name=defender.template.name,
                saving_throw_roll=ward_roll, save_ability="wisdom", save_dc=ward_dc,
                save_succeeded=False, hit=False, weapon_id=weapon.id, projectile=weapon.projectile,
                feature_id="sanctuary", animation="ward",
                description=f"{attacker.template.name} fails the Sanctuary save and loses the {weapon.name} attack.",
            )
        advantage, disadvantage = attack_roll_condition_sources(attacker, defender, distance_ft, defender_id)
        mode = resolve_attack_roll_mode(
            weapon, distance_ft,
            advantage_sources=advantage_sources + advantage + bloodied_fury_advantage(attacker, attack),
            other_disadvantage_sources=other_disadvantage_sources + disadvantage,
        )
        attack_roll = roll_d20(dice, attack.attack_bonus, mode)
        blessing = bless_bonus(attacker, dice)
        if blessing:
            attack_roll.notation += "+1d4"; attack_roll.rolls.append(blessing); attack_roll.total += blessing
        end_sanctuary(attacker)
        extend_rage_from_attack(attacker, round_number)
        if spend_action:
            spend(attacker, "action")
        natural = attack_roll.selected_roll or 0
        hit = natural != 1 and (natural == 20 or attack_roll.total >= defender.template.armor_class)
        critical = bool(hit and (natural == 20 or (close_hit_is_automatic_critical(defender) and distance_ft <= 5)))
        hp_before = defender.current_hp
        damage_roll = None; damage_components = []; damage_outcome = None; applied: list[str] = []
        concentration_roll = None; concentration_ok = None; concentration_dc = None
        if hit:
            active_key = turn_key or f"{round_number}:{attacker_id}"
            damage_roll, rolled = resolve_weapon_damage(attacker, attack, dice, critical, mode, active_key, bonus_damage=bonus_damage)
            applied_total, damage_components = apply_damage_defenses(defender, rolled)
            damage_roll.total = applied_total
            damage_outcome = apply_damage(defender, applied_total, critical=critical)
            end_rage_if_incapacitated(defender)
            applied = apply_hit_conditions(attack, defender, attacker_id)
            concentration_roll, concentration_ok, concentration_dc = concentration_after_damage(
                defender_id, defender, encounter_setup, applied_total, dice,
            )
        outcome = "CRITICAL HIT" if critical else "HIT" if hit else "MISS"
        description = f"{attacker.template.name}: {outcome} with {weapon.name}."
        if damage_outcome == "relentless_endurance": description += f" {defender.template.name} uses Relentless Endurance and remains at 1 HP."
        for condition, text in (("prone", "is knocked Prone"), ("grappled", "is Grappled"), ("restrained", "is Restrained while Grappled"), ("poisoned", "is Poisoned")):
            if condition in applied: description += f" {defender.template.name} {text}."
        if concentration_ok is False: description += f" {defender.template.name} loses Concentration."
        return BattleEvent(
            sequence=sequence, round_number=round_number, event_type="attack",
            actor_id=attacker_id, actor_name=attacker.template.name,
            target_id=defender_id, target_name=defender.template.name,
            attack_roll=attack_roll, damage_roll=damage_roll, damage_components=damage_components,
            concentration_roll=concentration_roll, concentration_dc=concentration_dc,
            concentration_succeeded=concentration_ok, applied_condition_ids=applied,
            hit=hit, critical=critical, hp_before=hp_before, hp_after=defender.current_hp,
            death_save_successes=defender.death_save_successes, death_save_failures=defender.death_save_failures,
            is_stable=defender.is_stable, is_dead=defender.is_dead,
            weapon_id=weapon.id, projectile=weapon.projectile, feature_id=feature_id,
            animation=weapon.animation, description=description,
        )
    except Exception as exc:
        logger.exception("Attack failed: %s -> %s.", attacker.template.name, defender.template.name)
        raise RuntimeError("Attack resolution failed.") from exc
