from __future__ import annotations

import logging

from app.content.wizard_evoker_2014_audits import build_wizard_evoker_2014_feature_audits
from app.content.wizard_evoker_2014_data import ASI_CHOICES, BASE_SCORES, HUMAN_INCREASES, ability_scores
from app.domain.character_builds import AbilityIncrease, CharacterBuildProfile

logger = logging.getLogger(__name__)


def _increases(rows) -> list[AbilityIncrease]:
    try:
        return [AbilityIncrease(ability=ability, amount=amount) for ability, amount in rows]
    except Exception:
        logger.exception("Failed to compile Elian ability increases.")
        raise


def build_elian_starweaver_2014_profile(level: int) -> CharacterBuildProfile:
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Elian profile covers levels 1 through 20.")
        return CharacterBuildProfile(
            id=f"build-elian-starweaver-2014-l{level}",
            template_id=f"elian-starweaver-2014-l{level}",
            character_name="Elian Starweaver",
            class_id="wizard",
            class_name="Wizard",
            level=level,
            ruleset="2014",
            subclass_id="evoker" if level >= 2 else None,
            subclass_name="School of Evocation" if level >= 2 else None,
            build_id="evoker-fire-caster",
            species_id="human",
            species_name="Human",
            background_id="sage",
            background_name="Sage",
            base_ability_scores=BASE_SCORES,
            species_increases=_increases(HUMAN_INCREASES.items()),
            advancement_increases=_increases(
                (ability, amount) for required, ability, amount in ASI_CHOICES if level >= required
            ),
            final_ability_scores=ability_scores(level),
            class_equipment_option="package",
            class_equipment=["Light Crossbow", "20 Bolts", "Arcane Focus", "Scholar's Pack", "Spellbook"],
            background_equipment_option="package",
            background_equipment=["Bottle of Ink", "Quill", "Small Knife", "Letter", "Common Clothes", "10 gp"],
            skill_proficiencies=["Arcana", "History", "Insight", "Investigation"],
            weapon_masteries=[],
            combat_loadout_kind=None,
            feature_audits=build_wizard_evoker_2014_feature_audits(level),
            source_references=[
                "D&D Basic Rules 2014: Human, Sage, Equipment",
                "D&D SRD 5.1 (2014): Wizard",
                "D&D SRD 5.1 (2014): School of Evocation",
            ],
        )
    except Exception:
        logger.exception("Failed to compile 2014 Elian Starweaver profile at level %s.", level)
        raise
