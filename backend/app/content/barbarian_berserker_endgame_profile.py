from __future__ import annotations

from app.content.barbarian_berserker_mid_profile import build_rokhan_stonefury_level11_profile
from app.content.barbarian_profile_from_levels import apply_barbarian_level_to_profile_data
from app.content.canonical_progression import advance_profile_data
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit


def build_rokhan_stonefury_level12_profile() -> CharacterBuildProfile:
    previous = build_rokhan_stonefury_level11_profile()
    data = advance_profile_data(previous, 12)
    apply_barbarian_level_to_profile_data(data, 12)
    feature = FeatureAudit(
        feature_id="ability-score-improvement-l12", feature_name="Ability Score Improvement",
        source_reference="D&D Beyond Basic Rules 2024: Barbarian Level 12; Feats — Ability Score Improvement",
        category="feat", combat_relevant=True, automated=True,
        notes=("Canonical progression raises Constitution from 16 to 18; existing shared derived-stat math updates AC, HP, and saves."),
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
            "Adds Staggering Blow and Sundering Blow to Brutal Strike. The canonical damage-priority "
            "arena policy selects Sundering Blow, composed from the universal non-stacking next-incoming-"
            "attack flat-bonus modifier. Staggering's next-save Disadvantage and Opportunity-Attack "
            "suppression semantics are already universal engine primitives."
        ),
    )
    data.update(
        feature_audits=[*data["feature_audits"], feature.model_dump()],
        source_references=[
            *data["source_references"],
            "D&D Beyond Basic Rules 2024: Barbarian Level 13 Improved Brutal Strike",
        ],
    )
    return CharacterBuildProfile.model_validate(data)
