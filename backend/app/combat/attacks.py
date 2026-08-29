from __future__ import annotations

import logging

from app.combat.barbarian import end_rage_if_incapacitated, extend_rage_from_attack
from app.combat.bloodied import bloodied_fury_advantage
from app.combat.conditions import apply_hit_conditions, attack_roll_condition_sources
from app.combat.damage import BonusDamageSpec, resolve_weapon_damage
from app.combat.damage_defenses import apply_damage_defenses
from app.combat.dice import DiceProvider
from app.combat.range import resolve_attack_roll_mode
from app.combat.rolls import roll_d20
from app.combat.zero_hp import apply_damage
from app.domain.models import BattleEvent, CombatantState, WeaponAttack

logger = logging.getLogger(__name__)


def resolve_attack(
    sequence: int,
    round_number: int,
    attacker: CombatantState,
    defender: CombatantState,
    attack: WeaponAttack,
    distance_ft: int,
    dice: DiceProvider,
    actor_event_id: str | None = None,
    target_event_id: str | None = None,
    spend_action: bool = True,
    advantage_sources: int = 0,
    other_disadvantage_sources: int = 0,
    feature_id: str | None = None,
    turn_key: str | None = None,
    bonus_damage: BonusDamageSpec | None = None,
) -> BattleEvent:
    try:
        if spend_action and not attacker.action_available:
            raise ValueError("Action is not available for an attack.")

        weapon = attack.weapon
        condition_advantage, condition_disadvantage = attack_roll_condition_sources(
            attacker,
            defender,
            distance_ft,
        )
        mode = resolve_attack_roll_mode(
            weapon,
            distance_ft,
            advantage_sources=(
                advantage_sources
                + condition_advantage
                + bloodied_fury_advantage(attacker, attack)
            ),
            other_disadvantage_sources=other_disadvantage_sources + condition_disadvantage,
        )
        attack_roll = roll_d20(dice, attack.attack_bonus, mode)
        extend_rage_from_attack(attacker, round_number)
        if spend_action:
            attacker.action_available = False
        natural = attack_roll.selected_roll or 0
        natural_critical = natural == 20
        hit = natural != 1 and (natural_critical or attack_roll.total >= defender.template.armor_class)
        critical = bool(hit and (natural_critical or (defender.is_unconscious and distance_ft <= 5)))
        hp_before = defender.current_hp
        damage_roll = None
        damage_components = []
        damage_outcome = None
        applied_conditions: list[str] = []

        if hit:
            active_turn_key = turn_key or f"{round_number}:{actor_event_id or attacker.template.id}"
            damage_roll, rolled_components = resolve_weapon_damage(
                attacker,
                attack,
                dice,
                critical,
                mode,
                active_turn_key,
                bonus_damage=bonus_damage,
            )
            applied_total, damage_components = apply_damage_defenses(
                defender,
                rolled_components,
            )
            damage_outcome = apply_damage(defender, applied_total, critical=critical)
            end_rage_if_incapacitated(defender)
            applied_conditions = apply_hit_conditions(attack, defender)

        outcome = "CRITICAL HIT" if critical else ("HIT" if hit else "MISS")
        description = f"{attacker.template.name}: {outcome} with {weapon.name}."
        if damage_outcome == "relentless_endurance":
            description += f" {defender.template.name} uses Relentless Endurance and remains at 1 HP."
        if "prone" in applied_conditions:
            description += f" {defender.template.name} is knocked Prone."
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="attack",
            actor_id=actor_event_id or attacker.template.id,
            actor_name=attacker.template.name,
            target_id=target_event_id or defender.template.id,
            target_name=defender.template.name,
            attack_roll=attack_roll,
            damage_roll=damage_roll,
            damage_components=damage_components,
            applied_condition_ids=applied_conditions,
            hit=hit,
            critical=critical,
            hp_before=hp_before,
            hp_after=defender.current_hp,
            death_save_successes=defender.death_save_successes,
            death_save_failures=defender.death_save_failures,
            is_stable=defender.is_stable,
            is_dead=defender.is_dead,
            weapon_id=weapon.id,
            projectile=weapon.projectile,
            feature_id=feature_id,
            animation=weapon.animation,
            description=description,
        )
    except Exception as exc:
        logger.exception("Attack failed: %s -> %s.", attacker.template.name, defender.template.name)
        raise RuntimeError("Attack resolution failed.") from exc
