from __future__ import annotations

import logging

from app.content.canonical_hero_policy import canonical_template_id
from app.content.paladin_devotion_2024_build_support import build_paladin_2024_ability_progression
from app.content.hero_progressions import HERO_BY_CLASS
from app.content.paladin_devotion_2024_feature_audits import build_paladin_2024_feature_audits
from app.content.paladin_devotion_2024_profile_support import paladin_2024_source_references
from app.domain.character_builds import CharacterBuildProfile

logger = logging.getLogger(__name__)


def build_aurelia_brightshield_2024_profile(level: int = 1) -> CharacterBuildProfile:
    """Compile Aurelia's legal 2024 Devotion Paladin progression through level 17."""
    try:
        if level not in range(1, 18):
            raise ValueError("The current 2024 Paladin profile tranche supports levels 1-17 only.")
        hero = HERO_BY_CLASS["paladin"]
        base, allowed, background, advancement, final = (
            build_paladin_2024_ability_progression(level)
        )

        audits = build_paladin_2024_feature_audits(level)

        return CharacterBuildProfile(
            id=f"build-aurelia-brightshield-2024-l{level}",
            template_id=canonical_template_id("paladin", level),
            character_name=hero.hero_name, class_id="paladin", class_name=hero.class_name,
            level=level, ruleset="2024", build_id="devotion-sword-shield",
            subclass_id="oath-devotion" if level >= 3 else None,
            subclass_name="Oath of Devotion" if level >= 3 else None,
            species_id="human", species_name="Human",
            background_id="soldier", background_name="Soldier",
            origin_feat_id="savage-attacker", origin_feat_name="Savage Attacker",
            base_ability_scores=base, background_allowed_abilities=allowed,
            background_increases=background, advancement_increases=advancement,
            final_ability_scores=final,
            class_equipment_option="package",
            class_equipment=[
                "Chain Mail", "Shield", "Longsword", "6 Javelins",
                "Holy Symbol", "Priest's Pack", "9 GP",
            ],
            background_equipment_option="package",
            background_equipment=[
                "Spear", "Shortbow", "20 Arrows", "Gaming Set", "Healer's Kit",
                "Quiver", "Traveler's Clothes", "14 GP",
            ],
            skill_proficiencies=[
                "Athletics", "Intimidation", "Insight", "Persuasion",
                "Perception", "Acrobatics", "Medicine", "Religion",
            ],
            weapon_masteries=["longsword", "javelin"],
            fighting_style="Defense" if level >= 2 else None,
            fighting_styles=["Defense"] if level >= 2 else [],
            combat_loadout_kind="one-hander-shield",
            feature_audits=audits,
            source_references=paladin_2024_source_references(level),
        )
    except Exception:
        logger.exception("Failed to compile 2024 Aurelia Brightshield profile at level %s.", level)
        raise
