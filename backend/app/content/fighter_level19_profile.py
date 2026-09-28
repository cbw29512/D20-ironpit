from __future__ import annotations

import logging

from app.content.canonical_progression import advance_profile_data
from app.content.fighter_endgame_profile import build_karnok_stoneward_level18_profile
from app.content.fighter_profile_from_levels import apply_fighter_level_to_profile_data
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit

logger = logging.getLogger(__name__)


def build_karnok_stoneward_level19_profile() -> CharacterBuildProfile:
    """Advance canonical Karnok from Fighter 18 to Fighter 19 Epic Boon."""
    try:
        previous = build_karnok_stoneward_level18_profile()
        data = advance_profile_data(previous, 19)
        apply_fighter_level_to_profile_data(data, 19)
        feature = FeatureAudit(
            feature_id="boon-combat-prowess-l19",
            feature_name="Boon of Combat Prowess",
            source_reference="D&D Beyond Basic Rules 2024: Fighter Level 19; Boon of Combat Prowess",
            category="feat",
            combat_relevant=True,
            automated=True,
            notes=(
                "Canonical choice raises Dexterity 17 to 18. Peerless Aim reuses the universal "
                "miss-to-hit override with one resource restored at the start of each turn."
            ),
        )
        data.update(
            feature_audits=[*data["feature_audits"], feature.model_dump()],
            source_references=[
                *data["source_references"],
                "D&D Beyond Basic Rules 2024: Fighter Level 19; Boon of Combat Prowess",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception as exc:
        logger.exception("Failed to build Karnok Stoneward level 19 profile.")
        raise RuntimeError("Karnok Stoneward level 19 profile could not be built.") from exc
