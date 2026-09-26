from __future__ import annotations

import logging

from app.content.armor_catalog import get_armor
from app.content.armor_class_rules import compile_worn_armor_class
from app.content.character_math import fixed_hit_points, proficiency_bonus, saving_throw_bonuses
from app.content.cleric_2014_level1_spells import cure_wounds_2014, healing_word_2014
from app.content.druid_2014_level1_spells import faerie_fire_2014, longstrider_2014, poison_spray_2014, produce_flame_2014
from app.content.druid_2014_level2_spells import barkskin_2014
from app.content.shared_spells_2014 import lesser_restoration_2014
from app.content.shared_movement_spells_2014 import freedom_of_movement_2014
from app.content.shared_effect_removal_spells_2014 import dispel_magic_2014
from app.content.druid_2014_progression import druid_2014_level
from app.content.druid_2014_wild_shape import wild_shape_action_2014
from app.content.druid_land_2014_level10 import (
    natures_ward_condition_immunities_2014,
    natures_ward_debuff_counters_2014,
)
from app.content.druid_land_2014_profile import build_thalen_greenbough_2014_profile
from app.content.weapon_catalog import build_weapon
from app.domain.debuffs import DebuffCounter
from app.domain.models import CombatantTemplate, DamageType, ResourceDefinition, VisualLoadout, WeaponAttack
from app.domain.progression import PassiveDebuffCounterGrant, ProgressionCombatFeatures, SavingThrowAdvantageGrant

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
    resources = [
        ResourceDefinition(
            id=f"spell-slot-{spell_level}",
            name=f"Spell Slot {spell_level}",
            max_uses=uses,
        )
        for spell_level, uses in enumerate(row.spell_slots, start=1)
        if uses
    ]
    if level >= 2 and not row.wild_shape_unlimited:
        resources.append(ResourceDefinition(
            id="wild-shape",
            name="Wild Shape",
            max_uses=row.wild_shape_uses,
        ))
    return resources


def build_thalen_greenbough_2014(level: int) -> CombatantTemplate:
    try:
        if level not in range(1, 12):
            raise ValueError("2014 Land Druid runtime currently covers levels 1 through 11.")
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
            spell_save_actions=[
                poison_spray_2014(save_dc, level),
                *([faerie_fire_2014(save_dc)] if level >= 2 else []),
            ],
            defensive_spell_actions=[
                longstrider_2014(),
                *([barkskin_2014()] if level >= 3 else []),
                *([freedom_of_movement_2014()] if level >= 7 else []),
            ],
            condition_removal_actions=(
                [lesser_restoration_2014()] if level >= 3 else []
            ),
            effect_removal_actions=(
                [dispel_magic_2014("wisdom")] if level >= 5 else []
            ),
            healing_actions=[
                healing_word_2014(wisdom_modifier, 0),
                cure_wounds_2014(wisdom_modifier, 0),
            ],
            replacement_form_actions=(
                [wild_shape_action_2014(level)] if level >= 2 else []
            ),
            passive_modifier_grants=(
                natures_ward_condition_immunities_2014() if level >= 10 else []
            ),
            damage_immunities=[DamageType.POISON] if level >= 10 else [],
            progression_features=ProgressionCombatFeatures(
                saving_throw_advantage_grants=[
                    SavingThrowAdvantageGrant(
                        source_id="fey-ancestry",
                        source_name="Fey Ancestry",
                        abilities=_ABILITIES,
                        required_effect_tags=["charm"],
                    ),
                    *([
                        SavingThrowAdvantageGrant(
                            source_id="lands-stride",
                            source_name="Land's Stride",
                            abilities=_ABILITIES,
                            requires_magical_effect=True,
                            required_effect_tags=["plant-impediment"],
                        )
                    ] if level >= 6 else []),
                ],
                passive_debuff_counter_grants=[
                    *([
                        PassiveDebuffCounterGrant(
                            source_id="lands-stride",
                            source_name="Land's Stride",
                            counter=DebuffCounter(
                                debuff_id="difficult-terrain",
                                source_scope="nonmagical",
                            ),
                        )
                    ] if level >= 6 else []),
                    *(natures_ward_debuff_counters_2014() if level >= 10 else []),
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
