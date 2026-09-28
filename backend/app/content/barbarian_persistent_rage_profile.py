from __future__ import annotations

import logging

from app.content.barbarian_berserker_endgame_profile import build_rokhan_stonefury_level14_profile
from app.content.barbarian_profile_from_levels import apply_barbarian_level_to_profile_data
from app.content.canonical_progression import advance_profile_data
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit

logger = logging.getLogger(__name__)


def build_rokhan_stonefury_level15_profile() -> CharacterBuildProfile:
    try:
        previous = build_rokhan_stonefury_level14_profile()
        data = advance_profile_data(previous, 15)
        apply_barbarian_level_to_profile_data(data, 15)
        feature = FeatureAudit(
            feature_id="persistent-rage",
            feature_name="Persistent Rage",
            source_reference="D&D Beyond Basic Rules 2024: Barbarian Level 15",
            category="class",
            combat_relevant=True,
            automated=True,
            notes=(
                "Uses the universal Rage persistence policy for the full 10-minute duration without "
                "round-by-round maintenance, ending early on Unconscious or Heavy armor. Initiative "
                "resource refill restores Rage to maximum once per Long Rest through a finite gate resource."
            ),
        )
        data.update(
            feature_audits=[*data["feature_audits"], feature.model_dump()],
            source_references=[
                *data["source_references"],
                "D&D Beyond Basic Rules 2024: Barbarian Level 15 Persistent Rage",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception:
        logger.exception("Failed to build Rokhan Stonefury 2024 level 15 profile.")
        raise
