from __future__ import annotations

import logging

from app.content.warlock_fiend_2014_audits import build_warlock_fiend_2014_feature_audits
from app.content.warlock_fiend_2014_data import ASI_CHOICES, BASE_SCORES, HUMAN_INCREASES, ability_scores
from app.domain.character_builds import AbilityIncrease, CharacterBuildProfile

logger = logging.getLogger(__name__)


def _increases(rows) -> list[AbilityIncrease]:
    return [AbilityIncrease(ability=ability, amount=amount) for ability, amount in rows]


def build_varek_ashenmark_2014_profile(level: int) -> CharacterBuildProfile:
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Varek profile covers levels 1 through 20.")
        return CharacterBuildProfile(
            id=f"build-varek-ashenmark-2014-l{level}",
            template_id=f"varek-ashenmark-2014-l{level}",
            character_name="Varek Ashenmark", class_id="warlock", class_name="Warlock",
            level=level, ruleset="2014",
            subclass_id="fiend-patron", subclass_name="Fiend Patron",
            build_id="fiend-blaster",
            species_id="human", species_name="Human",
            background_id="charlatan", background_name="Charlatan",
            base_ability_scores=BASE_SCORES,
            species_increases=_increases(HUMAN_INCREASES.items()),
            advancement_increases=_increases(
                (ability, amount) for required, ability, amount in ASI_CHOICES if level >= required
            ),
            final_ability_scores=ability_scores(level),
            class_equipment_option="package",
            class_equipment=["Light Crossbow", "20 Bolts", "Arcane Focus", "Scholar's Pack", "Leather Armor", "2 Daggers"],
            background_equipment_option="package",
            background_equipment=["Fine Clothes", "Disguise Kit", "Con Tools", "15 gp"],
            skill_proficiencies=["Arcana", "Deception", "Intimidation", "Sleight of Hand"],
            weapon_masteries=[],
            combat_loadout_kind=None,
            feature_audits=build_warlock_fiend_2014_feature_audits(level),
            source_references=[
                "D&D Basic Rules 2014: Human, Charlatan, Equipment",
                "D&D SRD 5.1 (2014): Warlock",
                "D&D SRD 5.1 (2014): The Fiend",
            ],
        )
    except Exception:
        logger.exception("Failed to compile 2014 Varek Ashenmark profile at level %s.", level)
        raise
