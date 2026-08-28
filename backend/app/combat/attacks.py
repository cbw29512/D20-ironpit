from __future__ import annotations

import logging

from app.combat.attack_damage import resolve_attack_damage
from app.combat.attack_rolls import resolve_attack_mode_and_cover
from app.combat.barbarian import extend_rage_by_attack
from app.combat.card_effects import attack_effect_change, hidden_effect_change, mastery_effect_change
from app.combat.conditions import is_automatic_critical_hit, is_incapacitated
from app.combat.dice import DiceProvider
from app.combat.masteries import apply_weapon_mastery_on_hit, consume_attack_roll_effects
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
        extend_rage_by_attack(attacker)
        was_hidden = break_hidden(attacker)
        consumed = consume_attack_roll_effects(attacker, target_id)
        effect_changes = [attack_effect_change(attacker, effect, "remove") for effect in consumed]
        if was_hidden:
            effect_changes.append(hidden_effect_change(attacker, "remove"))
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
        damage_applied = None
        feature_id = None
        sneak_attack_applied = False
        mitigation_note = ""

        if hit:
            damage = resolve_attack_damage(
                attacker,
                defender,
                attack,
                dice,
                critical,
                mode,
                include_positive_ability_damage_modifier,
            )
            damage_roll = damage.roll
            damage_components = damage.components
            damage_applied = damage.applied
            sneak_attack_applied = damage.sneak_attack_applied
            if damage.immune:
                mitigation_note = f" Immunity reduces applied damage to {damage.applied}."
            elif damage.resisted:
                mitigation_note = f" Resistance reduces applied damage to {damage.applied}."
            elif damage.vulnerable:
                mitigation_note = f" Vulnerability increases applied damage to {damage.applied}."
            if defender.is_alive:
                feature_id = apply_weapon_mastery_on_hit(
                    attacker, defender, weapon, damage_dealt=damage.applied > 0
                )
                change = mastery_effect_change(feature_id, attacker, defender)
                if change is not None:
                    effect_changes.append(change)

        outcome = "CRITICAL HIT" if critical else ("HIT" if hit else "MISS")
        description = f"{attacker.template.name}: {outcome} with {weapon.name}."
        if cover_bonus:
            description += f" Cover adds +{cover_bonus} AC."
        if sneak_attack_applied:
            description += " Sneak Attack adds precision damage."
        description += mitigation_note
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
            damage_applied=damage_applied,
            effect_changes=effect_changes,
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
        logger.exception("Attack failed: %s -> %s.", attacker.template.name, defender.template.name)
        raise RuntimeError("Attack resolution failed.") from exc
