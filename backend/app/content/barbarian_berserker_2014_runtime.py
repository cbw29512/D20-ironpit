from __future__ import annotations

import logging

from app.content.character_math import fixed_hit_points, proficiency_bonus, saving_throw_bonuses
from app.content.level_resources import barbarian_2014_rage_uses, barbarian_rage_damage_bonus
from app.content.weapon_catalog import build_weapon
from app.domain.actions import AttackActionDefinition, AttackActionSlot
from app.domain.character_builds import AbilityScores
from app.domain.models import CombatantTemplate, ResourceDefinition, VisualLoadout, WeaponAttack
from app.domain.progression import AbilityCheckMinimum, EffectBoundSurvivalSave, ProgressionCombatFeatures
from app.domain.reactions import DamageReactionAttack

logger = logging.getLogger(__name__)


def _scores(level: int) -> AbilityScores:
    strength = 16 + (2 if level >= 4 else 0) + (2 if level >= 8 else 0) + (4 if level >= 20 else 0)
    constitution = (
        15 + (1 if level >= 12 else 0) + (2 if level >= 16 else 0)
        + (2 if level >= 19 else 0) + (4 if level >= 20 else 0)
    )
    wisdom = 13 + (1 if level >= 12 else 0)
    return AbilityScores(strength=strength, dexterity=14, constitution=constitution,
                         intelligence=9, wisdom=wisdom, charisma=11)


def _attack(level: int, weapon_id: str, scores: AbilityScores, *, rage_eligible: bool) -> WeaponAttack:
    weapon = build_weapon(weapon_id).model_copy(update={"mastery_property": None})
    modifier = scores.modifier("strength")
    return WeaponAttack(
        id=f"rokhan-2014-{weapon_id}", weapon=weapon,
        attack_bonus=proficiency_bonus(level) + modifier, damage_bonus=modifier,
        attack_ability="strength", attack_ability_modifier=modifier, rage_eligible=rage_eligible,
    )


def _damage_reaction(level: int) -> DamageReactionAttack | None:
    return DamageReactionAttack(source_feature="retaliation") if level >= 14 else None


def _progression(level: int, scores: AbilityScores) -> ProgressionCombatFeatures:
    presence_dc = 8 + proficiency_bonus(level) + scores.modifier("charisma") if level >= 10 else 0
    brutal_dice = 3 if level >= 17 else 2 if level >= 13 else 1 if level >= 9 else 0
    relentless = (
        EffectBoundSurvivalSave(
            source_id="relentless-rage", required_effect_id="rage",
            save_ability="constitution", initial_dc=10, dc_increment=5, replacement_hp=1,
        )
        if level >= 11 else None
    )
    check_minimums = (
        [AbilityCheckMinimum(source_id="indomitable-might", ability="strength")]
        if level >= 18 else []
    )
    return ProgressionCombatFeatures(
        effect_bound_survival_save=relentless,
        ability_check_minimums=check_minimums,
        danger_sense=level >= 2, reckless_attack=level >= 2,
        frenzy_bonus_attack_2014=level >= 3,
        persistent_rage_2014=level >= 15,
        fast_movement_bonus_ft=10 if level >= 5 else 0, mindless_rage=level >= 6,
        initiative_advantage=level >= 7, brutal_critical_dice=brutal_dice,
        intimidating_presence_2014_dc=presence_dc,
    )


def build_rokhan_stonefury_2014(level: int) -> CombatantTemplate:
    """Compile the certified 2014 Human Path of the Berserker Barbarian through level 13."""
    try:
        if level not in range(1, 14):
            raise ValueError("2014 Berserker certification covers levels 1 through 13.")
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
            damage_reaction_attack=_damage_reaction(level),
            saving_throw_bonuses=saving_throw_bonuses(scores, level, ("strength", "constitution")),
            skill_bonuses={"athletics": scores.modifier("strength") + proficiency_bonus(level),
                           "acrobatics": dexterity},
            weapon_masteries=[], wearing_heavy_armor=False,
            rage_damage_bonus=barbarian_rage_damage_bonus(level), progression_features=_progression(level, scores),
            resources=(
                [] if level >= 20
                else [ResourceDefinition(id="rage", name="Rage", max_uses=barbarian_2014_rage_uses(level))]
            ),
            unlimited_resource_ids=["rage"] if level >= 20 else [],
            visual=VisualLoadout(armor="unarmored", main_hand="greataxe", body_style="humanoid"),
            source="D&D Basic Rules 2014: Human; Barbarian; Path of the Berserker; Soldier; Equipment",
        )
    except Exception:
        logger.exception("Failed to compile 2014 Rokhan Stonefury at level %s", level)
        raise
