from __future__ import annotations

import logging

from app.content.druid_land_2014_audits import build_druid_land_2014_feature_audits
from app.content.druid_land_2014_data import ASI_CHOICES, BASE_SCORES, HUMAN_INCREASES, ability_scores
from app.domain.character_builds import AbilityIncrease, CharacterBuildProfile

logger = logging.getLogger(__name__)


def _increases(rows) -> list[AbilityIncrease]:
    try:
        return [AbilityIncrease(ability=ability, amount=amount) for ability, amount in rows]
    except Exception:
        logger.exception("Failed to compile Thalen ability increases.")
        raise


def build_thalen_greenbough_2014_profile(level: int) -> CharacterBuildProfile:
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Thalen profile covers levels 1 through 20.")
        return CharacterBuildProfile(
            id=f"build-thalen-greenbough-2014-l{level}",
            template_id=f"thalen-greenbough-2014-l{level}",
            character_name="Thalen Greenbough",
            class_id="druid",
            class_name="Druid",
            level=level,
            ruleset="2014",
            subclass_id="circle-land" if level >= 2 else None,
            subclass_name="Circle of the Land" if level >= 2 else None,
            build_id="land-caster",
            species_id="human",
            species_name="Human",
            background_id="hermit",
            background_name="Hermit",
            base_ability_scores=BASE_SCORES,
            species_increases=_increases(HUMAN_INCREASES.items()),
            advancement_increases=_increases(
                (ability, amount) for required, ability, amount in ASI_CHOICES if level >= required
            ),
            final_ability_scores=ability_scores(level),
            class_equipment_option="package",
            class_equipment=["Wooden Shield", "Scimitar", "Leather Armor", "Explorer's Pack", "Druidic Focus"],
            background_equipment_option="package",
            background_equipment=["Scroll Case", "Winter Blanket", "Common Clothes", "Herbalism Kit", "5 gp"],
            skill_proficiencies=["Arcana", "Medicine", "Nature", "Perception"],
            weapon_masteries=[],
            combat_loadout_kind="one-hander-shield",
            feature_audits=build_druid_land_2014_feature_audits(level),
            source_references=[
                "D&D Basic Rules 2014: Human, Hermit, Equipment",
                "D&D SRD 5.1 (2014): Druid",
                "D&D SRD 5.1 (2014): Circle of the Land",
            ],
        )
    except Exception:
        logger.exception("Failed to compile 2014 Thalen Greenbough profile at level %s.", level)
        raise
