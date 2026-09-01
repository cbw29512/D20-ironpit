from __future__ import annotations

from app.content.canonical_progression import advance_profile_data
from app.content.fighter_asi_progression_profile import build_karnok_stoneward_level6_profile
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit


def build_karnok_stoneward_level7_profile() -> CharacterBuildProfile:
    previous = build_karnok_stoneward_level6_profile()
    data = advance_profile_data(previous, 7)
    feature = FeatureAudit(
        feature_id="additional-fighting-style-great-weapon-fighting",
        feature_name="Additional Fighting Style — Great Weapon Fighting",
        source_reference="D&D Beyond Basic Rules 2024: Champion Level 7; Fighting Style — Great Weapon Fighting",
        category="subclass",
        combat_relevant=True,
        automated=True,
        notes=("Deterministic role-preserving choice: Great Weapon Fighting. Karnok's Greatsword weapon damage "
               "treats each 1 or 2 as 3; the Shortbow and non-weapon rider dice do not receive the minimum."),
    )
    data.update(
        feature_audits=[*data["feature_audits"], feature.model_dump()],
        source_references=[
            *data["source_references"],
            "Basic Rules 2024: Champion — Level 7 Additional Fighting Style",
            "Basic Rules 2024: Fighting Style — Great Weapon Fighting",
        ],
    )
    return CharacterBuildProfile.model_validate(data)
