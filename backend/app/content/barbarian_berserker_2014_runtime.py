from __future__ import annotations

import logging

from app.content.character_math import fixed_hit_points, proficiency_bonus, saving_throw_bonuses
from app.content.level_resources import barbarian_2014_rage_uses, barbarian_rage_damage_bonus
from app.content.weapon_catalog import build_weapon
from app.domain.actions import AttackActionDefinition, AttackActionSlot
from app.domain.character_builds import AbilityScores
from app.domain.models import CombatantTemplate, ResourceDefinition, VisualLoadout, WeaponAttack
from app.domain.progression import ProgressionCombatFeatures

logger = logging.getLogger(__name__)


def _scores(level: int) -> AbilityScores:
    strength = 16 + (2 if level >= 4 else 0) + (2 if level >= 8 else 0)
    return AbilityScores(strength=strength, dexterity=14, constitution=15,
                         intelligence=9, wisdom=13, charisma=11)


def _attack(level: int, weapon_id: str, scores: AbilityScores, *, rage_eligible: bool) -> WeaponAttack:
    weapon = build_weapon(weapon_id).model_copy(update={"mastery_property": None})
    modifier = scores.modifier("strength")
    return WeaponAttack(
        id=f"rokhan-2014-{weapon_id}", weapon=weapon,
        attack_bonus=proficiency_bonus(level) + modifier, damage_bonus=modifier,
        attack_ability="strength", attack_ability_modifier=modifier, rage_eligible=rage_eligible,
    )


def _progression(level: int) -> ProgressionCombatFeatures:
    return ProgressionCombatFeatures(
        danger_sense=level >= 2,
        reckless_attack=level >= 2,
        frenzy=level >= 3,
        fast_movement_bonus_ft=10 if level >= 5 else 0,
        mindless_rage=level >= 6,
        initiative_advantage=level >= 7,
        brutal_critical_dice=1 if level >= 9 else 0,
    )


def build_rokhan_stonefury_2014(level: int) -> CombatantTemplate:
    """Compile the 2014 Human Path of the Berserker Barbarian through Brutal Critical."""
    try:
        if level not in range(1, 10):
            raise ValueError("2014 Berserker certification currently covers levels 1 through 9.")
        scores = _scores(level)
        greataxe = _attack(level, "greataxe", scores, rage_eligible=True)
        handaxe = _attack(level, "handaxe", scores, rage_eligible=False)
        attack_count = 2 if level >= 5 else 1
        action = AttackActionDefinition(
            id="attack", name="Attack", is_attack_action=True,
            slots=[AttackActionSlot(attack_ids=[greataxe.id, handaxe.id]) for _ in range(attack_count)],
        )
        dexterity = scores.modifier("dexterity"); constitution = scores.modifier("constitution")
        return CombatantTemplate(
            id=f"rokhan-stonefury-2014-l{level}", name="Rokhan Stonefury", archetype="Barbarian",
            level=level, kind="character", ruleset="2014", ability_scores=scores,
            armor_class=10 + dexterity + constitution,
            max_hp=fixed_hit_points(level, 12, constitution), speed_ft=40 if level >= 5 else 30,
            initiative_bonus=dexterity, weapon_attack=greataxe, alternate_weapon_attacks=[handaxe],
            attack_action=action,
            saving_throw_bonuses=saving_throw_bonuses(scores, level, ("strength", "constitution")),
            skill_bonuses={"athletics": scores.modifier("strength") + proficiency_bonus(level),
                           "acrobatics": dexterity},
            weapon_masteries=[], wearing_heavy_armor=False,
            rage_damage_bonus=barbarian_rage_damage_bonus(level),
            progression_features=_progression(level),
            resources=[ResourceDefinition(id="rage", name="Rage", max_uses=barbarian_2014_rage_uses(level))],
            visual=VisualLoadout(armor="unarmored", main_hand="greataxe", body_style="humanoid"),
            source="D&D Basic Rules 2014: Human; Barbarian; Path of the Berserker; Outlander; Equipment",
        )
    except Exception:
        logger.exception("Failed to compile 2014 Rokhan Stonefury at level %s", level)
        raise
