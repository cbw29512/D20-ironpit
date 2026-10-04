from __future__ import annotations

import logging

from app.content.armor_catalog import get_armor
from app.content.armor_class_rules import compile_worn_armor_class
from app.content.attack_bonus_rules import compile_weapon_attack_bonus
from app.content.character_math import fixed_hit_points, proficiency_bonus, saving_throw_bonuses
from app.content.character_resource_rules import expected_resources
from app.content.healing_spell_effects import build_cure_wounds
from app.content.ranger_hunter_2024_level1 import hunters_mark_2024
from app.content.ranger_hunter_2024_profile import build_rowan_ashtrail_2024_profile
from app.content.weapon_catalog import build_weapon
from app.domain.models import CombatantTemplate, ResourceDefinition, VisualLoadout, WeaponAttack
from app.domain.progression import ProgressionCombatFeatures, SavingThrowAdvantageGrant

logger = logging.getLogger(__name__)
_ABILITIES = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]


def _weapon(weapon_id: str, dexterity: int, level: int) -> WeaponAttack:
    try:
        weapon = build_weapon(weapon_id)
        return WeaponAttack(
            id=f"rowan-2024-{weapon_id}",
            weapon=weapon,
            attack_bonus=compile_weapon_attack_bonus(
                proficiency_bonus(level) + dexterity,
                [],
                weapon.attack_kind,
            ),
            damage_bonus=dexterity,
            attack_ability="dexterity",
            attack_ability_modifier=dexterity,
        )
    except Exception:
        logger.exception("Failed to build 2024 Rowan weapon %s.", weapon_id)
        raise


def build_rowan_ashtrail_2024(level: int = 1) -> CombatantTemplate:
    try:
        profile = build_rowan_ashtrail_2024_profile(level)
        scores = profile.final_ability_scores
        dexterity = scores.modifier("dexterity")
        wisdom = scores.modifier("wisdom")
        pb = proficiency_bonus(level)
        armor = get_armor("studded-leather")
        longbow = _weapon("longbow", dexterity, level)
        shortsword = _weapon("shortsword", dexterity, level)
        scimitar = _weapon("scimitar", dexterity, level)
        resources = expected_resources(profile)
        return CombatantTemplate(
            id=profile.template_id,
            name=profile.character_name,
            archetype="Ranger",
            level=level,
            kind="character",
            ruleset="2024",
            creature_type="humanoid",
            ability_scores=scores,
            armor_class=compile_worn_armor_class(
                armor.base_ac, armor.category, dexterity, [],
                wielding_shield=False, shield_trained=True,
            ),
            max_hp=fixed_hit_points(level, 10, scores.modifier("constitution")),
            speed_ft=35,
            initiative_bonus=dexterity + pb,
            weapon_attack=longbow,
            alternate_weapon_attacks=[shortsword, scimitar],
            targeted_concentration_damage_actions=[hunters_mark_2024()],
            healing_actions=[build_cure_wounds(wisdom)],
            saving_throw_bonuses=saving_throw_bonuses(scores, level, ("strength", "dexterity")),
            skill_bonuses={
                "athletics": scores.modifier("strength") + pb,
                "survival": wisdom + pb,
                "perception": wisdom + pb,
                "stealth": dexterity + pb,
                "insight": wisdom + pb,
                "investigation": scores.modifier("intelligence") + pb,
            },
            weapon_masteries=["longbow", "shortsword"],
            progression_features=ProgressionCombatFeatures(
                saving_throw_advantage_grants=[
                    SavingThrowAdvantageGrant(
                        source_id="fey-ancestry",
                        source_name="Fey Ancestry",
                        abilities=_ABILITIES,
                        required_effect_tags=["charm"],
                    ),
                ],
            ),
            resources=[
                ResourceDefinition(id=resource_id, name=resource_id.replace("-", " ").title(), max_uses=uses)
                for resource_id, uses in resources.items()
            ],
            visual=VisualLoadout(
                armor="studded-leather", main_hand="longbow", body_style="humanoid"
            ),
            source=(
                "D&D Beyond Basic Rules 2024: Ranger 1, Elf — Wood Elf, "
                "Hunter's Mark, Cure Wounds; converted legacy Outlander background"
            ),
        )
    except Exception:
        logger.exception("Failed to build 2024 Rowan Ashtrail at level %s.", level)
        raise
