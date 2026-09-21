from __future__ import annotations

import logging

from app.content.canonical_progression import advance_profile_data
from app.content.fighter_champion_profile_features import shared_fighter_champion_feature_audits
from app.content.fighter_high_level_profile import build_karnok_stoneward_level17_profile
from app.content.fighter_profile_from_levels import apply_fighter_level_to_profile_data
from app.domain.character_builds import CharacterBuildProfile

logger = logging.getLogger(__name__)


def build_karnok_stoneward_level18_profile() -> CharacterBuildProfile:
    """Advance canonical Karnok from Fighter 17 to Champion Fighter 18 only."""
    try:
        previous = build_karnok_stoneward_level17_profile()
        data = advance_profile_data(previous, 18)
        apply_fighter_level_to_profile_data(data, 18)
        survivor = next(
            item for item in shared_fighter_champion_feature_audits(18)
            if item.feature_id == "survivor"
        )
        data.update(
            feature_audits=[*data["feature_audits"], survivor.model_dump()],
            source_references=[
                *data["source_references"],
                "D&D Beyond Basic Rules 2024: Champion Level 18 — Survivor",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception as exc:
        logger.exception("Failed to build Karnok Stoneward level 18 profile.")
        raise RuntimeError("Karnok Stoneward level 18 profile could not be built.") from exc
