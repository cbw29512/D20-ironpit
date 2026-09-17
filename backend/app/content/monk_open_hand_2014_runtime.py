from __future__ import annotations

import logging

from app.content.character_math import fixed_hit_points, proficiency_bonus, saving_throw_bonuses
from app.content.weapon_catalog import build_weapon
from app.domain.actions import AttackActionDefinition, AttackActionSlot, ConditionRemovalAction, HealingAction
from app.domain.character_builds import AbilityScores
from app.domain.models import CombatantTemplate, DamageType, ResourceDefinition, VisualLoadout, Weapon, WeaponAttack, WeaponAttackKind
from app.domain.progression import ProgressionCombatFeatures

logger = logging.getLogger(__name__)


def _scores(level: int) -> AbilityScores:
    dexterity = 16 + (2 if level >= 4 else 0) + (2 if level >= 8 else 0)
    return AbilityScores(
        strength=13,
        dexterity=dexterity,
        constitution=14,
        intelligence=11,
        wisdom=15,
        charisma=9,
    )


def _martial_arts_die(level: int) -> int:
    return 4 if level < 5 else 6


def _speed(level: int) -> int:
    if level >= 10:
        return 50
    if level >= 6:
        return 45
    if level >= 2:
        return 40
    return 30


def _unarmed_attack(level: int, scores: AbilityScores) -> WeaponAttack:
    dexterity = scores.modifier("dexterity")
    weapon = Weapon(
        id="unarmed-strike",
        name="Unarmed Strike",
        attack_kind=WeaponAttackKind.MELEE,
        dice_count=1,
        dice_size=_martial_arts_die(level),
        damage_type=DamageType.BLUDGEONING,
        animation="strike",
        reach_ft=5,
    )
    return WeaponAttack(
        id="kael-2014-unarmed",
        weapon=weapon,
        attack_bonus=proficiency_bonus(level) + dexterity,
        damage_bonus=dexterity,
        attack_ability="dexterity",
        attack_ability_modifier=dexterity,
    )


def _shortsword_attack(level: int, scores: AbilityScores) -> WeaponAttack:
    dexterity = scores.modifier("dexterity")
    weapon = build_weapon("shortsword").model_copy(
        update={"mastery_property": None}
    )
    return WeaponAttack(
        id="kael-2014-shortsword",
        weapon=weapon,
        attack_bonus=proficiency_bonus(level) + dexterity,
        damage_bonus=dexterity,
        attack_ability="dexterity",
        attack_ability_modifier=dexterity,
    )


def _attack_action(level: int) -> AttackActionDefinition | None:
    if level < 5:
        return None
    choices = ["kael-2014-unarmed", "kael-2014-shortsword"]
    return AttackActionDefinition(
        id="extra-attack",
        name="Extra Attack",
        slots=[
            AttackActionSlot(attack_ids=choices),
            AttackActionSlot(attack_ids=choices),
        ],
        is_attack_action=True,
    )


def _resources(level: int) -> list[ResourceDefinition]:
    resources: list[ResourceDefinition] = []
    if level >= 2:
        resources.append(ResourceDefinition(id="ki", name="Ki", max_uses=level))
    if level >= 6:
        resources.append(
            ResourceDefinition(
                id="wholeness-of-body",
                name="Wholeness of Body",
                max_uses=1,
            )
        )
    return resources


def _healing_actions(level: int) -> list[HealingAction]:
    if level < 6:
        return []
    return [
        HealingAction(
            id="wholeness-of-body",
            name="Wholeness of Body",
            action_cost="action",
            range_ft=0,
            target_mode="self",
            dice_count=0,
            healing_bonus=3 * level,
            resource_id="wholeness-of-body",
            resource_cost=1,
            animation="healing",
        )
    ]


def _condition_removal_actions(level: int) -> list[ConditionRemovalAction]:
    if level < 7:
        return []
    return [
        ConditionRemovalAction(
            id="stillness-of-mind",
            name="Stillness of Mind",
            action_cost="action",
            range_ft=0,
            target_mode="self",
            removable_conditions=["charmed", "frightened"],
            max_conditions_per_use=1,
            animation="condition-removal",
        )
    ]


def _skill_bonuses(level: int, scores: AbilityScores) -> dict[str, int]:
    pb = proficiency_bonus(level)
    return {
        "acrobatics": scores.modifier("dexterity") + pb,
        "stealth": scores.modifier("dexterity") + pb,
        "insight": scores.modifier("wisdom") + pb,
        "religion": scores.modifier("intelligence") + pb,
    }


def build_kael_stillwater_2014(level: int) -> CombatantTemplate:
    """Compile Kael Stillwater, a 2014 Human Open Hand Monk, through level 10."""
    try:
        if level not in range(1, 11):
            raise ValueError("2014 Open Hand Monk certification covers levels 1 through 10.")
        scores = _scores(level)
        dexterity = scores.modifier("dexterity")
        wisdom = scores.modifier("wisdom")
        unarmed = _unarmed_attack(level, scores)
        shortsword = _shortsword_attack(level, scores)
        return CombatantTemplate(
            id=f"kael-stillwater-2014-l{level}",
            name="Kael Stillwater",
            archetype="Monk",
            level=level,
            kind="character",
            ruleset="2014",
            ability_scores=scores,
            armor_class=10 + dexterity + wisdom,
            max_hp=fixed_hit_points(level, 8, scores.modifier("constitution")),
            speed_ft=_speed(level),
            initiative_bonus=dexterity,
            weapon_attack=unarmed,
            alternate_weapon_attacks=[shortsword],
            attack_action=_attack_action(level),
            healing_actions=_healing_actions(level),
            condition_removal_actions=_condition_removal_actions(level),
            saving_throw_bonuses=saving_throw_bonuses(
                scores,
                level,
                ("strength", "dexterity"),
            ),
            skill_bonuses=_skill_bonuses(level, scores),
            weapon_masteries=[],
            condition_immunities=["poisoned"] if level >= 10 else [],
            resources=_resources(level),
            progression_features=ProgressionCombatFeatures(
                evasion=level >= 7,
                martial_arts_bonus_attack=True,
                martial_arts_die_size=_martial_arts_die(level),
                flurry_of_blows=level >= 2,
                deflect_missiles=level >= 3,
                open_hand_technique=level >= 3,
                stunning_strike=level >= 5,
            ),
            visual=VisualLoadout(
                armor="unarmored",
                main_hand="fists",
                body_style="humanoid",
            ),
            source=(
                "D&D Basic Rules 2014: Human, Acolyte, Equipment; "
                "D&D SRD 5.1 (2014): Monk, Way of the Open Hand"
            ),
        )
    except Exception:
        logger.exception("Failed to compile 2014 Kael Stillwater at level %s", level)
        raise
