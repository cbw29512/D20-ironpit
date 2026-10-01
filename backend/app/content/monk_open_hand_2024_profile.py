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
    combat_relevant: bool = True,
    notes: str | None = None,
) -> FeatureAudit:
    try:
        return FeatureAudit(
            feature_id=feature_id,
            feature_name=feature_name,
            source_reference="D&D Beyond Basic Rules 2024",
            category=category,
            combat_relevant=combat_relevant,
            automated=True,
            notes=notes,
        )
    except Exception:
        logger.exception("Failed to build 2024 Monk feature audit for %s.", feature_id)
        raise


def build_kael_stillwater_2024_profile(level: int = 1) -> CharacterBuildProfile:
    """Compile the legal 2024 Kael progression through the currently supported level."""
    try:
        if level not in {1, 2}:
            raise ValueError("The current 2024 Monk profile tranche supports levels 1-2 only.")
        hero = HERO_BY_CLASS["monk"]
        base = canonical_base_ability_scores("monk")
        background_allowed = ["dexterity", "constitution", "intelligence"]
        background = canonical_background_increases("monk", background_allowed)
        values = base.model_dump()
        for increase in background:
            values[increase.ability] += increase.amount
        final = type(base)(**values)
        return CharacterBuildProfile(
            id=f"build-kael-stillwater-2024-l{level}",
            template_id=canonical_template_id("monk", level),
            character_name=hero.hero_name,
            class_id="monk",
            class_name=hero.class_name,
            level=level,
            ruleset="2024",
            build_id="unarmed-offense",
            species_id="human",
            species_name="Human",
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
                "Spear", "5 Daggers", "Woodcarver's Tools", "Explorer's Pack", "11 GP",
            ],
            background_equipment_option="package",
            background_equipment=[
                "2 Daggers", "Thieves' Tools", "Crowbar", "2 Pouches", "Traveler's Clothes", "16 GP",
            ],
            skill_proficiencies=[
                "Sleight of Hand", "Stealth", "Acrobatics", "Insight",
                "Perception", "History", "Nature", "Religion",
            ],
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
                *(
                    [
                        _feature(
                            "monks-focus",
                            "Monk's Focus",
                            "class",
                            notes="Focus Points fuel Flurry of Blows, Patient Defense, and Step of the Wind through shared resource/action primitives.",
                        ),
                        _feature(
                            "unarmored-movement",
                            "Unarmored Movement",
                            "class",
                            notes="Adds 10 feet to Speed while unarmored and not wielding a Shield.",
                        ),
                        _feature(
                            "uncanny-metabolism",
                            "Uncanny Metabolism",
                            "class",
                            notes="On Initiative, once per Long Rest, restores expended Focus Points and heals Monk level + one Martial Arts die.",
                        ),
                    ]
                    if level >= 2 else []
                ),
                _feature(
                    "alert",
                    "Alert",
                    "feat",
                    notes="Adds Proficiency Bonus to Initiative; the optional ally initiative swap is declined by arena policy.",
                ),
                _feature(
                    "resourceful",
                    "Resourceful",
                    "species",
                    notes="Fresh-rest arena initialization starts Kael with Heroic Inspiration.",
                ),
                _feature(
                    "skillful",
                    "Skillful",
                    "species",
                    combat_relevant=False,
                    notes="Perception proficiency selected.",
                ),
                _feature(
                    "versatile",
                    "Versatile",
                    "species",
                    combat_relevant=False,
                    notes="Recommended Skilled Origin feat selected.",
                ),
                _feature(
                    "skilled",
                    "Skilled",
                    "feat",
                    combat_relevant=False,
                    notes="History, Nature, and Religion proficiencies selected.",
                ),
                _feature("unarmed-strike", "Unarmed Strike", "equipment"),
            ],
            source_references=[
                "Basic Rules 2024: Monk — Core Traits, Martial Arts, Monk's Focus, Unarmored Movement, Uncanny Metabolism",
                "Basic Rules 2024: Character Origins — Criminal and Human",
                "Basic Rules 2024: Feats — Alert and Skilled",
            ],
        )
    except Exception:
        logger.exception("Failed to compile 2024 Kael Stillwater profile at level %s.", level)
        raise
