from __future__ import annotations

import logging

from app.content.canonical_combat_build_policy import (
    canonical_background_increases,
    canonical_base_ability_scores,
)
from app.content.canonical_hero_policy import canonical_template_id
from app.content.hero_progressions import HERO_BY_CLASS
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit

logger = logging.getLogger(__name__)


def _feature(
    feature_id: str,
    feature_name: str,
    category: str,
    *,
    combat_relevant: bool,
    automated: bool,
    notes: str | None = None,
    runtime_attack_weapon_id: str | None = None,
) -> FeatureAudit:
    return FeatureAudit(
        feature_id=feature_id,
        feature_name=feature_name,
        source_reference="D&D Beyond Basic Rules 2024: Druid / Character Origins",
        category=category,
        combat_relevant=combat_relevant,
        automated=automated,
        notes=notes,
        runtime_attack_weapon_id=runtime_attack_weapon_id,
    )


def build_thalen_greenbough_profile(level: int = 1) -> CharacterBuildProfile:
    """Compile Thalen's 2024 Druid foundation without early subclass leakage."""
    try:
        if level != 1:
            raise ValueError("2024 Thalen profile currently certifies Druid level 1 only.")
        hero = HERO_BY_CLASS["druid"]
        base = canonical_base_ability_scores("druid")
        background_allowed = ["intelligence", "wisdom", "charisma"]
        background = canonical_background_increases("druid", background_allowed)
        values = base.model_dump()
        for increase in background:
            values[increase.ability] += increase.amount
        final = type(base)(**values)
        return CharacterBuildProfile(
            id="build-thalen-greenbough-l1",
            template_id=canonical_template_id("druid", 1),
            character_name=hero.hero_name,
            class_id="druid",
            class_name=hero.class_name,
            level=1,
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
            feature_audits=[
                _feature("spellcasting", "Spellcasting", "class", combat_relevant=True, automated=True),
                _feature(
                    "druidic", "Druidic", "class", combat_relevant=False, automated=True,
                    notes="Speak with Animals is always prepared but is arena-neutral.",
                ),
                _feature(
                    "primal-order-magician", "Primal Order: Magician", "class",
                    combat_relevant=False, automated=True,
                    notes=(
                        "Adds one Druid cantrip. The Wisdom-modifier bonus is assigned to Nature; "
                        "Nature checks are not used by the current automated arena."
                    ),
                ),
                _feature(
                    "fey-ancestry", "Fey Ancestry", "species",
                    combat_relevant=True, automated=True,
                    notes="Advantage on saves to avoid or end Charmed uses the universal save-advantage primitive.",
                ),
                _feature(
                    "wood-elf-lineage", "Elven Lineage: Wood Elf", "species",
                    combat_relevant=True, automated=True,
                    notes="Level 1 grants Speed 35 and Druidcraft; Druidcraft is arena-neutral.",
                ),
                _feature(
                    "keen-senses", "Keen Senses", "species",
                    combat_relevant=True, automated=True,
                    notes="Canonical proficiency choice is Perception.",
                ),
                _feature(
                    "darkvision", "Darkvision", "species",
                    combat_relevant=False, automated=False,
                    notes="Iron Pit assumes sufficient arena visibility.",
                ),
                _feature(
                    "trance", "Trance", "species",
                    combat_relevant=False, automated=False,
                    notes="Long-rest duration does not change a single Iron Pit match.",
                ),
                _feature(
                    "magic-initiate-cleric", "Magic Initiate (Cleric)", "feat",
                    combat_relevant=False, automated=False,
                    notes="Canonical choices are Light, Thaumaturgy, and Detect Magic; none alter arena combat.",
                ),
                _feature(
                    "sickle", "Sickle", "equipment", combat_relevant=True, automated=True,
                    runtime_attack_weapon_id="sickle",
                ),
                _feature(
                    "leather-shield", "Leather Armor and Shield",
                    "equipment", combat_relevant=True, automated=True,
                ),
            ],
            source_references=[
                "D&D Beyond Basic Rules 2024: Druid — Core Traits, Spellcasting, Druidic, Primal Order",
                "D&D Beyond Basic Rules 2024: Character Origins — Elf (Wood Elf), Acolyte",
                "D&D Beyond Basic Rules 2024: Feats — Magic Initiate",
                "D&D Beyond Basic Rules 2024: Equipment — Leather Armor, Shield, Sickle",
                "D&D Beyond Basic Rules 2024: Spells — Poison Spray, Healing Word, Cure Wounds, Longstrider",
            ],
        )
    except Exception:
        logger.exception("Failed to compile 2024 Thalen Greenbough profile at level %s.", level)
        raise
