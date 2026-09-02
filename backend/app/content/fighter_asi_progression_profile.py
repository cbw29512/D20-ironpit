from __future__ import annotations

from app.content.canonical_progression import advance_profile_data
from app.content.fighter_profile_from_levels import apply_fighter_level_to_profile_data
from app.content.fighter_progression_profile import build_karnok_stoneward_level5_profile
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit


def build_karnok_stoneward_level6_profile() -> CharacterBuildProfile:
    previous = build_karnok_stoneward_level5_profile()
    data = advance_profile_data(previous, 6)
    apply_fighter_level_to_profile_data(data, 6)
    feature = FeatureAudit(
        feature_id="ability-score-improvement-l6",
        feature_name="Ability Score Improvement",
        source_reference="D&D Beyond Basic Rules 2024: Fighter Level 6; Feats — Ability Score Improvement",
        category="feat",
        combat_relevant=True,
        automated=True,
        notes=("Deterministic melee-role choice: +2 Strength, STR 18→20. Runtime Greatsword attack/damage, "
               "Strength save, and Athletics values are updated; Constitution and HP progression remain unchanged."),
    )
    data.update(
        feature_audits=[*data["feature_audits"], feature.model_dump()],
        source_references=[
            *data["source_references"],
            "Basic Rules 2024: Fighter — Level 6 Ability Score Improvement",
            "Basic Rules 2024: Feats — Ability Score Improvement (+2 Strength)",
        ],
    )
    return CharacterBuildProfile.model_validate(data)


def build_karnok_stoneward_level8_profile() -> CharacterBuildProfile:
    from app.content.fighter_champion_progression_profile import build_karnok_stoneward_level7_profile

    previous = build_karnok_stoneward_level7_profile()
    data = advance_profile_data(previous, 8)
    apply_fighter_level_to_profile_data(data, 8)
    feature = FeatureAudit(
        feature_id="ability-score-improvement-l8",
        feature_name="Ability Score Improvement",
        source_reference="D&D Beyond Basic Rules 2024: Fighter Level 8; Feats — Ability Score Improvement",
        category="feat",
        combat_relevant=True,
        automated=True,
        notes=("Strength is already 20, so the deterministic next combat priority is +2 Constitution, CON 16→18. "
               "Maximum HP is recalculated for all eight Fighter levels and the Constitution save increases by 1."),
    )
    data.update(
        feature_audits=[*data["feature_audits"], feature.model_dump()],
        source_references=[
            *data["source_references"],
            "Basic Rules 2024: Fighter — Level 8 Ability Score Improvement",
            "Basic Rules 2024: Feats — Ability Score Improvement (+2 Constitution)",
        ],
    )
    return CharacterBuildProfile.model_validate(data)
