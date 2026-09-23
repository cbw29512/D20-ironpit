from __future__ import annotations

import logging

from app.content.cleric_life_2014_feature_audits import feature_audits_2014
from app.content.cleric_life_2014_progression import (
    advancement_increases_2014, base_scores_2014, final_scores_2014, species_increases_2014,
)
from app.domain.character_builds import CharacterBuildProfile

logger = logging.getLogger(__name__)


def build_seraphine_dawnshield_2014_profile(level: int) -> CharacterBuildProfile:
    """One persistent 2014 Seraphine; each level is previous state plus its legal delta."""
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Seraphine profile covers levels 1 through 20.")
        return CharacterBuildProfile(
            id=f"build-seraphine-dawnshield-2014-l{level}",
            template_id=f"seraphine-dawnshield-2014-l{level}",
            character_name="Seraphine Dawnshield",
            class_id="cleric", class_name="Cleric", level=level, ruleset="2014",
            subclass_id="life-domain", subclass_name="Life Domain", build_id="life-healer",
            species_id="hill-dwarf", species_name="Hill Dwarf",
            background_id="acolyte", background_name="Acolyte",
            base_ability_scores=base_scores_2014(),
            species_increases=species_increases_2014(),
            advancement_increases=advancement_increases_2014(level),
            final_ability_scores=final_scores_2014(level),
            class_equipment_option="package",
            class_equipment=[
                "Warhammer", "Scale Mail", "Light Crossbow", "20 Bolts",
                "Priest's Pack", "Shield", "Holy Symbol",
            ],
            background_equipment_option="package",
            background_equipment=[
                "Holy Symbol", "Prayer Book", "5 Sticks of Incense",
                "Vestments", "Common Clothes", "15 gp",
            ],
            skill_proficiencies=["Insight", "Religion", "Medicine", "Persuasion"],
            weapon_masteries=[], combat_loadout_kind=None,
            feature_audits=feature_audits_2014(level),
            source_references=[
                "D&D Basic Rules 2014: Hill Dwarf", "D&D Basic Rules 2014: Acolyte",
                "D&D Basic Rules 2014: Cleric", "D&D Basic Rules 2014: Life Domain",
                "D&D Basic Rules 2014: Equipment",
            ],
        )
    except Exception:
        logger.exception("Failed to compile 2014 Seraphine Dawnshield profile at level %s", level)
        raise
