from __future__ import annotations

import logging

from app.combat.damage import resolve_weapon_damage
from app.combat.dice import DiceProvider
from app.combat.masteries import (
    apply_weapon_mastery_on_hit,
    consume_attack_roll_effects,
    resolve_attack_roll_effect_sources,
)
from app.combat.range import resolve_attack_roll_mode
from app.combat.rolls import roll_d20
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
    spend_action: bool = True,
    include_positive_ability_damage_modifier: bool = True,
) -> BattleEvent:
    try:
        if spend_action and not attacker.action_available:
            raise ValueError("Action is not available for an attack.")

        weapon = attack.weapon
        target_id = defender.template.id
        advantage_sources, disadvantage_sources = resolve_attack_roll_effect_sources(
            attacker, target_id
        )
        mode = resolve_attack_roll_mode(
            weapon,
            distance_ft,
            advantage_sources=advantage_sources,
            other_disadvantage_sources=disadvantage_sources,
        )
        attack_roll = roll_d20(dice, attack.attack_bonus, mode)
        consume_attack_roll_effects(attacker, target_id)
        if spend_action:
            attacker.action_available = False
        natural = attack_roll.selected_roll or 0
        critical = natural == 20
        hit = natural != 1 and (
            critical or attack_roll.total >= defender.template.armor_class
        )
        hp_before = defender.current_hp
        damage_roll = None
        damage_components = []
        feature_id = None

        if hit:
            damage_roll, damage_components = resolve_weapon_damage(
                attacker,
                attack,
                dice,
                critical,
                mode,
                include_positive_ability_damage_modifier,
            )
            defender.current_hp = max(0, defender.current_hp - damage_roll.total)
            defender.is_alive = defender.current_hp > 0
            if defender.is_alive:
                feature_id = apply_weapon_mastery_on_hit(
                    attacker,
                    defender,
                    weapon,
                    damage_dealt=damage_roll.total > 0,
                )

        outcome = "CRITICAL HIT" if critical else ("HIT" if hit else "MISS")
        description = f"{attacker.template.name}: {outcome} with {weapon.name}."
        if feature_id == "sap":
            description += " Sap hinders the target's next attack roll."
        elif feature_id == "vex":
            description += " Vex grants Advantage on the next attack against this target."

        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="attack",
            actor_id=attacker.template.id,
            actor_name=attacker.template.name,
            target_id=target_id,
            target_name=defender.template.name,
            attack_roll=attack_roll,
            damage_roll=damage_roll,
            damage_components=damage_components,
            hit=hit,
            critical=critical,
            hp_before=hp_before,
            hp_after=defender.current_hp,
            weapon_id=weapon.id,
            projectile=weapon.projectile,
            feature_id=feature_id,
            animation=weapon.animation,
            description=description,
        )
    except Exception as exc:
        logger.exception(
            "Attack failed: %s -> %s.", attacker.template.name, defender.template.name
        )
        raise RuntimeError("Attack resolution failed.") from exc
