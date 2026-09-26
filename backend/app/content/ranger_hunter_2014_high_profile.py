from __future__ import annotations

from app.content.canonical_progression import advance_profile_data
from app.content.ranger_hunter_2014_audits import build_ranger_hunter_2014_feature_audits
from app.domain.character_builds import AbilityIncrease, AbilityScores, CharacterBuildProfile


def _apply(scores: AbilityScores, increases: list[AbilityIncrease]) -> AbilityScores:
    values = scores.model_dump()
    for increase in increases:
        values[increase.ability] += increase.amount
    return AbilityScores(**values)


def advance_rowan_ashtrail_2014_high(
    profile: CharacterBuildProfile,
    level: int,
) -> CharacterBuildProfile:
    """Advance the already-built level-8 Ranger through levels 9-20."""
    if level not in range(9, 21):
        raise ValueError("High-level 2014 Ranger progression covers levels 9 through 20.")

    data = advance_profile_data(profile, 9)
    data.update(
        feature_audits=build_ranger_hunter_2014_feature_audits(9),
        source_references=[*profile.source_references, "D&D Basic Rules 2014: Ranger 9"],
    )
    profile = CharacterBuildProfile(**data)
    if level == 9:
        return profile

    for next_level in (10, 11):
        data = advance_profile_data(profile, next_level)
        refs = [*profile.source_references, f"D&D Basic Rules 2014: Ranger {next_level}"]
        if next_level == 11:
            refs.append("D&D Basic Rules 2014: Hunter 11")
        data.update(
            feature_audits=build_ranger_hunter_2014_feature_audits(next_level),
            source_references=refs,
        )
        profile = CharacterBuildProfile(**data)
        if level == next_level:
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

    for next_level in (13, 14, 15):
        data = advance_profile_data(profile, next_level)
        refs = [*profile.source_references, f"D&D Basic Rules 2014: Ranger {next_level}"]
        if next_level == 15:
            refs.append("D&D Basic Rules 2014: Hunter 15")
        data.update(
            feature_audits=build_ranger_hunter_2014_feature_audits(next_level),
            source_references=refs,
        )
        profile = CharacterBuildProfile(**data)
        if level == next_level:
            return profile

    increase = AbilityIncrease(ability="wisdom", amount=2)
    data = advance_profile_data(profile, 16)
    data.update(
        advancement_increases=[*profile.advancement_increases, increase],
        final_ability_scores=_apply(profile.final_ability_scores, [increase]),
        feature_audits=build_ranger_hunter_2014_feature_audits(16),
        source_references=[*profile.source_references, "D&D Basic Rules 2014: Ranger 16"],
    )
    profile = CharacterBuildProfile(**data)
    if level == 16:
        return profile

    for next_level in (17, 18):
        data = advance_profile_data(profile, next_level)
        data.update(
            feature_audits=build_ranger_hunter_2014_feature_audits(next_level),
            source_references=[*profile.source_references, f"D&D Basic Rules 2014: Ranger {next_level}"],
        )
        profile = CharacterBuildProfile(**data)
        if level == next_level:
            return profile

    increases = [
        AbilityIncrease(ability="wisdom", amount=1),
        AbilityIncrease(ability="constitution", amount=1),
    ]
    data = advance_profile_data(profile, 19)
    data.update(
        advancement_increases=[*profile.advancement_increases, *increases],
        final_ability_scores=_apply(profile.final_ability_scores, increases),
        feature_audits=build_ranger_hunter_2014_feature_audits(19),
        source_references=[*profile.source_references, "D&D Basic Rules 2014: Ranger 19"],
    )
    profile = CharacterBuildProfile(**data)
    if level == 19:
        return profile

    data = advance_profile_data(profile, 20)
    data.update(
        feature_audits=build_ranger_hunter_2014_feature_audits(20),
        source_references=[*profile.source_references, "D&D Basic Rules 2014: Ranger 20"],
    )
    return CharacterBuildProfile(**data)
