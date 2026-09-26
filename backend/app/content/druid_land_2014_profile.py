from __future__ import annotations

import logging

from app.content.canonical_progression import advance_profile_data
from app.content.druid_land_2014_audits import build_druid_land_2014_feature_audits
from app.domain.character_builds import AbilityIncrease, AbilityScores, CharacterBuildProfile

logger = logging.getLogger(__name__)


def _base() -> AbilityScores:
    return AbilityScores(
        strength=8, dexterity=13, constitution=14,
        intelligence=12, wisdom=15, charisma=10,
    )


def _species() -> list[AbilityIncrease]:
    return [
        AbilityIncrease(ability="dexterity", amount=2),
        AbilityIncrease(ability="wisdom", amount=1),
    ]


def _advancement_delta(level: int) -> list[AbilityIncrease]:
    choices = {
        4: (("wisdom", 2),),
        8: (("wisdom", 2),),
        12: (("constitution", 2),),
        16: (("constitution", 2),),
        19: (("dexterity", 2),),
    }
    return [AbilityIncrease(ability=ability, amount=amount) for ability, amount in choices.get(level, ())]


def _apply(scores: AbilityScores, increases: list[AbilityIncrease]) -> AbilityScores:
    values = scores.model_dump()
    for increase in increases:
        values[increase.ability] += increase.amount
    return AbilityScores(**values)


def _level_one() -> CharacterBuildProfile:
    base = _base()
    species = _species()
    return CharacterBuildProfile(
        id="build-thalen-greenbough-2014-l1",
        template_id="thalen-greenbough-2014-l1",
        character_name="Thalen Greenbough",
        class_id="druid",
        class_name="Druid",
        level=1,
        ruleset="2014",
        subclass_id=None,
        subclass_name=None,
        build_id="land-damage",
        species_id="wood-elf",
        species_name="Wood Elf",
        background_id="acolyte",
        background_name="Acolyte",
        base_ability_scores=base,
        species_increases=species,
        advancement_increases=[],
        final_ability_scores=_apply(base, species),
        class_equipment_option="package",
        class_equipment=[
            "Wooden Shield", "Scimitar", "Leather Armor",
            "Explorer's Pack", "Druidic Focus",
        ],
        background_equipment_option="package",
        background_equipment=[
            "Holy Symbol", "Prayer Book", "5 Sticks of Incense",
            "Vestments", "Common Clothes", "15 gp",
        ],
        skill_proficiencies=["Insight", "Religion", "Perception", "Survival"],
        weapon_masteries=[],
        combat_loadout_kind=None,
        feature_audits=build_druid_land_2014_feature_audits(1),
        source_references=[
            "D&D Basic Rules 2014: Wood Elf",
            "D&D Basic Rules 2014: Acolyte",
            "D&D Basic Rules 2014: Druid",
            "D&D Basic Rules 2014: Equipment",
        ],
    )


def _advance(previous: CharacterBuildProfile, next_level: int) -> CharacterBuildProfile:
    data = advance_profile_data(previous, next_level)
    delta = _advancement_delta(next_level)
    data.update(
        subclass_id="circle-land" if next_level >= 2 else None,
        subclass_name="Circle of the Land" if next_level >= 2 else None,
        advancement_increases=[*previous.advancement_increases, *delta],
        final_ability_scores=_apply(previous.final_ability_scores, delta),
        feature_audits=build_druid_land_2014_feature_audits(next_level),
        source_references=[
            *previous.source_references,
            f"D&D Basic Rules 2014: Druid level {next_level}",
        ],
    )
    return CharacterBuildProfile(**data)


def build_thalen_greenbough_2014_profile(level: int) -> CharacterBuildProfile:
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Thalen profile covers levels 1 through 20.")
        profile = _level_one()
        for next_level in range(2, level + 1):
            profile = _advance(profile, next_level)
        return profile
    except Exception:
        logger.exception("Failed to compile 2014 Thalen Greenbough profile at level %s.", level)
        raise
