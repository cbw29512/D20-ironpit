from __future__ import annotations

import logging

from app.content.canonical_combat_build_policy import (
    canonical_background_increases,
    canonical_base_ability_scores,
)
from app.content.canonical_hero_policy import canonical_template_id
from app.content.hero_progressions import HERO_BY_CLASS
from app.content.sorcerer_draconic_2024_audits import build_nyra_draconic_2024_audits
from app.domain.character_builds import AbilityIncrease, AbilityScores, CharacterBuildProfile

logger = logging.getLogger(__name__)


def build_nyra_emberveil_2024_profile(level: int) -> CharacterBuildProfile:
    try:
        if level not in range(1, 21):
            raise ValueError("2024 Nyra profile currently certifies levels 1 through 20.")
        hero = HERO_BY_CLASS["sorcerer"]
        base = canonical_base_ability_scores("sorcerer")
        background_allowed = ["intelligence", "wisdom", "charisma"]
        background = canonical_background_increases("sorcerer", background_allowed)
        advancement: list[AbilityIncrease] = []
        if level >= 4:
            advancement.append(AbilityIncrease(ability="charisma", amount=2))
        if level >= 8:
            advancement.extend([
                AbilityIncrease(ability="charisma", amount=1),
                AbilityIncrease(ability="wisdom", amount=1),
            ])
        if level >= 12:
            advancement.append(AbilityIncrease(ability="wisdom", amount=2))
        if level >= 16:
            advancement.append(AbilityIncrease(ability="wisdom", amount=2))
        if level >= 19:
            advancement.append(AbilityIncrease(ability="intelligence", amount=1))
        values = base.model_dump()
        for increase in [*background, *advancement]:
            values[increase.ability] += increase.amount
        final = AbilityScores(**values)
        return CharacterBuildProfile(
            id=f"build-nyra-emberveil-2024-l{level}",
            template_id=canonical_template_id("sorcerer", level),
            character_name=hero.hero_name,
            class_id="sorcerer",
            class_name=hero.class_name,
            level=level,
            ruleset="2024",
            subclass_id="draconic-sorcery" if level >= 3 else None,
            subclass_name="Draconic Sorcery" if level >= 3 else None,
            build_id="fire-damage",
            species_id="human",
            species_name="Human",
            background_id="acolyte",
            background_name="Acolyte",
            origin_feat_id="magic-initiate-cleric",
            origin_feat_name="Magic Initiate (Cleric)",
            base_ability_scores=base,
            background_allowed_abilities=background_allowed,
            background_increases=background,
            advancement_increases=advancement,
            final_ability_scores=final,
            class_equipment_option="package",
            class_equipment=["Spear", "Dagger", "Dagger", "Arcane Focus", "Dungeoneer's Pack"],
            background_equipment_option="package",
            background_equipment=["Calligrapher's Supplies", "Book", "Holy Symbol", "Parchment", "Robe", "8 GP"],
            skill_proficiencies=[
                "Arcana", "Persuasion", "Insight", "Religion",
                "Deception", "Intimidation", "Investigation", "History",
            ],
            weapon_masteries=[],
            combat_loadout_kind=None,
            feature_audits=build_nyra_draconic_2024_audits(level),
            source_references=[
                "D&D Beyond Basic Rules 2024: Sorcerer",
                "D&D Beyond Basic Rules 2024: Draconic Sorcery",
                "D&D Beyond Basic Rules 2024: Human",
                "D&D Beyond Basic Rules 2024: Acolyte",
                "D&D Beyond Basic Rules 2024: Fire Bolt; Burning Hands; Chromatic Orb",
                "D&D Beyond Basic Rules 2024: Equipment",
            ],
        )
    except Exception:
        logger.exception("Failed to compile 2024 Nyra Emberveil profile at level %s.", level)
        raise
