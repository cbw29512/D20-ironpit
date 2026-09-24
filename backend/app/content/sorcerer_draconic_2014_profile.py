from __future__ import annotations

import logging

from app.content.sorcerer_draconic_2014_audits import build_sorcerer_draconic_2014_feature_audits
from app.content.sorcerer_draconic_2014_data import ASI_CHOICES, BASE_SCORES, HUMAN_INCREASES, ability_scores
from app.domain.character_builds import AbilityIncrease, CharacterBuildProfile

logger = logging.getLogger(__name__)


def _increases(rows) -> list[AbilityIncrease]:
    return [AbilityIncrease(ability=ability, amount=amount) for ability, amount in rows]


def build_nyra_emberveil_2014_profile(level: int) -> CharacterBuildProfile:
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Nyra profile covers levels 1 through 20.")
        return CharacterBuildProfile(
            id=f"build-nyra-emberveil-2014-l{level}",
            template_id=f"nyra-emberveil-2014-l{level}",
            character_name="Nyra Emberveil", class_id="sorcerer", class_name="Sorcerer",
            level=level, ruleset="2014",
            subclass_id="draconic-bloodline", subclass_name="Draconic Bloodline",
            build_id="draconic-fire-caster",
            species_id="human", species_name="Human",
            background_id="hermit", background_name="Hermit",
            base_ability_scores=BASE_SCORES,
            species_increases=_increases(HUMAN_INCREASES.items()),
            advancement_increases=_increases(
                (ability, amount) for required, ability, amount in ASI_CHOICES if level >= required
            ),
            final_ability_scores=ability_scores(level),
            class_equipment_option="package",
            class_equipment=["Light Crossbow", "20 Bolts", "Arcane Focus", "Explorer's Pack", "2 Daggers"],
            background_equipment_option="package",
            background_equipment=["Scroll Case", "Winter Blanket", "Common Clothes", "Herbalism Kit", "5 gp"],
            skill_proficiencies=["Arcana", "Medicine", "Persuasion", "Religion"],
            weapon_masteries=[],
            combat_loadout_kind=None,
            feature_audits=build_sorcerer_draconic_2014_feature_audits(level),
            source_references=[
                "D&D Basic Rules 2014: Human, Hermit, Equipment",
                "D&D SRD 5.1 (2014): Sorcerer",
                "D&D SRD 5.1 (2014): Draconic Bloodline",
            ],
        )
    except Exception:
        logger.exception("Failed to compile 2014 Nyra Emberveil profile at level %s.", level)
        raise
