from __future__ import annotations

import logging

from app.content.ranger_hunter_2014_audits import build_ranger_hunter_2014_feature_audits
from app.content.ranger_hunter_2014_data import ASI_CHOICES, BASE_SCORES, HUMAN_INCREASES, ability_scores
from app.domain.character_builds import AbilityIncrease, CharacterBuildProfile

logger = logging.getLogger(__name__)


def _increases(rows) -> list[AbilityIncrease]:
    return [AbilityIncrease(ability=ability, amount=amount) for ability, amount in rows]


def build_rowan_ashtrail_2014_profile(level: int) -> CharacterBuildProfile:
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Rowan profile covers levels 1 through 20.")
        return CharacterBuildProfile(
            id=f"build-rowan-ashtrail-2014-l{level}",
            template_id=f"rowan-ashtrail-2014-l{level}",
            character_name="Rowan Ashtrail", class_id="ranger", class_name="Ranger",
            level=level, ruleset="2014",
            subclass_id="hunter" if level >= 3 else None,
            subclass_name="Hunter" if level >= 3 else None,
            build_id="hunter-archer",
            species_id="human", species_name="Human",
            background_id="outlander", background_name="Outlander",
            base_ability_scores=BASE_SCORES,
            species_increases=_increases(HUMAN_INCREASES.items()),
            advancement_increases=_increases(
                (ability, amount) for required, ability, amount in ASI_CHOICES if level >= required
            ),
            final_ability_scores=ability_scores(level),
            class_equipment_option="package",
            class_equipment=[
                "Scale Mail", "2 Shortswords", "Explorer's Pack", "Longbow", "20 Arrows",
            ],
            background_equipment_option="package",
            background_equipment=["Staff", "Hunting Trap", "Traveler's Clothes", "Pouch", "10 gp"],
            skill_proficiencies=["Athletics", "Investigation", "Perception", "Stealth", "Survival"],
            weapon_masteries=[],
            fighting_style="Archery" if level >= 2 else None,
            fighting_styles=["Archery"] if level >= 2 else [],
            combat_loadout_kind="ranged",
            feature_audits=build_ranger_hunter_2014_feature_audits(level),
            source_references=[
                "D&D Basic Rules 2014: Human, Outlander, Equipment",
                "D&D SRD 5.1 (2014): Ranger",
                "D&D SRD 5.1 (2014): Hunter",
            ],
        )
    except Exception:
        logger.exception("Failed to compile 2014 Rowan Ashtrail profile at level %s.", level)
        raise
