from __future__ import annotations

from app.content.equipment import build_shortbow
from app.content.level_resources import fighter_second_wind_uses, orc_adrenaline_rush_uses
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


def _greatsword_attack() -> WeaponAttack:
    return WeaponAttack(
        id="karnok-greatsword",
        weapon=Weapon(
            id="greatsword",
            name="Greatsword",
            attack_kind=WeaponAttackKind.MELEE,
            dice_count=2,
            dice_size=6,
            damage_type=DamageType.SLASHING,
            animation="heavy-slash",
            reach_ft=5,
            mastery_property="Graze",
        ),
        attack_bonus=5,
        damage_bonus=3,
    )


def _shortbow_attack() -> WeaponAttack:
    return WeaponAttack(
        id="karnok-shortbow",
        weapon=build_shortbow(),
        attack_bonus=3,
        damage_bonus=1,
    )


def build_karnok_stoneward() -> CombatantTemplate:
    """Level-1 Orc Soldier Fighter derived from the 2024 Basic Rules."""
    level = 1
    return CombatantTemplate(
        id="karnok-stoneward-l1",
        name="Karnok Stoneward",
        archetype="Fighter",
        level=level,
        kind="character",
        armor_class=17,
        max_hp=12,
        speed_ft=30,
        initiative_bonus=1,
        weapon_attack=_greatsword_attack(),
        alternate_weapon_attacks=[_shortbow_attack()],
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
        fighting_style="Defense",
        weapon_masteries=["flail", "javelin", "spear"],
        visual=VisualLoadout(
            armor="chain-mail",
            main_hand="greatsword",
            body_style="humanoid",
        ),
        resources=[
            ResourceDefinition(
                id="second-wind",
                name="Second Wind",
                max_uses=fighter_second_wind_uses(level),
            ),
            ResourceDefinition(
                id="adrenaline-rush",
                name="Adrenaline Rush",
                max_uses=orc_adrenaline_rush_uses(level),
            ),
            ResourceDefinition(id="relentless-endurance", name="Relentless Endurance", max_uses=1),
        ],
        source="D&D Beyond Basic Rules 2024: Fighter, Orc, Soldier, Savage Attacker, Equipment",
    )
