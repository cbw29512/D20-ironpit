from __future__ import annotations

from app.content.armor_class_rules import compile_armored_base_ac
from app.content.canonical_hero_policy import canonical_template_id
from app.content.equipment import build_shortbow
from app.content.hero_progressions import HERO_BY_CLASS
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
        attack_ability="strength",
        attack_ability_modifier=3,
    )


def _shortbow_attack() -> WeaponAttack:
    return WeaponAttack(
        id="karnok-shortbow",
        weapon=build_shortbow(),
        attack_bonus=3,
        damage_bonus=1,
        attack_ability="dexterity",
        attack_ability_modifier=1,
    )


def build_karnok_stoneward() -> CombatantTemplate:
    """Level-1 canonical Fighter derived from the 2024 Basic Rules."""
    level = 1
    hero = HERO_BY_CLASS["fighter"]
    fighting_style = "Defense"
    armor_class = compile_armored_base_ac(16, fighting_style, "heavy")
    return CombatantTemplate(
        id=canonical_template_id("fighter", level),
        name=hero.hero_name,
        archetype=hero.class_name,
        level=level,
        kind="character",
        armor_class=armor_class,
        max_hp=12,
        speed_ft=30,
        initiative_bonus=1,
        weapon_attack=_greatsword_attack(),
        alternate_weapon_attacks=[_shortbow_attack()],
        saving_throw_bonuses={
            "strength": 5, "dexterity": 1, "constitution": 4,
            "intelligence": 0, "wisdom": 0, "charisma": 0,
        },
        skill_bonuses={"athletics": 5, "acrobatics": 1},
        combat_traits=[
            CombatTrait.SAVAGE_ATTACKER,
            CombatTrait.ADRENALINE_RUSH,
            CombatTrait.RELENTLESS_ENDURANCE,
        ],
        fighting_style=fighting_style,
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
