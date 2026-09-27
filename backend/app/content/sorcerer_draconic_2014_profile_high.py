from __future__ import annotations

from app.content.canonical_progression import advance_profile_data
from app.content.sorcerer_draconic_2014_audits import build_sorcerer_draconic_2014_feature_audits
from app.domain.character_builds import AbilityIncrease, AbilityScores, CharacterBuildProfile


def advance_nyra_2014_high_levels(
    profile: CharacterBuildProfile,
    target_level: int,
) -> CharacterBuildProfile:
    """Advance Nyra from a completed level-9 profile through levels 10-20."""
    if profile.level != 9 or target_level not in range(10, 21):
        raise ValueError("High-level Nyra progression requires level 9 and target 10-20.")

    for next_level in (10, 11):
        data = advance_profile_data(profile, next_level)
        data.update(
            feature_audits=build_sorcerer_draconic_2014_feature_audits(next_level),
            source_references=[*profile.source_references, f"D&D Basic Rules 2014: Sorcerer {next_level}"],
        )
        profile = CharacterBuildProfile(**data)
        if target_level == next_level:
            return profile

    increase = AbilityIncrease(ability="constitution", amount=2)
    values = profile.final_ability_scores.model_dump()
    values["constitution"] += increase.amount
    data = advance_profile_data(profile, 12)
    data.update(
        advancement_increases=[*profile.advancement_increases, increase],
        final_ability_scores=AbilityScores(**values),
        feature_audits=build_sorcerer_draconic_2014_feature_audits(12),
        source_references=[*profile.source_references, "D&D Basic Rules 2014: Sorcerer 12"],
    )
    profile = CharacterBuildProfile(**data)
    if target_level == 12:
        return profile

    data = advance_profile_data(profile, 13)
    data.update(
        feature_audits=build_sorcerer_draconic_2014_feature_audits(13),
        source_references=[*profile.source_references, "D&D Basic Rules 2014: Sorcerer 13"],
    )
    profile = CharacterBuildProfile(**data)
    if target_level == 13:
        return profile

    for next_level in (14, 15):
        data = advance_profile_data(profile, next_level)
        refs = [*profile.source_references, f"D&D Basic Rules 2014: Sorcerer {next_level}"]
        if next_level == 14:
            refs.append("D&D Basic Rules 2014: Draconic Bloodline 14")
        data.update(
            feature_audits=build_sorcerer_draconic_2014_feature_audits(next_level),
            source_references=refs,
        )
        profile = CharacterBuildProfile(**data)
        if target_level == next_level:
            return profile

    increase = AbilityIncrease(ability="constitution", amount=2)
    values = profile.final_ability_scores.model_dump()
    values["constitution"] += increase.amount
    data = advance_profile_data(profile, 16)
    data.update(
        advancement_increases=[*profile.advancement_increases, increase],
        final_ability_scores=AbilityScores(**values),
        feature_audits=build_sorcerer_draconic_2014_feature_audits(16),
        source_references=[*profile.source_references, "D&D Basic Rules 2014: Sorcerer 16"],
    )
    profile = CharacterBuildProfile(**data)
    if target_level == 16:
        return profile

    for next_level in (17, 18):
        data = advance_profile_data(profile, next_level)
        refs = [*profile.source_references, f"D&D Basic Rules 2014: Sorcerer {next_level}"]
        if next_level == 18:
            refs.append("D&D Basic Rules 2014: Draconic Bloodline 18")
        data.update(
            feature_audits=build_sorcerer_draconic_2014_feature_audits(next_level),
            source_references=refs,
        )
        profile = CharacterBuildProfile(**data)
        if target_level == next_level:
            return profile

    increase = AbilityIncrease(ability="dexterity", amount=2)
    values = profile.final_ability_scores.model_dump()
    values["dexterity"] += increase.amount
    data = advance_profile_data(profile, 19)
    data.update(
        advancement_increases=[*profile.advancement_increases, increase],
        final_ability_scores=AbilityScores(**values),
        feature_audits=build_sorcerer_draconic_2014_feature_audits(19),
        source_references=[*profile.source_references, "D&D Basic Rules 2014: Sorcerer 19"],
    )
    profile = CharacterBuildProfile(**data)
    if target_level == 19:
        return profile

    data = advance_profile_data(profile, 20)
    data.update(
        feature_audits=build_sorcerer_draconic_2014_feature_audits(20),
        source_references=[*profile.source_references, "D&D Basic Rules 2014: Sorcerer 20"],
    )
    return CharacterBuildProfile(**data)
