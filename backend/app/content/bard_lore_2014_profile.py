from __future__ import annotations

import logging

from app.content.bard_2014_audits import build_bard_2014_feature_audits
from app.content.canonical_progression import advance_profile_data
from app.domain.character_builds import AbilityIncrease, AbilityScores, CharacterBuildProfile

logger = logging.getLogger(__name__)


def _base() -> AbilityScores:
    return AbilityScores(
        strength=8, dexterity=12, constitution=10,
        intelligence=13, wisdom=14, charisma=15,
    )


def _species() -> list[AbilityIncrease]:
    return [
        AbilityIncrease(ability="charisma", amount=2),
        AbilityIncrease(ability="dexterity", amount=1),
        AbilityIncrease(ability="constitution", amount=1),
    ]


def _advancement_delta(level: int) -> list[AbilityIncrease]:
    choices = {
        4: (("charisma", 2),),
        8: (("charisma", 1), ("dexterity", 1)),
        12: (("dexterity", 2),),
        16: (("dexterity", 2),),
        19: (("constitution", 2),),
    }
    return [AbilityIncrease(ability=a, amount=n) for a, n in choices.get(level, ())]


def _apply(scores: AbilityScores, increases: list[AbilityIncrease]) -> AbilityScores:
    values = scores.model_dump()
    for increase in increases:
        values[increase.ability] += increase.amount
    return AbilityScores(**values)


def _level_one() -> CharacterBuildProfile:
    base = _base()
    species = _species()
    return CharacterBuildProfile(
        id="build-lyra-silverstring-2014-l1",
        template_id="lyra-silverstring-2014-l1",
        character_name="Lyra Silverstring",
        class_id="bard",
        class_name="Bard",
        level=1,
        ruleset="2014",
        subclass_id=None,
        subclass_name=None,
        build_id="lore-support",
        species_id="half-elf",
        species_name="Half-Elf",
        background_id="entertainer",
        background_name="Entertainer",
        base_ability_scores=base,
        species_increases=species,
        advancement_increases=[],
        final_ability_scores=_apply(base, species),
        class_equipment_option="package",
        class_equipment=["Rapier", "Diplomat's Pack", "Lute", "Leather Armor", "Dagger"],
        background_equipment_option="package",
        background_equipment=["Musical Instrument", "Admirer's Favor", "Costume", "15 gp"],
        skill_proficiencies=["Acrobatics", "Perception", "Performance", "Persuasion"],
        weapon_masteries=[],
        combat_loadout_kind=None,
        feature_audits=build_bard_2014_feature_audits(1),
        source_references=[
            "D&D Basic Rules 2014: Half-Elf",
            "D&D Basic Rules 2014: Entertainer",
            "D&D Basic Rules 2014: Bard",
            "D&D Basic Rules 2014: Equipment",
        ],
    )


def _advance(previous: CharacterBuildProfile, next_level: int) -> CharacterBuildProfile:
    data = advance_profile_data(previous, next_level)
    delta = _advancement_delta(next_level)
    data.update(
        subclass_id="college-lore" if next_level >= 3 else None,
        subclass_name="College of Lore" if next_level >= 3 else None,
        advancement_increases=[*previous.advancement_increases, *delta],
        final_ability_scores=_apply(previous.final_ability_scores, delta),
        feature_audits=build_bard_2014_feature_audits(next_level),
        source_references=[
            *previous.source_references,
            f"D&D Basic Rules 2014: Bard level {next_level}",
        ],
    )
    return CharacterBuildProfile(**data)


def build_lyra_silverstring_2014_profile(level: int) -> CharacterBuildProfile:
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Lyra profile covers levels 1 through 20.")
        profile = _level_one()
        for next_level in range(2, level + 1):
            profile = _advance(profile, next_level)
        return profile
    except Exception:
        logger.exception("Failed to compile 2014 Lyra Silverstring profile at level %s.", level)
        raise
