from __future__ import annotations

import logging

from app.content.armor_catalog import get_armor
from app.content.armor_class_rules import compile_worn_armor_class
from app.content.character_math import fixed_hit_points, proficiency_bonus, saving_throw_bonuses
from app.content.cleric_2014_level1_spells import cure_wounds_2014, healing_word_2014
from app.content.druid_2014_level1_spells import longstrider_2014, poison_spray_2014, produce_flame_2014
from app.content.druid_2014_progression import druid_2014_level
from app.content.druid_land_2014_profile import build_thalen_greenbough_2014_profile
from app.content.weapon_catalog import build_weapon
from app.domain.models import CombatantTemplate, ResourceDefinition, VisualLoadout, WeaponAttack
from app.domain.progression import ProgressionCombatFeatures, SavingThrowAdvantageGrant

logger = logging.getLogger(__name__)
_ABILITIES = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]


def _scimitar(level: int, scores) -> WeaponAttack:
    weapon = build_weapon("scimitar").model_copy(update={"mastery_property": None})
    modifier = scores.modifier("dexterity")
    return WeaponAttack(
        id="thalen-2014-scimitar",
        weapon=weapon,
        attack_bonus=proficiency_bonus(level) + modifier,
        damage_bonus=modifier,
        attack_ability="dexterity",
        attack_ability_modifier=modifier,
    )


def _resources(level: int) -> list[ResourceDefinition]:
    row = druid_2014_level(level)
    return [
        ResourceDefinition(
            id=f"spell-slot-{spell_level}",
            name=f"Spell Slot {spell_level}",
            max_uses=uses,
        )
        for spell_level, uses in enumerate(row.spell_slots, start=1)
        if uses
    ]


def build_thalen_greenbough_2014(level: int) -> CombatantTemplate:
    try:
        if level != 1:
            raise ValueError("2014 Land Druid runtime is currently certified only at level 1.")
        profile = build_thalen_greenbough_2014_profile(level)
        scores = profile.final_ability_scores
        pb = proficiency_bonus(level)
        wisdom_modifier = scores.modifier("wisdom")
        spell_attack = pb + wisdom_modifier
        save_dc = 8 + spell_attack
        armor = get_armor("leather")
        armor_class = compile_worn_armor_class(
            armor.base_ac,
            armor.category,
            scores.modifier("dexterity"),
            [],
            wielding_shield=True,
            shield_trained=True,
        )
        return CombatantTemplate(
            id=profile.template_id,
            name=profile.character_name,
            archetype="Druid",
            level=level,
            kind="character",
            ruleset="2014",
            ability_scores=scores,
            armor_class=armor_class,
            max_hp=fixed_hit_points(level, 8, scores.modifier("constitution")),
            speed_ft=35,
            initiative_bonus=scores.modifier("dexterity"),
            weapon_attack=_scimitar(level, scores),
            spell_attack_actions=[produce_flame_2014(spell_attack, level)],
            spell_save_actions=[poison_spray_2014(save_dc, level)],
            defensive_spell_actions=[longstrider_2014()],
            healing_actions=[
                healing_word_2014(wisdom_modifier, 0),
                cure_wounds_2014(wisdom_modifier, 0),
            ],
            progression_features=ProgressionCombatFeatures(
                saving_throw_advantage_grants=[
                    SavingThrowAdvantageGrant(
                        source_id="fey-ancestry",
                        source_name="Fey Ancestry",
                        abilities=_ABILITIES,
                        required_effect_tags=["charm"],
                    )
                ],
            ),
            saving_throw_bonuses=saving_throw_bonuses(
                scores,
                level,
                ("intelligence", "wisdom"),
            ),
            skill_bonuses={
                "insight": wisdom_modifier + pb,
                "religion": scores.modifier("intelligence") + pb,
                "perception": wisdom_modifier + pb,
                "survival": wisdom_modifier + pb,
            },
            weapon_masteries=[],
            resources=_resources(level),
            visual=VisualLoadout(
                armor="leather",
                main_hand="scimitar",
                off_hand="wooden-shield",
                body_style="humanoid",
            ),
            source=(
                "D&D Basic Rules 2014: Wood Elf, Acolyte, Druid, Produce Flame, Poison Spray, "
                "Healing Word, Cure Wounds, Longstrider, Equipment"
            ),
        )
    except Exception:
        logger.exception("Failed to compile 2014 Thalen Greenbough at level %s.", level)
        raise
