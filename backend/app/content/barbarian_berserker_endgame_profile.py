from __future__ import annotations

from app.content.barbarian_berserker_high_profile import build_rokhan_stonefury_level9_profile
from app.content.barbarian_profile_from_levels import apply_barbarian_level_to_profile_data
from app.content.canonical_progression import advance_profile_data
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit


def build_rokhan_stonefury_level10_profile() -> CharacterBuildProfile:
    previous = build_rokhan_stonefury_level9_profile()
    data = advance_profile_data(previous, 10)
    apply_barbarian_level_to_profile_data(data, 10)
    feature = FeatureAudit(
        feature_id="retaliation",
        feature_name="Retaliation",
        source_reference="D&D Beyond Basic Rules 2024: Path of the Berserker Level 10",
        category="subclass",
        combat_relevant=True,
        automated=True,
        notes=(
            "Reuses the universal damage-triggered reaction attack primitive already certified for 2014 "
            "Berserker Retaliation; 2024 supplies only the subclass unlock level."
        ),
    )
    data.update(
        feature_audits=[*data["feature_audits"], feature.model_dump()],
        source_references=[*data["source_references"], "D&D Beyond Basic Rules 2024: Path of the Berserker Level 10 Retaliation"],
    )
    return CharacterBuildProfile.model_validate(data)


def build_rokhan_stonefury_level11_profile() -> CharacterBuildProfile:
    previous = build_rokhan_stonefury_level10_profile()
    data = advance_profile_data(previous, 11)
    apply_barbarian_level_to_profile_data(data, 11)
    feature = FeatureAudit(
        feature_id="relentless-rage",
        feature_name="Relentless Rage",
        source_reference="D&D Beyond Basic Rules 2024: Barbarian Level 11",
        category="class",
        combat_relevant=True,
        automated=True,
        notes=(
            "Reuses the universal effect-bound survival-save primitive: Rage required, Constitution DC 10, "
            "+5 DC per attempt, and replacement HP equal to twice Barbarian level."
        ),
    )
    data.update(
        feature_audits=[*data["feature_audits"], feature.model_dump()],
        source_references=[*data["source_references"], "D&D Beyond Basic Rules 2024: Barbarian Level 11 Relentless Rage"],
    )
    return CharacterBuildProfile.model_validate(data)


def build_rokhan_stonefury_level12_profile() -> CharacterBuildProfile:
    previous = build_rokhan_stonefury_level11_profile()
    data = advance_profile_data(previous, 12)
    apply_barbarian_level_to_profile_data(data, 12)
    feature = FeatureAudit(
        feature_id="ability-score-improvement-l12",
        feature_name="Ability Score Improvement",
        source_reference="D&D Beyond Basic Rules 2024: Barbarian Level 12; Feats — Ability Score Improvement",
        category="feat",
        combat_relevant=True,
        automated=True,
        notes=(
            "Canonical progression raises Constitution from 16 to 18. Shared derived-stat math updates AC, HP, "
            "Constitution saves, and all dependent runtime values; no new combat primitive is introduced."
        ),
    )
    data.update(
        feature_audits=[*data["feature_audits"], feature.model_dump()],
        source_references=[*data["source_references"], "D&D Beyond Basic Rules 2024: Barbarian Level 12 Ability Score Improvement (+2 Constitution)"],
    )
    return CharacterBuildProfile.model_validate(data)


def build_rokhan_stonefury_level13_profile() -> CharacterBuildProfile:
    previous = build_rokhan_stonefury_level12_profile()
    data = advance_profile_data(previous, 13)
    apply_barbarian_level_to_profile_data(data, 13)
    feature = FeatureAudit(
        feature_id="improved-brutal-strike",
        feature_name="Improved Brutal Strike",
        source_reference="D&D Beyond Basic Rules 2024: Barbarian Level 13",
        category="class",
        combat_relevant=True,
        automated=True,
        notes=(
            "Adds Staggering Blow and Sundering Blow to the shared Brutal Strike effect list. "
            "Staggering composes next-save Disadvantage plus Opportunity Attack suppression; "
            "Sundering composes the generic next incoming other-creature attack +5 modifier. "
            "Level 13 still applies only one Brutal Strike effect per successful use."
        ),
    )
    data.update(
        feature_audits=[*data["feature_audits"], feature.model_dump()],
        source_references=[*data["source_references"], "D&D Beyond Basic Rules 2024: Barbarian Level 13 Improved Brutal Strike"],
    )
    return CharacterBuildProfile.model_validate(data)
