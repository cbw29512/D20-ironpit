from __future__ import annotations

import logging

from app.content.canonical_combat_build_policy import (
    canonical_background_increases,
    canonical_base_ability_scores,
)
from app.content.canonical_hero_policy import canonical_template_id
from app.content.hero_progressions import HERO_BY_CLASS
from app.content.druid_2024_profile_features import build_druid_2024_feature_audits
from app.domain.character_builds import CharacterBuildProfile

logger = logging.getLogger(__name__)


def build_thalen_greenbough_profile(level: int = 1) -> CharacterBuildProfile:
    """Compile Thalen's 2024 Druid foundation without early subclass leakage."""
    try:
        if level not in {1, 2}:
            raise ValueError("2024 Thalen profile currently certifies Druid levels 1 through 2.")
        hero = HERO_BY_CLASS["druid"]
        base = canonical_base_ability_scores("druid")
        background_allowed = ["intelligence", "wisdom", "charisma"]
        background = canonical_background_increases("druid", background_allowed)
        values = base.model_dump()
        for increase in background:
            values[increase.ability] += increase.amount
        final = type(base)(**values)
        return CharacterBuildProfile(
            id=f"build-thalen-greenbough-l{level}",
            template_id=canonical_template_id("druid", level),
            character_name=hero.hero_name,
            class_id="druid",
            class_name=hero.class_name,
            level=level,
            ruleset="2024",
            subclass_id=None,
            subclass_name=None,
            build_id="land-damage",
            species_id="wood-elf",
            species_name="Wood Elf",
            background_id="acolyte",
            background_name="Acolyte",
            origin_feat_id="magic-initiate-cleric",
            origin_feat_name="Magic Initiate (Cleric)",
            base_ability_scores=base,
            background_allowed_abilities=background_allowed,
            background_increases=background,
            advancement_increases=[],
            final_ability_scores=final,
            class_equipment_option="package",
            class_equipment=[
                "Leather Armor", "Shield", "Sickle", "Druidic Focus (Quarterstaff)",
                "Explorer's Pack", "Herbalism Kit", "9 GP",
            ],
            background_equipment_option="package",
            background_equipment=[
                "Calligrapher's Supplies", "Book (prayers)", "Holy Symbol",
                "Parchment (10 sheets)", "Robe", "8 GP",
            ],
            skill_proficiencies=["Nature", "Survival", "Insight", "Religion", "Perception"],
            weapon_masteries=[],
            combat_loadout_kind=None,
            feature_audits=build_druid_2024_feature_audits(level),
            source_references=[
                "D&D Beyond Basic Rules 2024: Druid — Core Traits, Spellcasting, Druidic, Primal Order",
                "D&D Beyond Basic Rules 2024: Character Origins — Elf (Wood Elf), Acolyte",
                "D&D Beyond Basic Rules 2024: Feats — Magic Initiate",
                "D&D Beyond Basic Rules 2024: Equipment — Leather Armor, Shield, Sickle",
                "D&D Beyond Basic Rules 2024: Spells — Poison Spray, Healing Word, Cure Wounds, Longstrider, Faerie Fire",
                "D&D Beyond Basic Rules 2024: Druid 2 — Wild Shape, Wild Companion",
            ],
        )
    except Exception:
        logger.exception("Failed to compile 2024 Thalen Greenbough profile at level %s.", level)
        raise
