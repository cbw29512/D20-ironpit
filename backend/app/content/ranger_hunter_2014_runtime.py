from __future__ import annotations

import logging

from app.content.armor_catalog import get_armor
from app.content.armor_class_rules import compile_worn_armor_class
from app.content.attack_bonus_rules import compile_weapon_attack_bonus
from app.content.character_math import fixed_hit_points, proficiency_bonus, saving_throw_bonuses
from app.content.cleric_2014_level1_spells import cure_wounds_2014
from app.content.druid_2014_level1_spells import longstrider_2014
from app.content.ranger_2014_progression import ranger_2014_level
from app.content.ranger_hunter_2014_level3 import colossus_slayer_2014
from app.content.ranger_hunter_2014_profile import build_rowan_ashtrail_2014_profile
from app.content.weapon_catalog import build_weapon
from app.domain.models import CombatantTemplate, ResourceDefinition, VisualLoadout, WeaponAttack
from app.domain.progression import ProgressionCombatFeatures, SavingThrowAdvantageGrant

logger = logging.getLogger(__name__)
_ABILITIES = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]


def _weapon(level: int, weapon_id: str, dexterity: int) -> WeaponAttack:
    weapon = build_weapon(weapon_id).model_copy(update={"mastery_property": None})
    styles = ["Archery"] if level >= 2 else []
    return WeaponAttack(
        id=f"rowan-2014-{weapon_id}", weapon=weapon,
        attack_bonus=compile_weapon_attack_bonus(
            proficiency_bonus(level) + dexterity, styles, weapon.attack_kind,
        ),
        damage_bonus=dexterity, attack_ability="dexterity",
        attack_ability_modifier=dexterity,
    )


def _resources(level: int) -> list[ResourceDefinition]:
    return [
        ResourceDefinition(id=f"spell-slot-{spell_level}", name=f"Spell Slot {spell_level}", max_uses=uses)
        for spell_level, uses in enumerate(ranger_2014_level(level).spell_slots, start=1)
        if uses
    ]


def build_rowan_ashtrail_2014(level: int) -> CombatantTemplate:
    try:
        if level not in range(1, 4):
            raise ValueError("2014 Hunter Ranger runtime currently covers levels 1 through 3.")
        profile = build_rowan_ashtrail_2014_profile(level)
        scores = profile.final_ability_scores
        dexterity = scores.modifier("dexterity")
        armor = get_armor("leather")
        longbow = _weapon(level, "longbow", dexterity)
        shortsword = _weapon(level, "shortsword", dexterity)
        return CombatantTemplate(
            id=profile.template_id, name=profile.character_name, archetype="Ranger",
            level=level, kind="character", ruleset="2014", ability_scores=scores,
            armor_class=compile_worn_armor_class(
                armor.base_ac, armor.category, dexterity, [],
                wielding_shield=False, shield_trained=True,
            ),
            max_hp=fixed_hit_points(level, 10, scores.modifier("constitution")),
            speed_ft=35, initiative_bonus=dexterity,
            weapon_attack=longbow, alternate_weapon_attacks=[shortsword],
            defensive_spell_actions=[longstrider_2014()] if level >= 2 else [],
            healing_actions=[cure_wounds_2014(scores.modifier("wisdom"), 0)] if level >= 2 else [],
            saving_throw_bonuses=saving_throw_bonuses(scores, level, ("strength", "dexterity")),
            skill_bonuses={
                "athletics": scores.modifier("strength") + proficiency_bonus(level),
                "survival": scores.modifier("wisdom") + proficiency_bonus(level),
                "perception": scores.modifier("wisdom") + proficiency_bonus(level),
                "stealth": dexterity + proficiency_bonus(level),
                "insight": scores.modifier("wisdom") + proficiency_bonus(level),
                "investigation": scores.modifier("intelligence") + proficiency_bonus(level),
            },
            weapon_masteries=[],
            progression_features=ProgressionCombatFeatures(
                once_per_turn_weapon_hit_damage_rider=colossus_slayer_2014() if level >= 3 else None,
                saving_throw_advantage_grants=[
                    SavingThrowAdvantageGrant(
                        source_id="fey-ancestry",
                        source_name="Fey Ancestry",
                        abilities=_ABILITIES,
                        required_effect_tags=["charm"],
                    )
                ],
            ),
            fighting_style="Archery" if level >= 2 else None,
            fighting_styles=["Archery"] if level >= 2 else [],
            resources=_resources(level),
            visual=VisualLoadout(armor="leather", main_hand="longbow", body_style="humanoid"),
            source="D&D Basic Rules 2014: Wood Elf; Outlander; Ranger; Equipment",
        )
    except Exception:
        logger.exception("Failed to compile 2014 Rowan Ashtrail at level %s.", level)
        raise
