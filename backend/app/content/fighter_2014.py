from __future__ import annotations

import logging
import math

from app.content.fighter_2014_combat_levels import fighter_2014_level
from app.content.weapon_catalog_2014 import build_weapon_2014
from app.domain.character_builds import AbilityScores
from app.domain.models import (
    AttackActionDefinition,
    AttackActionSlot,
    CombatantTemplate,
    ResourceDefinition,
    VisualLoadout,
    WeaponAttack,
)
from app.domain.progression import ProgressionCombatFeatures

logger = logging.getLogger(__name__)


def karnok_2014_template_id(level: int) -> str:
    return f"karnok-stoneward-2014-l{level}"


def _modifier(score: int) -> int:
    return (score - 10) // 2


def _attacks(level: int) -> tuple[WeaponAttack, WeaponAttack]:
    row = fighter_2014_level(level)
    strength_mod = _modifier(row.strength)
    dexterity_mod = _modifier(row.dexterity)
    archery_bonus = 2 if "Archery" in row.fighting_styles else 0
    return (
        WeaponAttack(
            id="karnok-2014-greatsword",
            weapon=build_weapon_2014("greatsword"),
            attack_bonus=row.proficiency_bonus + strength_mod,
            damage_bonus=strength_mod,
            attack_ability="strength",
            attack_ability_modifier=strength_mod,
        ),
        WeaponAttack(
            id="karnok-2014-longbow",
            weapon=build_weapon_2014("longbow"),
            attack_bonus=row.proficiency_bonus + dexterity_mod + archery_bonus,
            damage_bonus=dexterity_mod,
            attack_ability="dexterity",
            attack_ability_modifier=dexterity_mod,
        ),
    )


def _resources(level: int) -> list[ResourceDefinition]:
    row = fighter_2014_level(level)
    definitions = [
        ("second-wind", "Second Wind", row.second_wind_uses),
        ("action-surge", "Action Surge", row.action_surge_uses),
        ("indomitable", "Indomitable", row.indomitable_uses),
    ]
    return [
        ResourceDefinition(id=resource_id, name=name, max_uses=uses)
        for resource_id, name, uses in definitions
        if uses > 0
    ]


def _attack_action(level: int) -> AttackActionDefinition | None:
    row = fighter_2014_level(level)
    if row.attack_count <= 1:
        return None
    choices = ["karnok-2014-greatsword", "karnok-2014-longbow"]
    return AttackActionDefinition(
        id="extra-attack",
        name="Extra Attack",
        is_attack_action=True,
        slots=[AttackActionSlot(attack_ids=choices) for _ in range(row.attack_count)],
    )


def build_karnok_stoneward_2014(level: int) -> CombatantTemplate:
    """Compile the legal 2014 Human Champion Fighter progression for Iron Pit."""
    try:
        row = fighter_2014_level(level)
        greatsword, longbow = _attacks(level)
        half_proficiency = math.ceil(row.proficiency_bonus / 2) if row.remarkable_athlete else 0
        dexterity_mod = _modifier(row.dexterity)
        strength_mod = _modifier(row.strength)
        constitution_mod = _modifier(row.constitution)
        return CombatantTemplate(
            id=karnok_2014_template_id(level),
            name="Karnok Stoneward",
            archetype="Fighter",
            level=level,
            kind="character",
            ruleset="2014",
            ability_scores=AbilityScores(
                strength=row.strength,
                dexterity=row.dexterity,
                constitution=row.constitution,
                intelligence=row.intelligence,
                wisdom=row.wisdom,
                charisma=row.charisma,
            ),
            armor_class=17,
            max_hp=row.max_hp,
            speed_ft=30,
            initiative_bonus=dexterity_mod + half_proficiency,
            progression_features=ProgressionCombatFeatures(
                critical_hit_minimum=row.critical_hit_minimum,
            ),
            weapon_attack=greatsword,
            alternate_weapon_attacks=[longbow],
            attack_action=_attack_action(level),
            saving_throw_bonuses={
                "strength": row.proficiency_bonus + strength_mod,
                "dexterity": dexterity_mod,
                "constitution": row.proficiency_bonus + constitution_mod,
                "intelligence": _modifier(row.intelligence),
                "wisdom": _modifier(row.wisdom),
                "charisma": _modifier(row.charisma),
            },
            skill_bonuses={
                "athletics": row.proficiency_bonus + strength_mod,
                "acrobatics": dexterity_mod + half_proficiency,
                "intimidation": row.proficiency_bonus + _modifier(row.charisma),
                "perception": row.proficiency_bonus + _modifier(row.wisdom),
            },
            fighting_style=row.fighting_styles[0],
            fighting_styles=list(row.fighting_styles),
            weapon_masteries=[],
            wearing_heavy_armor=True,
            visual=VisualLoadout(
                armor="chain-mail",
                main_hand="greatsword",
                body_style="humanoid",
            ),
            resources=_resources(level),
            source=row.source,
        )
    except Exception:
        logger.exception("Failed to compile 2014 Karnok Stoneward level %s.", level)
        raise
