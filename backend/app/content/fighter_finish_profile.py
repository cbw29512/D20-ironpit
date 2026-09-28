from __future__ import annotations

import logging

from app.content.canonical_progression import advance_profile_data
from app.content.fighter_endgame_profile import build_karnok_stoneward_level18_profile
from app.content.fighter_profile_from_levels import apply_fighter_level_to_profile_data
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit

logger = logging.getLogger(__name__)


def _combat_prowess_audit() -> FeatureAudit:
    try:
        return FeatureAudit(
            feature_id="boon-combat-prowess",
            feature_name="Boon of Combat Prowess",
            source_reference="D&D Beyond Basic Rules 2024: Fighter 19 Epic Boon; Boon of Combat Prowess",
            category="feat",
            combat_relevant=True,
            automated=True,
            notes=(
                "Peerless Aim reuses the universal miss-to-hit override with a one-use resource "
                "that refills at the start of each turn."
            ),
        )
    except Exception:
        logger.exception("Failed to build Boon of Combat Prowess audit.")
        raise


def build_karnok_stoneward_level19_profile() -> CharacterBuildProfile:
    try:
        previous = build_karnok_stoneward_level18_profile()
        data = advance_profile_data(previous, 19)
        apply_fighter_level_to_profile_data(data, 19)
        data.update(
            feature_audits=[*data["feature_audits"], _combat_prowess_audit().model_dump()],
            source_references=[
                *data["source_references"],
                "D&D Beyond Basic Rules 2024: Fighter 19 Epic Boon; Boon of Combat Prowess",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception as exc:
        logger.exception("Failed to build Karnok Stoneward level 19 profile.")
        raise RuntimeError("Karnok Stoneward level 19 profile could not be built.") from exc


def build_karnok_stoneward_level20_profile() -> CharacterBuildProfile:
    try:
        previous = build_karnok_stoneward_level19_profile()
        data = advance_profile_data(previous, 20)
        apply_fighter_level_to_profile_data(data, 20)
        feature = FeatureAudit(
            feature_id="three-extra-attacks",
            feature_name="Three Extra Attacks",
            source_reference="D&D Beyond Basic Rules 2024: Fighter 20 Three Extra Attacks",
            category="class",
            combat_relevant=True,
            automated=True,
            notes="The existing universal Attack Action slot model scales to four attacks.",
        )
        data.update(
            feature_audits=[*data["feature_audits"], feature.model_dump()],
            source_references=[
                *data["source_references"],
                "D&D Beyond Basic Rules 2024: Fighter 20 Three Extra Attacks",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception as exc:
        logger.exception("Failed to build Karnok Stoneward level 20 profile.")
        raise RuntimeError("Karnok Stoneward level 20 profile could not be built.") from exc
