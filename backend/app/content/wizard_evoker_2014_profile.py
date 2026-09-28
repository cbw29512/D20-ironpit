from __future__ import annotations

import logging

from app.content.canonical_progression import advance_profile_data
from app.content.wizard_evoker_2014_audits import build_wizard_evoker_2014_feature_audits
from app.domain.character_builds import AbilityIncrease, AbilityScores, CharacterBuildProfile

logger = logging.getLogger(__name__)


def _base_scores() -> AbilityScores:
    return AbilityScores(
        strength=8, dexterity=13, constitution=14,
        intelligence=15, wisdom=12, charisma=10,
    )


def _human_increases() -> list[AbilityIncrease]:
    return [
        AbilityIncrease(ability="strength", amount=1),
        AbilityIncrease(ability="dexterity", amount=1),
        AbilityIncrease(ability="constitution", amount=1),
        AbilityIncrease(ability="intelligence", amount=1),
        AbilityIncrease(ability="wisdom", amount=1),
        AbilityIncrease(ability="charisma", amount=1),
    ]


def _apply(scores: AbilityScores, increases: list[AbilityIncrease]) -> AbilityScores:
    try:
        values = scores.model_dump()
        for increase in increases:
            values[increase.ability] += increase.amount
        return AbilityScores(**values)
    except Exception:
        logger.exception("Failed to apply Elian's 2014 ability increases.")
        raise


def _level_one() -> CharacterBuildProfile:
    base = _base_scores()
    species = _human_increases()
    return CharacterBuildProfile(
        id="build-elian-starweaver-2014-l1",
        template_id="elian-starweaver-2014-l1",
        character_name="Elian Starweaver",
        class_id="wizard", class_name="Wizard", level=1, ruleset="2014",
        subclass_id=None, subclass_name=None, build_id="fire-damage",
        species_id="human", species_name="Human",
        background_id="sage", background_name="Sage",
        base_ability_scores=base, species_increases=species,
        advancement_increases=[], final_ability_scores=_apply(base, species),
        class_equipment_option="package",
        class_equipment=["Dagger", "Arcane Focus", "Scholar's Pack", "Spellbook"],
        background_equipment_option="package",
        background_equipment=["Bottle of Black Ink", "Quill", "Small Knife", "Letter", "Common Clothes", "10 gp"],
        skill_proficiencies=["Arcana", "History", "Investigation", "Insight"],
        weapon_masteries=[], combat_loadout_kind=None,
        feature_audits=build_wizard_evoker_2014_feature_audits(1),
        source_references=[
            "D&D Basic Rules 2014: Human",
            "D&D Basic Rules 2014: Sage",
            "D&D Basic Rules 2014: Wizard",
            "D&D Basic Rules 2014: Equipment",
        ],
    )


_ASI_BY_LEVEL: dict[int, list[AbilityIncrease]] = {
    4: [AbilityIncrease(ability="intelligence", amount=2)],
    8: [AbilityIncrease(ability="intelligence", amount=2)],
    12: [AbilityIncrease(ability="constitution", amount=2)],
    16: [AbilityIncrease(ability="constitution", amount=2)],
    19: [
        AbilityIncrease(ability="constitution", amount=1),
        AbilityIncrease(ability="wisdom", amount=1),
    ],
}


def build_elian_starweaver_2014_profile(level: int) -> CharacterBuildProfile:
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Elian profile currently covers levels 1 through 20.")
        profile = _level_one()
        if level == 1:
            return profile

        for next_level in range(2, level + 1):
            data = advance_profile_data(profile, next_level)
            increases = _ASI_BY_LEVEL.get(next_level, [])
            if increases:
                data.update(
                    advancement_increases=[*profile.advancement_increases, *increases],
                    final_ability_scores=_apply(profile.final_ability_scores, increases),
                )
            if next_level == 2:
                data.update(subclass_id="evoker", subclass_name="School of Evocation")
            refs = [*profile.source_references, f"D&D Basic Rules 2014: Wizard {next_level}"]
            if next_level in (2, 6, 10, 14):
                refs.append(f"D&D Basic Rules 2014: School of Evocation {next_level}")
            data.update(
                feature_audits=build_wizard_evoker_2014_feature_audits(next_level),
                source_references=refs,
            )
            profile = CharacterBuildProfile(**data)
        return profile
    except Exception:
        logger.exception("Failed to compile 2014 Elian Starweaver profile at level %s.", level)
        raise
