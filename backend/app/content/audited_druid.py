from __future__ import annotations

import logging

from app.content.armor_catalog import get_armor
from app.content.armor_class_rules import compile_worn_armor_class
from app.content.audited_druid_profile import build_thalen_greenbough_profile
from app.content.character_math import saving_throw_bonuses
from app.content.druid_2024_sources import druid_runtime_source_reference
from app.content.druid_2024_runtime_support import (
    druid_actions,
    druid_resources,
    natural_recovery_alternate_casts,
    wild_shape_actions,
)
from app.content.druid_combat_levels import DRUID_COMBAT_LEVELS
from app.content.weapon_catalog import build_weapon
from app.domain.models import CombatantTemplate, DamageType, VisualLoadout, WeaponAttack
from app.domain.progression import ProgressionCombatFeatures, SavingThrowAdvantageGrant

logger = logging.getLogger(__name__)
_ABILITIES = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]


def _sickle(proficiency_bonus: int, strength_modifier: int) -> WeaponAttack:
    weapon = build_weapon("sickle").model_copy(update={"mastery_property": None})
    return WeaponAttack(
        id="thalen-sickle",
        weapon=weapon,
        attack_bonus=proficiency_bonus + strength_modifier,
        damage_bonus=strength_modifier,
        attack_ability="strength",
        attack_ability_modifier=strength_modifier,
    )


def build_thalen_greenbough_level(level: int) -> CombatantTemplate:
    """Compile the certified 2024 Land-Druid progression."""
    try:
        if level not in {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15}:
            raise ValueError("2024 Thalen runtime currently supports Druid levels 1 through 15.")
        profile = build_thalen_greenbough_profile(level)
        row = DRUID_COMBAT_LEVELS[level]
        scores = profile.final_ability_scores
        wisdom_modifier = scores.modifier("wisdom")
        pb = row.proficiency_bonus
        armor = get_armor("leather")
        armor_class = compile_worn_armor_class(
            armor.base_ac,
            armor.category,
            scores.modifier("dexterity"),
            [],
            wielding_shield=True,
            shield_trained=True,
        )
        if armor_class != row.armor_class:
            raise ValueError(
                f"2024 Druid level {level} AC drifted: compiled {armor_class}, spine {row.armor_class}."
            )
        return CombatantTemplate(
            id=profile.template_id,
            name=profile.character_name,
            archetype="Druid",
            level=level,
            kind="character",
            ruleset="2024",
            creature_type="Humanoid",
            ability_scores=scores,
            armor_class=armor_class,
            max_hp=row.max_hp,
            speed_ft=35,
            initiative_bonus=scores.modifier("dexterity"),
            weapon_attack=_sickle(pb, scores.modifier("strength")),
            **druid_actions(level, pb, wisdom_modifier),
            progression_features=ProgressionCombatFeatures(
                saving_throw_advantage_grants=[
                    SavingThrowAdvantageGrant(
                        source_id="fey-ancestry",
                        source_name="Fey Ancestry",
                        abilities=_ABILITIES,
                        required_effect_tags=["charm"],
                    ),
                ],
                alternate_spell_cast_grants=natural_recovery_alternate_casts(level),
            ),
            saving_throw_bonuses=saving_throw_bonuses(
                scores, level, ("intelligence", "wisdom"),
            ),
            skill_bonuses={
                "athletics": scores.modifier("strength"),
                "acrobatics": scores.modifier("dexterity"),
                "nature": scores.modifier("intelligence") + pb + wisdom_modifier,
                "survival": wisdom_modifier + pb,
                "insight": wisdom_modifier + pb,
                "religion": scores.modifier("intelligence") + pb,
                "perception": wisdom_modifier + pb,
            },
            resources=druid_resources(level, row.spell_slots, row.wild_shape_uses),
            replacement_form_actions=wild_shape_actions(level),
            damage_resistances=[DamageType.FIRE] if level >= 10 else [],
            condition_immunities=["poisoned"] if level >= 10 else [],
            weapon_masteries=[],
            visual=VisualLoadout(
                armor="leather",
                main_hand="sickle",
                off_hand="wooden-shield",
                body_style="humanoid",
            ),
            source=druid_runtime_source_reference(level),
        )
    except Exception:
        logger.exception("Failed to compile 2024 Thalen Greenbough at Druid level %s.", level)
        raise
