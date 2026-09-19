from __future__ import annotations

import logging

from app.content.canonical_progression import advance_profile_data
from app.content.fighter_high_level_profile import build_karnok_stoneward_level16_profile
from app.content.fighter_profile_from_levels import apply_fighter_level_to_profile_data
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit

logger = logging.getLogger(__name__)


def build_karnok_stoneward_level17_profile() -> CharacterBuildProfile:
    """Advance the certified level-16 foundation using only the level-17 delta."""
    try:
        previous = build_karnok_stoneward_level16_profile()
        data = advance_profile_data(previous, 17)
        apply_fighter_level_to_profile_data(data, 17)
        action_surge = FeatureAudit(
            feature_id="action-surge-two-uses",
            feature_name="Action Surge — Two Uses",
            source_reference="D&D Beyond Basic Rules 2024: Fighter Level 17 — Action Surge and Indomitable",
            category="class",
            combat_relevant=True,
            automated=True,
            notes=(
                "The level-17 Fighter progression row increases Action Surge to two uses and "
                "Indomitable to three uses while preserving the existing universal action/resource resolvers."
            ),
        )
        data.update(
            feature_audits=[*data["feature_audits"], action_surge.model_dump()],
            source_references=[
                *data["source_references"],
                "D&D Beyond Basic Rules 2024: Fighter Level 17 — Action Surge and Indomitable",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception as exc:
        logger.exception("Failed to build Karnok Stoneward level 17 profile.")
        raise RuntimeError("Karnok Stoneward level 17 profile could not be built.") from exc
