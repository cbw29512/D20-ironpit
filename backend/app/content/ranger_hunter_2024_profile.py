from __future__ import annotations

import logging

from app.content.canonical_combat_build_policy import (
    canonical_background_increases,
    canonical_base_ability_scores,
)
from app.content.canonical_hero_policy import canonical_template_id
from app.content.hero_progressions import HERO_BY_CLASS
from app.content.ranger_hunter_2024_level1 import build_ranger_2024_level1_audits
from app.domain.character_builds import CharacterBuildProfile

logger = logging.getLogger(__name__)


def build_rowan_ashtrail_2024_profile(level: int = 1) -> CharacterBuildProfile:
    """Convert persistent 2014 Rowan Ashtrail into the audited 2024 Ranger track."""
    try:
        if level != 1:
            raise ValueError("The current 2024 Ranger conversion tranche certifies level 1 only.")
        hero = HERO_BY_CLASS["ranger"]
        base = canonical_base_ability_scores("ranger")
        # Outlander is retained from Rowan's 2014 identity. Under the 2024
        # legacy-background conversion rule its ability increases are flexible.
        allowed = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        background = canonical_background_increases("ranger", allowed)
        values = base.model_dump()
        for increase in background:
            values[increase.ability] += increase.amount
        final = type(base)(**values)
        return CharacterBuildProfile(
            id="build-rowan-ashtrail-2024-l1",
            template_id=canonical_template_id("ranger", 1),
            character_name=hero.hero_name,
            class_id="ranger",
            class_name=hero.class_name,
            level=1,
            ruleset="2024",
            build_id="archer",
            subclass_id=None,
            subclass_name=None,
            species_id="wood-elf",
            species_name="Wood Elf",
            background_id="outlander",
            background_name="Outlander",
            origin_feat_id="alert",
            origin_feat_name="Alert",
            base_ability_scores=base,
            background_allowed_abilities=allowed,
            background_increases=background,
            advancement_increases=[],
            final_ability_scores=final,
            class_equipment_option="package",
            class_equipment=[
                "Studded Leather Armor", "Scimitar", "Shortsword", "Longbow",
                "20 Arrows", "Quiver", "Druidic Focus", "Explorer's Pack", "7 GP",
            ],
            background_equipment_option="package",
            background_equipment=[
                "Staff", "Hunting Trap", "Traveler's Clothes", "10 GP",
            ],
            skill_proficiencies=[
                "Athletics", "Survival", "Perception", "Stealth", "Insight", "Investigation",
            ],
            weapon_masteries=["longbow", "shortsword"],
            combat_loadout_kind="dual-wield",
            feature_audits=build_ranger_2024_level1_audits(),
            source_references=[
                "D&D Beyond Basic Rules 2024: Ranger 1",
                "D&D Beyond Basic Rules 2024: Elf — Wood Elf",
                "D&D Beyond Basic Rules 2024: Backgrounds and Species from Older Books",
                "D&D Beyond Basic Rules 2014: Outlander",
            ],
        )
    except Exception:
        logger.exception("Failed to compile 2024 Rowan Ashtrail profile at level %s.", level)
        raise
