from __future__ import annotations

from app.content.barbarian_berserker_progression_profile import build_rokhan_stonefury_level7_profile
from app.content.barbarian_profile_from_levels import apply_barbarian_level_to_profile_data
from app.content.canonical_progression import advance_profile_data
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit


def build_rokhan_stonefury_level8_profile() -> CharacterBuildProfile:
    previous = build_rokhan_stonefury_level7_profile()
    data = advance_profile_data(previous, 8)
    apply_barbarian_level_to_profile_data(data, 8)
    asi = FeatureAudit(
        feature_id="ability-score-improvement-l8",
        feature_name="Ability Score Improvement (+2 Strength)",
        source_reference="D&D Beyond Basic Rules 2024: Barbarian Level 8; Feats — Ability Score Improvement",
        category="feat", combat_relevant=True, automated=True,
        notes="STR 18→20; attack, damage, Strength saves, and Athletics update through shared character math.",
    )
    data.update(
        feature_audits=[*data["feature_audits"], asi.model_dump()],
        source_references=[*data["source_references"], "D&D Beyond Basic Rules 2024: Barbarian 8 Ability Score Improvement"],
    )
    return CharacterBuildProfile.model_validate(data)


def build_rokhan_stonefury_level9_profile() -> CharacterBuildProfile:
    previous = build_rokhan_stonefury_level8_profile()
    data = advance_profile_data(previous, 9)
    apply_barbarian_level_to_profile_data(data, 9)
    brutal = FeatureAudit(
        feature_id="brutal-strike", feature_name="Brutal Strike",
        source_reference="D&D Beyond Basic Rules 2024: Barbarian Level 9",
        category="class", combat_relevant=True, automated=True,
        notes="Reuses the universal Reckless Attack tradeoff and shared bonus-damage resolver for 1d10 extra damage.",
    )
    hamstring = FeatureAudit(
        feature_id="hamstring-blow", feature_name="Hamstring Blow",
        source_reference="D&D Beyond Basic Rules 2024: Barbarian Level 9",
        category="class", combat_relevant=False, automated=False,
        notes="Arena policy selects the direct-damage Brutal Strike option; speed-control option is arena-ignored.",
    )
    data.update(
        feature_audits=[*data["feature_audits"], brutal.model_dump(), hamstring.model_dump()],
        source_references=[*data["source_references"], "D&D Beyond Basic Rules 2024: Barbarian 9 Brutal Strike"],
    )
    return CharacterBuildProfile.model_validate(data)
