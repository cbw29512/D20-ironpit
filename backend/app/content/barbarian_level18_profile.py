from __future__ import annotations

import logging

from app.content.barbarian_level17_profile import build_rokhan_stonefury_level17_profile
from app.content.barbarian_profile_from_levels import apply_barbarian_level_to_profile_data
from app.content.canonical_progression import advance_profile_data
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit

logger = logging.getLogger(__name__)


def build_rokhan_stonefury_level18_profile() -> CharacterBuildProfile:
    try:
        previous = build_rokhan_stonefury_level17_profile()
        data = advance_profile_data(previous, 18)
        apply_barbarian_level_to_profile_data(data, 18)
        feature = FeatureAudit(
            feature_id="indomitable-might-l18",
            feature_name="Indomitable Might",
            source_reference="D&D Beyond Basic Rules 2024: Barbarian Level 18 Indomitable Might",
            category="class",
            combat_relevant=True,
            automated=True,
            notes=(
                "Strength checks reuse the existing universal ability-score total floor. "
                "Strength saving throws use the matching universal saving-throw total floor. "
                "Neither path dispatches on the Barbarian or feature name."
            ),
        )
        data.update(
            feature_audits=[*data["feature_audits"], feature.model_dump()],
            source_references=[
                *data["source_references"],
                "D&D Beyond Basic Rules 2024: Barbarian Level 18 Indomitable Might",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception:
        logger.exception("Failed to build Rokhan Stonefury 2024 level 18 profile.")
        raise
