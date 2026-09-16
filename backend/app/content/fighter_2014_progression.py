from __future__ import annotations

import logging

from app.content.equipment import build_greatsword, build_shortbow
from app.content.fighter_2014_levels import FIGHTER_2014_LEVELS
from app.content.hero_progressions import HERO_BY_CLASS
from app.domain.character_builds import AbilityScores
from app.domain.models import CombatantTemplate, ResourceDefinition, VisualLoadout, WeaponAttack
from app.domain.traits import CombatTrait

logger = logging.getLogger(__name__)


def _modifier(score: int) -> int:
    return (score - 10) // 2


def _attack(weapon_id: str, level: int) -> WeaponAttack:
    row = FIGHTER_2014_LEVELS[level]
    if weapon_id == "greatsword":
        weapon = build_greatsword().model_copy(update={"mastery_property": None})
        modifier = _modifier(row.strength)
        bonus = row.proficiency_bonus + modifier
        attack_id = "karnok-2014-greatsword"
    elif weapon_id == "shortbow":
        weapon = build_shortbow().model_copy(update={"mastery_property": None})
        modifier = _modifier(row.dexterity)
        archery = 2 if "Archery" in row.fighting_styles else 0
        bonus = row.proficiency_bonus + modifier + archery
        attack_id = "karnok-2014-shortbow"
    else:
        raise ValueError(f"Unsupported 2014 Karnok weapon: {weapon_id}.")
    return WeaponAttack(
        id=attack_id,
        weapon=weapon,
        attack_bonus=bonus,
        damage_bonus=modifier,
        attack_ability="strength" if weapon_id == "greatsword" else "dexterity",
        attack_ability_modifier=modifier,
    )


def _resources(level: int) -> list[ResourceDefinition]:
    row = FIGHTER_2014_LEVELS[level]
    values = [
        ("second-wind", "Second Wind", row.second_wind_uses),
        ("action-surge", "Action Surge", row.action_surge_uses),
        ("indomitable", "Indomitable", row.indomitable_uses),
        ("relentless-endurance", "Relentless Endurance", 1),
    ]
    return [ResourceDefinition(id=key, name=name, max_uses=uses) for key, name, uses in values if uses]


def build_karnok_stoneward_2014_level(level: int) -> CombatantTemplate:
    """Build the canonical 2014 Half-Orc Champion Fighter for levels 1-10."""
    try:
        if level not in FIGHTER_2014_LEVELS:
            raise ValueError("2014 Karnok Fighter level must be between 1 and 10.")
        row = FIGHTER_2014_LEVELS[level]
        hero = HERO_BY_CLASS["fighter"]
        strength_mod = _modifier(row.strength)
        dexterity_mod = _modifier(row.dexterity)
        constitution_mod = _modifier(row.constitution)
        initiative_bonus = dexterity_mod + row.remarkable_athlete_bonus
        attacks = [_attack("greatsword", level), _attack("shortbow", level)]
        attack_action = None
        if row.attack_count > 1:
            ids = [attack.id for attack in attacks]
            attack_action = {
                "id": "extra-attack",
                "name": "Extra Attack",
                "is_attack_action": True,
                "slots": [{"attack_ids": ids} for _ in range(row.attack_count)],
            }
        return CombatantTemplate(
            id=f"karnok-stoneward-2014-l{level}",
            name=hero.hero_name,
            archetype=hero.class_name,
            level=level,
            kind="character",
            ruleset="2014",
            ability_scores=AbilityScores(
                strength=row.strength,
                dexterity=row.dexterity,
                constitution=row.constitution,
                intelligence=10,
                wisdom=12,
                charisma=8,
            ),
            armor_class=17,
            max_hp=row.max_hp,
            speed_ft=30,
            initiative_bonus=initiative_bonus,
            progression_features={"critical_hit_minimum": row.critical_hit_minimum},
            weapon_attack=attacks[0],
            alternate_weapon_attacks=[attacks[1]],
            attack_action=attack_action,
            saving_throw_bonuses={
                "strength": row.proficiency_bonus + strength_mod,
                "dexterity": dexterity_mod,
                "constitution": row.proficiency_bonus + constitution_mod,
                "intelligence": 0,
                "wisdom": 1,
                "charisma": -1,
            },
            skill_bonuses={
                "athletics": row.proficiency_bonus + strength_mod,
                "acrobatics": dexterity_mod + row.remarkable_athlete_bonus,
            },
            combat_traits=[CombatTrait.SAVAGE_ATTACKS, CombatTrait.RELENTLESS_ENDURANCE],
            source_trait_names=["Savage Attacks", "Relentless Endurance"],
            fighting_style=row.fighting_styles[0],
            fighting_styles=list(row.fighting_styles),
            weapon_masteries=[],
            visual=VisualLoadout(armor="chain-mail", main_hand="greatsword", body_style="humanoid"),
            resources=_resources(level),
            source=row.source,
        )
    except Exception:
        logger.exception("Failed to build 2014 Karnok Stoneward level %s.", level)
        raise
