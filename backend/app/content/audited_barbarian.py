from __future__ import annotations

from app.content.level_resources import (
    barbarian_rage_damage_bonus,
    barbarian_rage_uses,
    orc_adrenaline_rush_uses,
)
from app.domain.models import (
    CombatantTemplate,
    DamageType,
    ResourceDefinition,
    VisualLoadout,
    Weapon,
    WeaponAttack,
    WeaponAttackKind,
)
from app.domain.traits import CombatTrait


def _greataxe_attack() -> WeaponAttack:
    return WeaponAttack(
        id="rokhan-greataxe",
        weapon=Weapon(
            id="greataxe",
            name="Greataxe",
            attack_kind=WeaponAttackKind.MELEE,
            dice_count=1,
            dice_size=12,
            damage_type=DamageType.SLASHING,
            animation="heavy-slash",
            reach_ft=5,
            mastery_property="Cleave",
        ),
        attack_bonus=5,
        damage_bonus=3,
        rage_eligible=True,
    )


def _handaxe_throw() -> WeaponAttack:
    return WeaponAttack(
        id="rokhan-handaxe-thrown",
        weapon=Weapon(
            id="handaxe",
            name="Handaxe",
            attack_kind=WeaponAttackKind.RANGED,
            dice_count=1,
            dice_size=6,
            damage_type=DamageType.SLASHING,
            animation="projectile",
            normal_range_ft=20,
            long_range_ft=60,
            projectile="handaxe",
            mastery_property="Vex",
        ),
        attack_bonus=5,
        damage_bonus=3,
        rage_eligible=True,
    )


def build_rokhan_stonefury() -> CombatantTemplate:
    """Level-1 Orc Soldier Barbarian derived from the 2024 Basic Rules."""
    level = 1
    return CombatantTemplate(
        id="rokhan-stonefury-l1",
        name="Rokhan Stonefury",
        archetype="Barbarian",
        level=level,
        kind="character",
        armor_class=13,
        max_hp=14,
        speed_ft=30,
        initiative_bonus=1,
        weapon_attack=_greataxe_attack(),
        alternate_weapon_attacks=[_handaxe_throw()],
        saving_throw_bonuses={
            "strength": 5, "dexterity": 1, "constitution": 4,
            "intelligence": -1, "wisdom": 1, "charisma": 0,
        },
        skill_bonuses={"athletics": 5, "acrobatics": 1},
        combat_traits=[
            CombatTrait.SAVAGE_ATTACKER,
            CombatTrait.ADRENALINE_RUSH,
            CombatTrait.RELENTLESS_ENDURANCE,
        ],
        weapon_masteries=["flail", "pike"],
        wearing_heavy_armor=False,
        rage_damage_bonus=barbarian_rage_damage_bonus(level),
        visual=VisualLoadout(
            armor="unarmored",
            main_hand="greataxe",
            body_style="humanoid",
        ),
        resources=[
            ResourceDefinition(id="rage", name="Rage", max_uses=barbarian_rage_uses(level)),
            ResourceDefinition(
                id="adrenaline-rush",
                name="Adrenaline Rush",
                max_uses=orc_adrenaline_rush_uses(level),
            ),
            ResourceDefinition(id="relentless-endurance", name="Relentless Endurance", max_uses=1),
        ],
        source="D&D Beyond Basic Rules 2024: Barbarian, Orc, Soldier, Savage Attacker, Equipment",
    )
