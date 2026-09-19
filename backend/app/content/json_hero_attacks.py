from __future__ import annotations

import logging

from app.content.attack_bonus_rules import compile_weapon_attack_bonus
from app.content.json_hero_derived import ability_modifier
from app.content.weapon_catalog import build_weapon
from app.domain.combatant_source import HeroBuildSource
from app.domain.models import WeaponAttackKind

LOGGER = logging.getLogger(__name__)


def _catalog_weapon(weapon_id: str):
    try:
        return build_weapon(weapon_id)
    except ValueError:
        return None


def _attack_kind(value) -> WeaponAttackKind:
    try:
        if isinstance(value, WeaponAttackKind):
            return value
        return WeaponAttackKind(str(value))
    except Exception:
        LOGGER.exception("Unable to type weapon attack kind value=%r", value)
        raise


def compile_hero_attacks(
    *,
    edition: str,
    abilities: dict[str, int],
    proficiency: int,
    capabilities: list[str],
    fighting_styles: list[str],
    unarmed_dice: object,
    build: HeroBuildSource,
) -> list[dict[str, object]]:
    try:
        gwf = "great-weapon-fighting" in capabilities
        attacks: list[dict[str, object]] = []
        for attack in build.attacks:
            weapon = _catalog_weapon(attack.weapon_id)
            modifier = ability_modifier(int(abilities[attack.ability]))
            kind = _attack_kind(weapon.attack_kind if weapon is not None else attack.attack_kind)
            bonus = compile_weapon_attack_bonus(proficiency + modifier, fighting_styles, kind)
            melee = kind is WeaponAttackKind.MELEE
            if weapon is None:
                dice_size = (
                    int(unarmed_dice)
                    if unarmed_dice and attack.weapon_id == "unarmed-strike"
                    else attack.dice_size
                )
                two_handed = attack.two_handed
                attacks.append({
                    "id": attack.id, "name": attack.name, "weapon_id": attack.weapon_id,
                    "attack_kind": attack.attack_kind, "attack_bonus": bonus,
                    "damage": {"count": attack.dice_count, "size": dice_size, "bonus": modifier},
                    "damage_type": attack.damage_type, "animation": attack.animation,
                    "reach_ft": attack.reach_ft, "normal_range_ft": attack.normal_range_ft,
                    "long_range_ft": attack.long_range_ft, "mastery_property": attack.mastery_property,
                    "heavy": attack.heavy, "two_handed": two_handed,
                    "attack_ability": attack.ability, "attack_ability_modifier": modifier,
                    "rage_eligible": "rage" in capabilities,
                    "sneak_attack_eligible": "sneak-attack" in capabilities,
                    "damage_die_minimum": 3 if gwf and melee and two_handed else None,
                })
                continue
            attacks.append({
                "id": attack.id, "name": weapon.name, "weapon_id": weapon.id,
                "attack_kind": weapon.attack_kind, "attack_bonus": bonus,
                "damage": {"count": weapon.dice_count, "size": weapon.dice_size, "bonus": modifier},
                "damage_type": weapon.damage_type, "animation": weapon.animation,
                "reach_ft": weapon.reach_ft, "normal_range_ft": weapon.normal_range_ft,
                "long_range_ft": weapon.long_range_ft, "projectile": weapon.projectile,
                "mastery_property": None if edition == "2014" else weapon.mastery_property,
                "heavy": weapon.heavy, "two_handed": weapon.two_handed,
                "light": weapon.light, "finesse": weapon.finesse, "versatile": weapon.versatile,
                "attack_ability": attack.ability, "attack_ability_modifier": modifier,
                "rage_eligible": "rage" in capabilities,
                "sneak_attack_eligible": "sneak-attack" in capabilities,
                "damage_die_minimum": 3 if gwf and melee and weapon.two_handed else None,
            })
        return attacks
    except Exception:
        LOGGER.exception("Failed to compile hero attacks class=%s edition=%s", build.class_id, edition)
        raise
