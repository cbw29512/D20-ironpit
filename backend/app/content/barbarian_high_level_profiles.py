from __future__ import annotations

from app.content.barbarian_berserker_progression_profile import build_rokhan_stonefury_level6_profile
from app.content.barbarian_profile_from_levels import apply_barbarian_level_to_profile_data
from app.content.canonical_progression import advance_profile_data
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit


def build_rokhan_stonefury_level7_profile() -> CharacterBuildProfile:
    previous = build_rokhan_stonefury_level6_profile()
    data = advance_profile_data(previous, 7)
    apply_barbarian_level_to_profile_data(data, 7)
    source = "D&D Beyond Basic Rules 2024: Barbarian Level 7"
    features = [
        FeatureAudit(
            feature_id="feral-instinct", feature_name="Feral Instinct", source_reference=source,
            category="class", combat_relevant=True, automated=True,
            notes="Rokhan has Advantage on Initiative rolls through the shared initiative resolver.",
        ),
        FeatureAudit(
            feature_id="instinctive-pounce", feature_name="Instinctive Pounce", source_reference=source,
            category="class", combat_relevant=True, automated=True,
            notes="When Rage starts, Rokhan may move up to half his Speed through the shared movement resolver.",
        ),
    ]
    data.update(
        feature_audits=[*data["feature_audits"], *(feature.model_dump() for feature in features)],
        source_references=[*data["source_references"], "Basic Rules 2024: Barbarian — Level 7 Feral Instinct and Instinctive Pounce"],
    )
    return CharacterBuildProfile.model_validate(data)


def build_rokhan_stonefury_level8_profile() -> CharacterBuildProfile:
    previous = build_rokhan_stonefury_level7_profile()
    data = advance_profile_data(previous, 8)
    apply_barbarian_level_to_profile_data(data, 8)
    source = "D&D Beyond Basic Rules 2024: Barbarian Level 8 Ability Score Improvement"
    feature = FeatureAudit(
        feature_id="ability-score-improvement-l8", feature_name="Ability Score Improvement",
        source_reference=source, category="feat", combat_relevant=True, automated=True,
        notes="Deterministic melee progression: +2 Strength, STR 18→20; attack, damage, saves, and Athletics update from the level table.",
    )
    data.update(
        feature_audits=[*data["feature_audits"], feature.model_dump()],
        source_references=[*data["source_references"], source, "Basic Rules 2024: Feats — Ability Score Improvement (+2 Strength)"],
    )
    return CharacterBuildProfile.model_validate(data)


def build_rokhan_stonefury_level9_profile() -> CharacterBuildProfile:
    previous = build_rokhan_stonefury_level8_profile()
    data = advance_profile_data(previous, 9)
    apply_barbarian_level_to_profile_data(data, 9)
    source = "D&D Beyond Basic Rules 2024: Barbarian Level 9 Brutal Strike"
    feature = FeatureAudit(
        feature_id="brutal-strike", feature_name="Brutal Strike",
        source_reference=source, category="class", combat_relevant=True, automated=False,
        notes=(
            "Requires trading Reckless Attack Advantage on one Strength attack for extra damage "
            "and a selectable Forceful or Hamstring rider. Certification waits for shared "
            "attack-choice plus forced-movement/speed-control parity."
        ),
    )
    data.update(
        feature_audits=[*data["feature_audits"], feature.model_dump()],
        source_references=[*data["source_references"], source],
    )
    return CharacterBuildProfile.model_validate(data)
