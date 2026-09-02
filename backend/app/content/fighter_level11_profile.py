from __future__ import annotations

from app.content.canonical_progression import advance_profile_data
from app.content.fighter_level10_profile import build_karnok_stoneward_level10_profile
from app.content.fighter_profile_from_levels import apply_fighter_level_to_profile_data
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit


def build_karnok_stoneward_level11_profile() -> CharacterBuildProfile:
    previous = build_karnok_stoneward_level10_profile()
    data = advance_profile_data(previous, 11)
    apply_fighter_level_to_profile_data(data, 11)
    source = "D&D Beyond Basic Rules 2024: Fighter 11 Two Extra Attacks"
    feature = FeatureAudit(
        feature_id="two-extra-attacks",
        feature_name="Two Extra Attacks",
        source_reference=source,
        category="class",
        combat_relevant=True,
        automated=True,
        notes="The Attack action resolves three certified weapon-attack slots at Fighter level 11.",
    )
    data.update(
        feature_audits=[*data["feature_audits"], feature.model_dump()],
        source_references=[*data["source_references"], source],
    )
    return CharacterBuildProfile.model_validate(data)
