from __future__ import annotations

import math

from app.content.weapon_catalog import build_weapon
from app.domain.character_builds import AbilityScores
from app.domain.models import CombatantTemplate, ResourceDefinition, VisualLoadout, WeaponAttack
from app.domain.progression import ProgressionCombatFeatures

_SOURCE = "D&D Beyond Basic Rules 2014: Fighter, Champion, Human, Soldier, Equipment"


def _pb(level: int) -> int:
    return 2 if level <= 4 else 3 if level <= 8 else 4


def _scores(level: int) -> AbilityScores:
    strength = 16 + (2 if level >= 4 else 0) + (2 if level >= 6 else 0)
    constitution = 16 + (2 if level >= 8 else 0)
    return AbilityScores(
        strength=strength, dexterity=14, constitution=constitution,
        intelligence=9, wisdom=11, charisma=9,
    )


def _max_hp(level: int, constitution: int) -> int:
    modifier = (constitution - 10) // 2
    return 10 + modifier + (level - 1) * (6 + modifier)


def _weapon(weapon_id: str):
    return build_weapon(weapon_id).model_copy(update={"mastery_property": None})


def _attacks(level: int, scores: AbilityScores) -> tuple[WeaponAttack, WeaponAttack]:
    proficiency = _pb(level)
    strength = (scores.strength - 10) // 2
    dexterity = (scores.dexterity - 10) // 2
    archery = 2 if level >= 10 else 0
    greatsword = WeaponAttack(
        id="karnok-2014-greatsword", weapon=_weapon("greatsword"),
        attack_bonus=proficiency + strength, damage_bonus=strength,
        attack_ability="strength", attack_ability_modifier=strength,
    )
    longbow = WeaponAttack(
        id="karnok-2014-longbow", weapon=_weapon("longbow"),
        attack_bonus=proficiency + dexterity + archery, damage_bonus=dexterity,
        attack_ability="dexterity", attack_ability_modifier=dexterity,
    )
    return greatsword, longbow


def _resources(level: int) -> list[ResourceDefinition]:
    rows = [("second-wind", "Second Wind", 1)]
    if level >= 2:
        rows.append(("action-surge", "Action Surge", 1))
    if level >= 9:
        rows.append(("indomitable", "Indomitable", 1))
    return [ResourceDefinition(id=key, name=name, max_uses=uses) for key, name, uses in rows]


def build_karnok_stoneward_2014_level(level: int) -> CombatantTemplate:
    """Compile the legal 2014 Champion test progression for levels 1-10."""
    if level not in range(1, 11):
        raise ValueError("2014 Karnok test progression supports levels 1 through 10.")
    scores = _scores(level)
    proficiency = _pb(level)
    strength = (scores.strength - 10) // 2
    dexterity = (scores.dexterity - 10) // 2
    constitution = (scores.constitution - 10) // 2
    remarkable = math.ceil(proficiency / 2) if level >= 7 else 0
    primary, ranged = _attacks(level, scores)
    attack_count = 2 if level >= 5 else 1
    attack_action = None if attack_count == 1 else {
        "id": "extra-attack", "name": "Extra Attack", "is_attack_action": True,
        "slots": [{"attack_ids": [primary.id, ranged.id]} for _ in range(attack_count)],
    }
    features = ProgressionCombatFeatures(
        critical_hit_minimum=19 if level >= 3 else 20,
        indomitable_reroll=level >= 9,
    )
    return CombatantTemplate(
        id=f"fighter-2014-canonical-l{level}", name="Karnok Stoneward",
        archetype="Fighter", level=level, kind="character", ruleset="2014",
        ability_scores=scores, armor_class=17, max_hp=_max_hp(level, scores.constitution),
        speed_ft=30, initiative_bonus=dexterity + remarkable,
        progression_features=features, weapon_attack=primary,
        alternate_weapon_attacks=[ranged], attack_action=attack_action,
        saving_throw_bonuses={
            "strength": proficiency + strength, "dexterity": dexterity,
            "constitution": proficiency + constitution, "intelligence": -1,
            "wisdom": 0, "charisma": -1,
        },
        skill_bonuses={"athletics": proficiency + strength, "acrobatics": dexterity + remarkable},
        fighting_style="Defense",
        fighting_styles=["Defense", "Archery"] if level >= 10 else ["Defense"],
        weapon_masteries=[], resources=_resources(level),
        visual=VisualLoadout(armor="chain-mail", main_hand="greatsword", body_style="humanoid"),
        source=_SOURCE,
    )


def build_certified_2014_fighter_levels() -> list[CombatantTemplate]:
    return [build_karnok_stoneward_2014_level(level) for level in range(1, 11)]
