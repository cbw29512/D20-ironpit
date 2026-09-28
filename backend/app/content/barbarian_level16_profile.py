from __future__ import annotations

import logging

from app.content.barbarian_persistent_rage_profile import build_rokhan_stonefury_level15_profile
from app.content.barbarian_profile_from_levels import apply_barbarian_level_to_profile_data
from app.content.canonical_progression import advance_profile_data
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit

logger = logging.getLogger(__name__)


def build_rokhan_stonefury_level16_profile() -> CharacterBuildProfile:
    try:
        previous = build_rokhan_stonefury_level15_profile()
        data = advance_profile_data(previous, 16)
        apply_barbarian_level_to_profile_data(data, 16)
        feature = FeatureAudit(
            feature_id="ability-score-improvement-l16",
            feature_name="Ability Score Improvement",
            source_reference=(
                "D&D Beyond Basic Rules 2024: Barbarian Level 16; "
                "Feats — Ability Score Improvement"
            ),
            category="feat",
            combat_relevant=True,
            automated=True,
            notes=(
                "Canonical progression raises Constitution from 18 to 20. Shared derived-stat math "
                "updates Unarmored Defense AC, hit points, Constitution saves, and dependent values. "
                "The Barbarian level table independently raises Rage Damage from +3 to +4."
            ),
        )
        data.update(
            feature_audits=[*data["feature_audits"], feature.model_dump()],
            source_references=[
                *data["source_references"],
                "D&D Beyond Basic Rules 2024: Barbarian Level 16 Ability Score Improvement (+2 Constitution)",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception:
        logger.exception("Failed to build Rokhan Stonefury 2024 level 16 profile.")
        raise
