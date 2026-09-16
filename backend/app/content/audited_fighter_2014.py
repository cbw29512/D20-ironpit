from __future__ import annotations

from dataclasses import dataclass

from app.content.equipment import build_greatsword, build_shortbow
from app.domain.character_builds import AbilityScores
from app.domain.models import CombatantTemplate, ResourceDefinition, VisualLoadout, WeaponAttack


@dataclass(frozen=True)
class Fighter2014Level:
    level: int
    proficiency_bonus: int
    max_hp: int
    strength: int
    dexterity: int
    constitution: int
    attack_count: int
    critical_minimum: int
    second_wind_uses: int
    action_surge_uses: int
    indomitable_uses: int
    remarkable_athlete: bool = False
    second_fighting_style: bool = False


LEVELS: dict[int, Fighter2014Level] = {
    1: Fighter2014Level(1, 2, 12, 16, 14, 15, 1, 20, 1, 0, 0),
    2: Fighter2014Level(2, 2, 20, 16, 14, 15, 1, 20, 1, 1, 0),
    3: Fighter2014Level(3, 2, 28, 16, 14, 15, 1, 19, 1, 1, 0),
    4: Fighter2014Level(4, 2, 36, 18, 14, 15, 1, 19, 1, 1, 0),
    5: Fighter2014Level(5, 3, 44, 18, 14, 15, 2, 19, 1, 1, 0),
    6: Fighter2014Level(6, 3, 52, 20, 14, 15, 2, 19, 1, 1, 0),
    7: Fighter2014Level(7, 3, 60, 20, 14, 15, 2, 19, 1, 1, 0, remarkable_athlete=True),
    8: Fighter2014Level(8, 3, 76, 20, 14, 17, 2, 19, 1, 1, 0, remarkable_athlete=True),
    9: Fighter2014Level(9, 4, 85, 20, 14, 17, 2, 19, 1, 1, 1, remarkable_athlete=True),
    10: Fighter2014Level(10, 4, 94, 20, 14, 17, 2, 19, 1, 1, 1, remarkable_athlete=True, second_fighting_style=True),
}


def _modifier(score: int) -> int:
    return (score - 10) // 2


def _resources(row: Fighter2014Level) -> list[ResourceDefinition]:
    values = (
        ("second-wind", "Second Wind", row.second_wind_uses),
        ("action-surge", "Action Surge", row.action_surge_uses),
        ("indomitable", "Indomitable", row.indomitable_uses),
    )
    return [ResourceDefinition(id=key, name=name, max_uses=uses) for key, name, uses in values if uses]


def _greatsword(row: Fighter2014Level) -> WeaponAttack:
    strength = _modifier(row.strength)
    return WeaponAttack(
        id="karnok-2014-greatsword", weapon=build_greatsword(),
        attack_bonus=row.proficiency_bonus + strength, damage_bonus=strength,
        attack_ability="strength", attack_ability_modifier=strength,
    )


def _shortbow(row: Fighter2014Level) -> WeaponAttack:
    dexterity = _modifier(row.dexterity)
    archery = 2 if row.second_fighting_style else 0
    return WeaponAttack(
        id="karnok-2014-shortbow", weapon=build_shortbow(),
        attack_bonus=row.proficiency_bonus + dexterity + archery, damage_bonus=dexterity,
        attack_ability="dexterity", attack_ability_modifier=dexterity,
    )


def build_karnok_stoneward_2014(level: int) -> CombatantTemplate:
    """Build the legal 2014 Human Champion test progression used by the first 2014 pregen lane."""
    if level not in LEVELS:
        raise ValueError(f"2014 Champion Fighter level {level} must be between 1 and 10.")
    row = LEVELS[level]
    strength = _modifier(row.strength)
    dexterity = _modifier(row.dexterity)
    constitution = _modifier(row.constitution)
    initiative = dexterity + ((row.proficiency_bonus + 1) // 2 if row.remarkable_athlete else 0)
    ids = ["karnok-2014-greatsword", "karnok-2014-shortbow"]
    attack_action = None
    if row.attack_count > 1:
        attack_action = {
            "id": "extra-attack", "name": "Extra Attack", "is_attack_action": True,
            "slots": [{"attack_ids": ids} for _ in range(row.attack_count)],
        }
    styles = ["Defense"] + (["Archery"] if row.second_fighting_style else [])
    return CombatantTemplate(
        id=f"hero-2014-fighter-l{level}", name="Karnok Stoneward", archetype="Fighter",
        level=level, kind="character", ruleset="2014",
        ability_scores=AbilityScores(
            strength=row.strength, dexterity=row.dexterity, constitution=row.constitution,
            intelligence=11, wisdom=11, charisma=11,
        ),
        armor_class=17, max_hp=row.max_hp, speed_ft=30, initiative_bonus=initiative,
        weapon_attack=_greatsword(row), alternate_weapon_attacks=[_shortbow(row)],
        attack_action=attack_action,
        saving_throw_bonuses={
            "strength": row.proficiency_bonus + strength, "dexterity": dexterity,
            "constitution": row.proficiency_bonus + constitution,
            "intelligence": 0, "wisdom": 0, "charisma": 0,
        },
        skill_bonuses={"athletics": row.proficiency_bonus + strength, "acrobatics": dexterity},
        resources=_resources(row), fighting_style="Defense", fighting_styles=styles,
        weapon_masteries=[], progression_features={"critical_hit_minimum": row.critical_minimum},
        visual=VisualLoadout(armor="chain-mail", main_hand="greatsword", body_style="humanoid"),
        source="D&D Basic Rules 2014: Human, Fighter, Champion, Equipment",
    )


def build_certified_fighter_2014_levels() -> list[CombatantTemplate]:
    return [build_karnok_stoneward_2014(level) for level in range(1, 11)]
