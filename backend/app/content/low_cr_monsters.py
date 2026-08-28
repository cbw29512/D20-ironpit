from __future__ import annotations

import logging

from app.domain.models import (
    AbilityKind,
    CombatantTemplate,
    DamageType,
    VisualLoadout,
    Weapon,
    WeaponAttack,
    WeaponAttackKind,
    WeaponProperty,
)

logger = logging.getLogger(__name__)


def _weapon(
    id_: str,
    name: str,
    kind: WeaponAttackKind,
    dice_size: int,
    *,
    normal_range: int | None = None,
    long_range: int | None = None,
    projectile: str | None = None,
) -> Weapon:
    return Weapon(
        id=id_,
        name=name,
        attack_kind=kind,
        dice_count=1,
        dice_size=dice_size,
        damage_type=DamageType.PIERCING if name != "Scimitar" else DamageType.SLASHING,
        animation="projectile" if kind is WeaponAttackKind.RANGED else "slash",
        reach_ft=5,
        normal_range_ft=normal_range,
        long_range_ft=long_range,
        projectile=projectile,
        properties=[WeaponProperty.THROWN] if name == "Spear" and kind is WeaponAttackKind.RANGED else [],
    )


def build_bandit() -> CombatantTemplate:
    try:
        scimitar = _weapon("scimitar", "Scimitar", WeaponAttackKind.MELEE, 6)
        crossbow = _weapon(
            "light-crossbow", "Light Crossbow", WeaponAttackKind.RANGED, 8,
            normal_range=80, long_range=320, projectile="bolt",
        )
        return CombatantTemplate(
            id="srd-bandit", name="Bandit", archetype="Bandit", challenge_rating="1/8",
            kind="monster", armor_class=12, max_hp=11, speed_ft=30, initiative_bonus=1,
            proficiency_bonus=2,
            ability_modifiers={
                AbilityKind.STRENGTH: 0, AbilityKind.DEXTERITY: 1,
                AbilityKind.CONSTITUTION: 1, AbilityKind.INTELLIGENCE: 0,
                AbilityKind.WISDOM: 0, AbilityKind.CHARISMA: 0,
            },
            weapon_attack=WeaponAttack(
                id="bandit-scimitar", weapon=scimitar, attack_bonus=3,
                ability_damage_modifier=1,
            ),
            alternate_weapon_attacks=[WeaponAttack(
                id="bandit-light-crossbow", weapon=crossbow, attack_bonus=3,
                ability_damage_modifier=1,
            )],
            passive_perception=10,
            visual=VisualLoadout(
                armor="leather", main_hand="scimitar", off_hand=None, body_style="humanoid"
            ),
            source="D&D Beyond Basic Rules (2024): Creature Stat Blocks — Bandit",
        )
    except Exception as exc:
        logger.exception("Failed to build Bandit stat block.")
        raise RuntimeError("Bandit content could not be created.") from exc


def build_guard() -> CombatantTemplate:
    try:
        melee = _weapon("spear", "Spear", WeaponAttackKind.MELEE, 6)
        thrown = _weapon(
            "spear", "Spear", WeaponAttackKind.RANGED, 6,
            normal_range=20, long_range=60, projectile="spear",
        )
        return CombatantTemplate(
            id="srd-guard", name="Guard", archetype="Guard", challenge_rating="1/8",
            kind="monster", armor_class=16, max_hp=11, speed_ft=30, initiative_bonus=1,
            proficiency_bonus=2,
            ability_modifiers={
                AbilityKind.STRENGTH: 1, AbilityKind.DEXTERITY: 1,
                AbilityKind.CONSTITUTION: 1, AbilityKind.INTELLIGENCE: 0,
                AbilityKind.WISDOM: 0, AbilityKind.CHARISMA: 0,
            },
            weapon_attack=WeaponAttack(
                id="guard-spear-melee", weapon=melee, attack_bonus=3,
                ability_damage_modifier=1,
            ),
            alternate_weapon_attacks=[WeaponAttack(
                id="guard-spear-thrown", weapon=thrown, attack_bonus=3,
                ability_damage_modifier=1,
            )],
            skill_bonuses={"perception": 2}, passive_perception=12,
            visual=VisualLoadout(
                armor="chain-shirt", main_hand="spear", off_hand="shield", body_style="humanoid"
            ),
            source="D&D Beyond Basic Rules (2024): Creature Stat Blocks — Guard",
        )
    except Exception as exc:
        logger.exception("Failed to build Guard stat block.")
        raise RuntimeError("Guard content could not be created.") from exc
