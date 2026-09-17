from __future__ import annotations

import logging

from app.content.character_math import fixed_hit_points, proficiency_bonus, saving_throw_bonuses
from app.content.level_resources import barbarian_2014_rage_damage_bonus, barbarian_2014_rage_uses
from app.content.weapon_catalog import build_weapon
from app.domain.actions import AttackActionDefinition, AttackActionSlot
from app.domain.character_builds import AbilityScores
from app.domain.models import (
    CombatantTemplate,
    DamageType,
    ResourceDefinition,
    VisualLoadout,
    Weapon,
    WeaponAttack,
    WeaponAttackKind,
)
from app.domain.progression import ProgressionCombatFeatures
from app.domain.traits import CombatTrait

logger = logging.getLogger(__name__)


def _scores(level: int) -> AbilityScores:
    return AbilityScores(
        strength=17 + (1 if level >= 4 else 0) + (2 if level >= 8 else 0),
        dexterity=14,
        constitution=14 + (1 if level >= 4 else 0),
        intelligence=8,
        wisdom=12,
        charisma=10,
    )


def _greataxe_attack(level: int, scores: AbilityScores) -> WeaponAttack:
    weapon = build_weapon("greataxe").model_copy(update={"mastery_property": None})
    modifier = scores.modifier("strength")
    return WeaponAttack(
        id="rokhan-2014-greataxe",
        weapon=weapon,
        attack_bonus=proficiency_bonus(level) + modifier,
        damage_bonus=modifier,
        attack_ability="strength",
        attack_ability_modifier=modifier,
        rage_eligible=True,
    )


def _handaxe_throw(level: int, scores: AbilityScores) -> WeaponAttack:
    modifier = scores.modifier("strength")
    return WeaponAttack(
        id="rokhan-2014-handaxe-thrown",
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
            mastery_property=None,
            light=True,
        ),
        attack_bonus=proficiency_bonus(level) + modifier,
        damage_bonus=modifier,
        attack_ability="strength",
        attack_ability_modifier=modifier,
        rage_eligible=False,
    )


def _resources(level: int) -> list[ResourceDefinition]:
    return [
        ResourceDefinition(id="rage", name="Rage", max_uses=barbarian_2014_rage_uses(level)),
        ResourceDefinition(id="relentless-endurance", name="Relentless Endurance", max_uses=1),
    ]


def build_rokhan_stonefury_2014(level: int) -> CombatantTemplate:
    """Compile Rokhan as a legal 2014 Half-Orc Berserker Barbarian, levels 1-10."""
    try:
        if level not in range(1, 11):
            raise ValueError("2014 Berserker Barbarian certification currently covers levels 1 through 10.")
        scores = _scores(level)
        greataxe = _greataxe_attack(level, scores)
        handaxe = _handaxe_throw(level, scores)
        attacks_per_action = 2 if level >= 5 else 1
        attack_action = AttackActionDefinition(
            id="attack",
            name="Attack",
            is_attack_action=True,
            slots=[AttackActionSlot(attack_ids=[greataxe.id, handaxe.id]) for _ in range(attacks_per_action)],
        )
        return CombatantTemplate(
            id=f"rokhan-stonefury-2014-l{level}",
            name="Rokhan Stonefury",
            archetype="Barbarian",
            level=level,
            kind="character",
            ruleset="2014",
            ability_scores=scores,
            armor_class=10 + scores.modifier("dexterity") + scores.modifier("constitution"),
            max_hp=fixed_hit_points(level, 12, scores.modifier("constitution")),
            speed_ft=40 if level >= 5 else 30,
            initiative_bonus=scores.modifier("dexterity"),
            weapon_attack=greataxe,
            alternate_weapon_attacks=[handaxe],
            attack_action=attack_action,
            saving_throw_bonuses=saving_throw_bonuses(scores, level, ("strength", "constitution")),
            skill_bonuses={
                "athletics": scores.modifier("strength") + proficiency_bonus(level),
                "intimidation": scores.modifier("charisma") + proficiency_bonus(level),
                "perception": scores.modifier("wisdom") + proficiency_bonus(level),
                "survival": scores.modifier("wisdom") + proficiency_bonus(level),
            },
            combat_traits=[CombatTrait.RELENTLESS_ENDURANCE],
            weapon_masteries=[],
            wearing_heavy_armor=False,
            rage_damage_bonus=barbarian_2014_rage_damage_bonus(level),
            visual=VisualLoadout(armor="unarmored", main_hand="greataxe", body_style="humanoid"),
            resources=_resources(level),
            progression_features=ProgressionCombatFeatures(
                initiative_advantage=level >= 7,
                danger_sense=level >= 2,
                reckless_attack=level >= 2,
                frenzy_bonus_attack_2014=level >= 3,
                mindless_rage=level >= 6,
                fast_movement_bonus_ft=10 if level >= 5 else 0,
                melee_critical_extra_weapon_dice=1 + (1 if level >= 9 else 0),
                intimidating_presence_2014=level >= 10,
            ),
            source="D&D Basic Rules 2014: Half-Orc; Barbarian; Path of the Berserker; Soldier; Equipment",
        )
    except Exception:
        logger.exception("Failed to compile 2014 Rokhan Stonefury at level %s", level)
        raise
