from __future__ import annotations

import logging

from app.combat.attack_rolls import resolve_attack_mode_and_cover
from app.combat.conditions import is_automatic_critical_hit, is_incapacitated
from app.combat.damage import resolve_weapon_damage
from app.combat.dice import DiceProvider
from app.combat.masteries import apply_weapon_mastery_on_hit, consume_attack_roll_effects
from app.combat.rogue import resolve_sneak_attack_component
from app.combat.rolls import roll_d20
from app.combat.stealth import break_hidden
from app.domain.models import BattleEvent, BattlefieldState, CombatantState, WeaponAttack

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
    battlefield: BattlefieldState | None = None,
) -> BattleEvent:
    try:
        if is_incapacitated(attacker):
            raise ValueError("Incapacitated creatures cannot make attacks.")
        if spend_action and not attacker.action_available:
            raise ValueError("Action is not available for an attack.")

        weapon = attack.weapon
        target_id = defender.template.id
        mode, cover_bonus = resolve_attack_mode_and_cover(
            attacker, defender, weapon, distance_ft, battlefield
        )
        attack_roll = roll_d20(dice, attack.attack_bonus, mode)
        break_hidden(attacker)
        consume_attack_roll_effects(attacker, target_id)
        if spend_action:
            attacker.action_available = False
        natural = attack_roll.selected_roll or 0
        critical = natural == 20
        effective_ac = defender.template.armor_class + cover_bonus
        hit = natural != 1 and (critical or attack_roll.total >= effective_ac)
        critical = critical or (hit and is_automatic_critical_hit(defender, distance_ft))
        hp_before = defender.current_hp
        damage_roll = None
        damage_components = []
        feature_id = None
        sneak_attack_applied = False

        if hit:
            damage_roll, damage_components = resolve_weapon_damage(
                attacker,
                attack,
                dice,
                critical,
                mode,
                include_positive_ability_damage_modifier,
            )
            sneak_component = resolve_sneak_attack_component(
                attacker, attack, dice, critical, mode
            )
            if sneak_component is not None:
                damage_components.append(sneak_component)
                damage_roll.notation += f" + {sneak_component.notation}"
                damage_roll.rolls.extend(sneak_component.rolls)
                damage_roll.total += sneak_component.total
                sneak_attack_applied = True

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
        if cover_bonus:
            description += f" Cover adds +{cover_bonus} AC."
        if sneak_attack_applied:
            description += " Sneak Attack adds precision damage."
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
