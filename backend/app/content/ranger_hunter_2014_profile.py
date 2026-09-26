from __future__ import annotations

import logging

from app.content.canonical_progression import advance_profile_data
from app.domain.character_builds import AbilityIncrease, AbilityScores, CharacterBuildProfile
from app.content.ranger_hunter_2014_audits import build_ranger_hunter_2014_feature_audits

logger = logging.getLogger(__name__)


def _scores() -> AbilityScores:
    return AbilityScores(strength=12, dexterity=15, constitution=14, intelligence=10, wisdom=13, charisma=8)


def _species_increases() -> list[AbilityIncrease]:
    return [AbilityIncrease(ability="dexterity", amount=2), AbilityIncrease(ability="wisdom", amount=1)]


def _apply(scores: AbilityScores, increases: list[AbilityIncrease]) -> AbilityScores:
    values = scores.model_dump()
    for increase in increases:
        values[increase.ability] += increase.amount
    return AbilityScores(**values)


def _level_one() -> CharacterBuildProfile:
    base = _scores()
    species = _species_increases()
    final = base.model_copy(update={"dexterity": 17, "wisdom": 14})
    return CharacterBuildProfile(
        id="build-rowan-ashtrail-2014-l1",
        template_id="rowan-ashtrail-2014-l1",
        character_name="Rowan Ashtrail",
        class_id="ranger", class_name="Ranger", level=1, ruleset="2014",
        subclass_id=None, subclass_name=None, build_id="archer",
        species_id="wood-elf", species_name="Wood Elf",
        background_id="outlander", background_name="Outlander",
        base_ability_scores=base, species_increases=species,
        advancement_increases=[], final_ability_scores=final,
        class_equipment_option="package",
        class_equipment=["Leather Armor", "Shortsword", "Shortsword", "Explorer's Pack", "Longbow", "20 Arrows"],
        background_equipment_option="package",
        background_equipment=["Staff", "Hunting Trap", "Traveler's Clothes", "10 gp"],
        skill_proficiencies=["Athletics", "Survival", "Perception", "Stealth", "Insight", "Investigation"],
        weapon_masteries=[], combat_loadout_kind="dual-wield",
        feature_audits=build_ranger_hunter_2014_feature_audits(1),
        source_references=[
            "D&D Basic Rules 2014: Wood Elf",
            "D&D Basic Rules 2014: Outlander",
            "D&D Basic Rules 2014: Ranger",
            "D&D Basic Rules 2014: Equipment",
        ],
    )


def build_rowan_ashtrail_2014_profile(level: int) -> CharacterBuildProfile:
    try:
        if level not in range(1, 14):
            raise ValueError("2014 Rowan profile currently covers levels 1 through 13.")
        profile = _level_one()
        if level == 1:
            return profile
        data = advance_profile_data(profile, 2)
        data.update(
            fighting_style="Archery",
            fighting_styles=["Archery"],
            feature_audits=build_ranger_hunter_2014_feature_audits(2),
            source_references=[*profile.source_references, "D&D Basic Rules 2014: Ranger 2"],
        )
        profile = CharacterBuildProfile(**data)
        if level == 2:
            return profile
        data = advance_profile_data(profile, 3)
        data.update(
            subclass_id="hunter",
            subclass_name="Hunter",
            feature_audits=build_ranger_hunter_2014_feature_audits(3),
            source_references=[
                *profile.source_references,
                "D&D Basic Rules 2014: Ranger 3",
                "D&D Basic Rules 2014: Hunter 3",
            ],
        )
        profile = CharacterBuildProfile(**data)
        if level == 3:
            return profile
        increase = AbilityIncrease(ability="dexterity", amount=2)
        data = advance_profile_data(profile, 4)
        data.update(
            advancement_increases=[*profile.advancement_increases, increase],
            final_ability_scores=_apply(profile.final_ability_scores, [increase]),
            feature_audits=build_ranger_hunter_2014_feature_audits(4),
            source_references=[*profile.source_references, "D&D Basic Rules 2014: Ranger 4"],
        )
        profile = CharacterBuildProfile(**data)
        if level == 4:
            return profile
        data = advance_profile_data(profile, 5)
        data.update(
            feature_audits=build_ranger_hunter_2014_feature_audits(5),
            source_references=[*profile.source_references, "D&D Basic Rules 2014: Ranger 5"],
        )
        profile = CharacterBuildProfile(**data)
        if level == 5:
            return profile
        data = advance_profile_data(profile, 6)
        data.update(
            feature_audits=build_ranger_hunter_2014_feature_audits(6),
            source_references=[*profile.source_references, "D&D Basic Rules 2014: Ranger 6"],
        )
        profile = CharacterBuildProfile(**data)
        if level == 6:
            return profile
        data = advance_profile_data(profile, 7)
        data.update(
            feature_audits=build_ranger_hunter_2014_feature_audits(7),
            source_references=[
                *profile.source_references,
                "D&D Basic Rules 2014: Ranger 7",
                "D&D Basic Rules 2014: Hunter 7",
            ],
        )
        profile = CharacterBuildProfile(**data)
        if level == 7:
            return profile
        increases = [
            AbilityIncrease(ability="dexterity", amount=1),
            AbilityIncrease(ability="wisdom", amount=1),
        ]
        data = advance_profile_data(profile, 8)
        data.update(
            advancement_increases=[*profile.advancement_increases, *increases],
            final_ability_scores=_apply(profile.final_ability_scores, increases),
            feature_audits=build_ranger_hunter_2014_feature_audits(8),
            source_references=[*profile.source_references, "D&D Basic Rules 2014: Ranger 8"],
        )
        profile = CharacterBuildProfile(**data)
        if level == 8:
            return profile
        data = advance_profile_data(profile, 9)
        data.update(
            feature_audits=build_ranger_hunter_2014_feature_audits(9),
            source_references=[*profile.source_references, "D&D Basic Rules 2014: Ranger 9"],
        )
        profile = CharacterBuildProfile(**data)
        if level == 9:
            return profile
        data = advance_profile_data(profile, 10)
        data.update(
            feature_audits=build_ranger_hunter_2014_feature_audits(10),
            source_references=[*profile.source_references, "D&D Basic Rules 2014: Ranger 10"],
        )
        profile = CharacterBuildProfile(**data)
        if level == 10:
            return profile
        data = advance_profile_data(profile, 11)
        data.update(
            feature_audits=build_ranger_hunter_2014_feature_audits(11),
            source_references=[
                *profile.source_references,
                "D&D Basic Rules 2014: Ranger 11",
                "D&D Basic Rules 2014: Hunter 11",
            ],
        )
        profile = CharacterBuildProfile(**data)
        if level == 11:
            return profile
        increase = AbilityIncrease(ability="wisdom", amount=2)
        data = advance_profile_data(profile, 12)
        data.update(
            advancement_increases=[*profile.advancement_increases, increase],
            final_ability_scores=_apply(profile.final_ability_scores, [increase]),
            feature_audits=build_ranger_hunter_2014_feature_audits(12),
            source_references=[*profile.source_references, "D&D Basic Rules 2014: Ranger 12"],
        )
        profile = CharacterBuildProfile(**data)
        if level == 12:
            return profile
        data = advance_profile_data(profile, 13)
        data.update(
            feature_audits=build_ranger_hunter_2014_feature_audits(13),
            source_references=[*profile.source_references, "D&D Basic Rules 2014: Ranger 13"],
        )
        return CharacterBuildProfile(**data)
    except Exception:
        logger.exception("Failed to compile 2014 Rowan Ashtrail profile at level %s.", level)
        raise
