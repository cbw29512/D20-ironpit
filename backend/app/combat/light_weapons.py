from __future__ import annotations

import logging

from app.combat.attacks import resolve_attack
from app.combat.dice import DiceProvider
from app.combat.range import resolve_attack_roll_mode
from app.domain.models import (
    BattleEvent,
    BattlefieldState,
    CombatantState,
    WeaponAttack,
    WeaponProperty,
)

logger = logging.getLogger(__name__)
LIGHT_RULE = "light"
NICK_MASTERY = "nick"
TWO_WEAPON_FIGHTING = "two-weapon-fighting"


def _select_light_extra_attack(
    attacker: CombatantState,
    triggering_attack: WeaponAttack,
    distance_ft: int,
) -> WeaponAttack | None:
    try:
        if WeaponProperty.LIGHT not in triggering_attack.weapon.properties:
            return None
        profiles = [
            attacker.template.weapon_attack,
            *attacker.template.alternate_weapon_attacks,
        ]
        for attack in profiles:
            if attack.id == triggering_attack.id:
                continue
            if WeaponProperty.LIGHT not in attack.weapon.properties:
                continue
            try:
                resolve_attack_roll_mode(attack.weapon, distance_ft)
                return attack
            except ValueError:
                continue
        return None
    except Exception as exc:
        logger.exception(
            "Failed to select Light extra attack for %s.", attacker.template.name
        )
        raise RuntimeError("Light extra attack selection failed.") from exc


def _uses_nick(attacker: CombatantState, attack: WeaponAttack) -> bool:
    try:
        return bool(
            attack.weapon.mastery_property == NICK_MASTERY
            and attack.weapon.id in attacker.template.weapon_masteries
        )
    except Exception as exc:
        logger.exception("Failed to resolve Nick eligibility for %s.", attacker.template.name)
        raise RuntimeError("Nick eligibility could not be resolved.") from exc


def resolve_light_extra_attack(
    sequence: int,
    round_number: int,
    attacker: CombatantState,
    defender: CombatantState,
    triggering_attack: WeaponAttack,
    distance_ft: int,
    dice: DiceProvider,
    battlefield: BattlefieldState | None = None,
) -> BattleEvent | None:
    """Resolve the one-per-turn extra attack granted by the Light property."""
    try:
        if attacker.light_extra_attack_used or not defender.is_alive:
            return None
        extra_attack = _select_light_extra_attack(
            attacker, triggering_attack, distance_ft
        )
        if extra_attack is None:
            return None

        uses_nick = _uses_nick(attacker, extra_attack)
        if not uses_nick and not attacker.bonus_action_available:
            return None

        include_positive_ability = (
            attacker.template.fighting_style == TWO_WEAPON_FIGHTING
        )
        event = resolve_attack(
            sequence,
            round_number,
            attacker,
            defender,
            extra_attack,
            distance_ft,
            dice,
            spend_action=False,
            include_positive_ability_damage_modifier=include_positive_ability,
            battlefield=battlefield,
        )
        attacker.light_extra_attack_used = True
        if uses_nick:
            event.feature_id = NICK_MASTERY
            event.description = f"Nick Light extra attack — {event.description}"
        else:
            attacker.bonus_action_available = False
            if event.feature_id is None:
                event.feature_id = LIGHT_RULE
            event.description = f"Light Bonus Action attack — {event.description}"
        return event
    except Exception as exc:
        logger.exception("Light extra attack failed for %s.", attacker.template.name)
        raise RuntimeError("Light extra attack could not be resolved.") from exc
