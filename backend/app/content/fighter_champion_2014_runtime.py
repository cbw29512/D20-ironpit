from __future__ import annotations

import logging

from app.content.armor_catalog import get_armor
from app.content.armor_class_rules import compile_worn_armor_class
from app.content.character_math import fixed_hit_points, proficiency_bonus, saving_throw_bonuses
from app.content.weapon_catalog import build_weapon
from app.domain.actions import AttackActionDefinition, AttackActionSlot
from app.domain.character_builds import AbilityScores
from app.domain.models import CombatantTemplate, ResourceDefinition, VisualLoadout, WeaponAttack, WeaponAttackKind
from app.domain.progression import ProgressionCombatFeatures

logger = logging.getLogger(__name__)


def _scores(level: int) -> AbilityScores:
    strength = 16 + (2 if level >= 4 else 0) + (2 if level >= 6 else 0)
    dexterity = 14 + (1 if level >= 8 else 0) + (1 if level >= 14 else 0) + (2 if level >= 16 else 0)
    constitution = 15 + (1 if level >= 8 else 0) + (2 if level >= 12 else 0) + (1 if level >= 14 else 0) + (1 if level >= 19 else 0)
    wisdom = 13 + (1 if level >= 19 else 0)
    return AbilityScores(strength=strength, dexterity=dexterity, constitution=constitution,
                         intelligence=9, wisdom=wisdom, charisma=11)


def _attack(level: int, weapon_id: str, scores: AbilityScores) -> WeaponAttack:
    weapon = build_weapon(weapon_id).model_copy(update={"mastery_property": None})
    ability = "dexterity" if weapon.attack_kind is WeaponAttackKind.RANGED else "strength"
    modifier = scores.modifier(ability)
    style_bonus = 2 if weapon.attack_kind is WeaponAttackKind.RANGED and level >= 10 else 0
    return WeaponAttack(id=f"karnok-2014-{weapon_id}", weapon=weapon,
                        attack_bonus=proficiency_bonus(level) + modifier + style_bonus,
                        damage_bonus=modifier, attack_ability=ability, attack_ability_modifier=modifier)


def _resources(level: int) -> list[ResourceDefinition]:
    resources = [ResourceDefinition(id="second-wind", name="Second Wind", max_uses=1)]
    if level >= 2:
        resources.append(ResourceDefinition(id="action-surge", name="Action Surge", max_uses=2 if level >= 17 else 1))
    if level >= 9:
        uses = 3 if level >= 17 else 2 if level >= 13 else 1
        resources.append(ResourceDefinition(id="indomitable", name="Indomitable", max_uses=uses))
    return resources


def _remarkable_athlete_bonus(level: int) -> int:
    return (proficiency_bonus(level) + 1) // 2 if level >= 7 else 0


def _fighting_styles(level: int) -> list[str]:
    return ["Defense", *(["Archery"] if level >= 10 else [])]


def _attacks_per_action(level: int) -> int:
    if level >= 20:
        return 4
    if level >= 11:
        return 3
    return 2 if level >= 5 else 1


def _critical_minimum(level: int) -> int:
    return 18 if level >= 15 else 19 if level >= 3 else 20


def build_karnok_stoneward_2014(level: int) -> CombatantTemplate:
    """Compile the legal 2014 Human Champion Fighter baseline for Iron Pit."""
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Champion Fighter certification covers levels 1 through 20.")
        scores = _scores(level); styles = _fighting_styles(level); armor = get_armor("chain-mail")
        armor_class = compile_worn_armor_class(armor.base_ac, armor.category, scores.modifier("dexterity"),
                                               styles, wielding_shield=False, shield_trained=True)
        greatsword = _attack(level, "greatsword", scores); longbow = _attack(level, "longbow", scores)
        action = AttackActionDefinition(
            id="attack", name="Attack", is_attack_action=True,
            slots=[AttackActionSlot(attack_ids=[greatsword.id, longbow.id]) for _ in range(_attacks_per_action(level))],
        )
        remarkable = _remarkable_athlete_bonus(level)
        survivor = 5 + scores.modifier("constitution") if level >= 18 else 0
        return CombatantTemplate(
            id=f"karnok-stoneward-2014-l{level}", name="Karnok Stoneward", archetype="Fighter", level=level,
            kind="character", ruleset="2014", ability_scores=scores, armor_class=armor_class,
            max_hp=fixed_hit_points(level, 10, scores.modifier("constitution")), speed_ft=30,
            initiative_bonus=scores.modifier("dexterity") + remarkable, weapon_attack=greatsword,
            alternate_weapon_attacks=[longbow], attack_action=action,
            saving_throw_bonuses=saving_throw_bonuses(scores, level, ("strength", "constitution")),
            skill_bonuses={"athletics": scores.modifier("strength") + proficiency_bonus(level),
                           "acrobatics": scores.modifier("dexterity") + remarkable},
            fighting_style=styles[0], fighting_styles=styles, weapon_masteries=[],
            visual=VisualLoadout(armor=armor.id, main_hand="greatsword", body_style="humanoid"),
            resources=_resources(level),
            progression_features=ProgressionCombatFeatures(
                critical_hit_minimum=_critical_minimum(level), indomitable_reroll=level >= 9,
                indomitable_bonus=0, survivor_heal_amount=survivor,
            ),
            source="D&D Basic Rules 2014: Human; Fighter; Champion; Soldier; Equipment",
        )
    except Exception:
        logger.exception("Failed to compile 2014 Karnok Stoneward at level %s", level)
        raise
