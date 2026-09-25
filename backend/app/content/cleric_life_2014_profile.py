from __future__ import annotations

import logging

from app.content.canonical_progression import advance_profile_data
from app.content.cleric_life_2014_audits import build_cleric_life_2014_feature_audits
from app.domain.character_builds import AbilityIncrease, AbilityScores, CharacterBuildProfile

logger = logging.getLogger(__name__)


def _base_scores() -> AbilityScores:
    try:
        return AbilityScores(
            strength=13, dexterity=10, constitution=14,
            intelligence=8, wisdom=15, charisma=12,
        )
    except Exception:
        logger.exception("Failed to build Seraphine's 2014 base ability scores.")
        raise


def _species_increases() -> list[AbilityIncrease]:
    try:
        return [
            AbilityIncrease(ability="constitution", amount=2),
            AbilityIncrease(ability="wisdom", amount=1),
        ]
    except Exception:
        logger.exception("Failed to build Seraphine's 2014 Hill Dwarf ability increases.")
        raise


def _advancement_delta(level: int) -> list[AbilityIncrease]:
    try:
        milestones = {
            4: ("wisdom", 2),
            8: ("wisdom", 2),
            12: ("constitution", 2),
            16: ("constitution", 2),
            19: ("strength", 2),
        }
        choice = milestones.get(level)
        return [] if choice is None else [AbilityIncrease(ability=choice[0], amount=choice[1])]
    except Exception:
        logger.exception("Failed to build Seraphine's level-%s ASI delta.", level)
        raise


def _apply_increases(scores: AbilityScores, increases: list[AbilityIncrease]) -> AbilityScores:
    try:
        values = scores.model_dump()
        for increase in increases:
            values[increase.ability] += increase.amount
        return AbilityScores(**values)
    except Exception:
        logger.exception("Failed to apply Seraphine's 2014 ability increases.")
        raise


def _level_one_profile() -> CharacterBuildProfile:
    try:
        base = _base_scores()
        species = _species_increases()
        return CharacterBuildProfile(
            id="build-seraphine-dawnshield-2014-l1",
            template_id="seraphine-dawnshield-2014-l1",
            character_name="Seraphine Dawnshield",
            class_id="cleric",
            class_name="Cleric",
            level=1,
            ruleset="2014",
            subclass_id="life-domain",
            subclass_name="Life Domain",
            build_id="life-healer",
            species_id="hill-dwarf",
            species_name="Hill Dwarf",
            background_id="acolyte",
            background_name="Acolyte",
            base_ability_scores=base,
            species_increases=species,
            advancement_increases=[],
            final_ability_scores=_apply_increases(base, species),
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
            weapon_masteries=[],
            combat_loadout_kind=None,
            feature_audits=build_cleric_life_2014_feature_audits(1),
            source_references=[
                "D&D Basic Rules 2014: Hill Dwarf",
                "D&D Basic Rules 2014: Acolyte",
                "D&D Basic Rules 2014: Cleric",
                "D&D Basic Rules 2014: Life Domain",
                "D&D Basic Rules 2014: Equipment",
            ],
        )
    except Exception:
        logger.exception("Failed to build Seraphine's persistent 2014 level-1 profile.")
        raise


def _advance_one_level(previous: CharacterBuildProfile, next_level: int) -> CharacterBuildProfile:
    try:
        data = advance_profile_data(previous, next_level)
        asi_delta = _advancement_delta(next_level)
        previous_audits = build_cleric_life_2014_feature_audits(next_level - 1)
        current_audits = build_cleric_life_2014_feature_audits(next_level)
        data.update(
            advancement_increases=[*previous.advancement_increases, *asi_delta],
            final_ability_scores=_apply_increases(previous.final_ability_scores, asi_delta),
            feature_audits=[*previous.feature_audits, *current_audits[len(previous_audits):]],
            source_references=[
                *previous.source_references,
                f"D&D Basic Rules 2014: Cleric level {next_level}",
            ],
        )
        return CharacterBuildProfile(**data)
    except Exception:
        logger.exception("Failed to advance Seraphine from level %s to level %s.", previous.level, next_level)
        raise


def build_seraphine_dawnshield_2014_profile(level: int) -> CharacterBuildProfile:
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Seraphine profile covers levels 1 through 20.")
        profile = _level_one_profile()
        for next_level in range(2, level + 1):
            profile = _advance_one_level(profile, next_level)
        return profile
    except Exception:
        logger.exception("Failed to advance 2014 Seraphine Dawnshield to level %s", level)
        raise
