from __future__ import annotations

import logging

from app.content.armor_catalog import get_armor
from app.content.armor_class_rules import compile_worn_armor_class
from app.content.audited_bard_profile import build_lyra_silverstring_profile
from app.content.bard_2024_cutting_words import build_cutting_words_2024
from app.content.bard_2024_inspiration import build_bardic_inspiration_2024
from app.content.bard_2024_runtime_support import (
    bard_defensive_spells,
    bard_effect_removals,
    bard_progression_features,
    bard_resource_conversions,
    bard_resources,
    bard_spell_attacks,
    bard_spell_saves,
)
from app.content.bard_combat_levels import BARD_COMBAT_LEVELS
from app.content.character_math import saving_throw_bonuses
from app.content.healing_spell_effects import (
    build_cure_wounds,
    build_healing_word,
    build_mass_cure_wounds,
    build_mass_healing_word,
)
from app.content.hero_progressions import HERO_BY_CLASS
from app.content.weapon_catalog import build_weapon
from app.domain.models import CombatantTemplate, VisualLoadout, WeaponAttack
from app.domain.traits import CombatTrait

logger = logging.getLogger(__name__)


def _dagger(level: int, dexterity_modifier: int) -> WeaponAttack:
    try:
        weapon = build_weapon("dagger").model_copy(update={"mastery_property": None})
        proficiency_bonus = BARD_COMBAT_LEVELS[level].proficiency_bonus
        return WeaponAttack(
            id="lyra-dagger",
            weapon=weapon,
            attack_bonus=proficiency_bonus + dexterity_modifier,
            damage_bonus=dexterity_modifier,
            attack_ability="dexterity",
            attack_ability_modifier=dexterity_modifier,
        )
    except Exception:
        logger.exception("Failed to build Lyra's dagger attack at Bard level %s.", level)
        raise


def build_lyra_silverstring_level(level: int) -> CombatantTemplate:
    """Compile the 2024 support/healer Lore Bard through level 11."""
    try:
        if level not in {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11}:
            raise ValueError("2024 Lyra runtime currently supports Bard levels 1 through 11.")
        profile = build_lyra_silverstring_profile(level)
        row = BARD_COMBAT_LEVELS[level]
        scores = profile.final_ability_scores
        dexterity_modifier = scores.modifier("dexterity")
        wisdom_modifier = scores.modifier("wisdom")
        charisma_modifier = scores.modifier("charisma")
        armor = get_armor("studded-leather")
        armor_class = compile_worn_armor_class(
            armor.base_ac,
            armor.category,
            dexterity_modifier,
            [],
            wielding_shield=False,
            shield_trained=False,
        )
        proficiency_bonus = row.proficiency_bonus
        acrobatics_multiplier = 2 if level >= 2 else 1
        perception_multiplier = 2 if level >= 9 else 1
        performance_multiplier = 2 if level >= 9 else 1

        return CombatantTemplate(
            id=profile.template_id,
            name=HERO_BY_CLASS["bard"].hero_name,
            archetype="Bard",
            level=level,
            kind="character",
            ability_scores=scores,
            armor_class=armor_class,
            max_hp=row.max_hp,
            speed_ft=30,
            initiative_bonus=dexterity_modifier,
            weapon_attack=_dagger(level, dexterity_modifier),
            healing_actions=[
                build_healing_word(charisma_modifier),
                build_cure_wounds(charisma_modifier),
                *([build_mass_healing_word(charisma_modifier)] if level >= 5 else []),
                *([build_mass_cure_wounds(charisma_modifier)] if level >= 9 else []),
            ],
            d20_bonus_die_actions=[build_bardic_inspiration_2024(level)],
            reaction_roll_penalty_actions=(
                [build_cutting_words_2024(level)] if level >= 3 else []
            ),
            resource_conversion_actions=bard_resource_conversions(level),
            spell_save_actions=bard_spell_saves(
                level, 8 + proficiency_bonus + charisma_modifier,
            ),
            spell_attack_actions=bard_spell_attacks(
                level, proficiency_bonus + charisma_modifier,
            ),
            defensive_spell_actions=bard_defensive_spells(level),
            effect_removal_actions=bard_effect_removals(level),
            progression_features=bard_progression_features(level),
            saving_throw_bonuses=saving_throw_bonuses(scores, level, ("dexterity", "charisma")),
            skill_bonuses={
                "athletics": scores.modifier("strength"),
                "acrobatics": dexterity_modifier + proficiency_bonus * acrobatics_multiplier,
                "perception": wisdom_modifier + proficiency_bonus * perception_multiplier,
                "performance": charisma_modifier + proficiency_bonus * performance_multiplier,
                "insight": wisdom_modifier + proficiency_bonus,
                "religion": scores.modifier("intelligence") + proficiency_bonus,
            },
            combat_traits=[CombatTrait.ADRENALINE_RUSH, CombatTrait.RELENTLESS_ENDURANCE],
            resources=bard_resources(level, charisma_modifier),
            weapon_masteries=[],
            visual=VisualLoadout(
                armor=armor.id,
                main_hand="dagger",
                off_hand="lute",
                body_style="humanoid",
            ),
            source=(
                "D&D Beyond Basic Rules 2024: Bard, Acolyte, Orc, "
                "Bardic Inspiration, Healing Word, Cure Wounds, Equipment"
                + (
                    "; College of Lore, Magical Discoveries"
                    if level >= 6 else ""
                )
            ),
        )
    except Exception:
        logger.exception("Failed to compile 2024 Lyra Silverstring at level %s.", level)
        raise
