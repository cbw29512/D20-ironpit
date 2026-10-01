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
    notes: str | None = None,
) -> FeatureAudit:
    try:
        return FeatureAudit(
            feature_id=feature_id,
            feature_name=feature_name,
            source_reference="D&D Beyond Basic Rules 2024",
            category=category,
            combat_relevant=True,
            automated=True,
            notes=notes,
        )
    except Exception:
        logger.exception("Failed to build 2024 Monk feature audit for %s.", feature_id)
        raise


def build_kael_stillwater_2024_profile(level: int = 1) -> CharacterBuildProfile:
    """Compile the legal level-1 2024 Kael foundation for the unarmed-offense build."""
    try:
        if level != 1:
            raise ValueError("The current 2024 Monk profile tranche supports level 1 only.")
        hero = HERO_BY_CLASS["monk"]
        base = canonical_base_ability_scores("monk")
        background_allowed = ["dexterity", "constitution", "intelligence"]
        background = canonical_background_increases("monk", background_allowed)
        values = base.model_dump()
        for increase in background:
            values[increase.ability] += increase.amount
        final = type(base)(**values)
        return CharacterBuildProfile(
            id="build-kael-stillwater-2024-l1",
            template_id=canonical_template_id("monk", 1),
            character_name=hero.hero_name,
            class_id="monk",
            class_name=hero.class_name,
            level=1,
            ruleset="2024",
            build_id="unarmed-offense",
            species_id="orc",
            species_name="Orc",
            background_id="criminal",
            background_name="Criminal",
            origin_feat_id="alert",
            origin_feat_name="Alert",
            base_ability_scores=base,
            background_allowed_abilities=background_allowed,
            background_increases=background,
            final_ability_scores=final,
            class_equipment_option="package",
            class_equipment=[
                "Spear", "5 Daggers", "Artisan's Tools", "Explorer's Pack", "11 GP",
            ],
            background_equipment_option="package",
            background_equipment=[
                "2 Daggers", "Thieves' Tools", "Crowbar", "2 Pouches", "Traveler's Clothes", "16 GP",
            ],
            skill_proficiencies=["Sleight of Hand", "Stealth", "Acrobatics", "Insight"],
            weapon_masteries=[],
            combat_loadout_kind="unarmed",
            feature_audits=[
                _feature(
                    "martial-arts",
                    "Martial Arts",
                    "class",
                    notes="Uses the shared Bonus Action attack grant; no Attack action prerequisite is imposed.",
                ),
                _feature("unarmored-defense", "Unarmored Defense", "class"),
                _feature(
                    "alert",
                    "Alert",
                    "feat",
                    notes="Adds Proficiency Bonus to Initiative; the optional ally initiative swap is declined by arena policy.",
                ),
                _feature("adrenaline-rush", "Adrenaline Rush", "species"),
                _feature("relentless-endurance", "Relentless Endurance", "species"),
                _feature("unarmed-strike", "Unarmed Strike", "equipment"),
            ],
            source_references=[
                "Basic Rules 2024: Monk — Core Traits and Level 1 Martial Arts",
                "Basic Rules 2024: Character Origins — Criminal and Orc",
                "Basic Rules 2024: Feats — Alert",
            ],
        )
    except Exception:
        logger.exception("Failed to compile 2024 Kael Stillwater profile at level %s.", level)
        raise
