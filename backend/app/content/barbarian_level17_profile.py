from __future__ import annotations

import logging

from app.content.barbarian_level16_profile import build_rokhan_stonefury_level16_profile
from app.content.barbarian_profile_from_levels import apply_barbarian_level_to_profile_data
from app.content.canonical_progression import advance_profile_data
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit

logger = logging.getLogger(__name__)


def build_rokhan_stonefury_level17_profile() -> CharacterBuildProfile:
    try:
        previous = build_rokhan_stonefury_level16_profile()
        data = advance_profile_data(previous, 17)
        apply_barbarian_level_to_profile_data(data, 17)
        feature = FeatureAudit(
            feature_id="improved-brutal-strike-l17",
            feature_name="Improved Brutal Strike",
            source_reference="D&D Beyond Basic Rules 2024: Barbarian Level 17 Improved Brutal Strike",
            category="class",
            combat_relevant=True,
            automated=True,
            notes=(
                "Existing universal Brutal Strike capability scales to 2d10 extra damage and allows "
                "two different effects on the same qualifying strike. No source-specific resolver is required."
            ),
        )
        data.update(
            feature_audits=[*data["feature_audits"], feature.model_dump()],
            source_references=[
                *data["source_references"],
                "D&D Beyond Basic Rules 2024: Barbarian Level 17 Improved Brutal Strike",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception:
        logger.exception("Failed to build Rokhan Stonefury 2024 level 17 profile.")
        raise
