from __future__ import annotations

import logging

from app.content.audited_cleric_life_levels13_16 import build_seraphine_dawnshield_level16_profile
from app.content.canonical_progression import advance_profile_data
from app.content.cleric_profile_from_levels import apply_cleric_level_to_profile_data
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit

logger = logging.getLogger(__name__)


def _feature(feature_id: str, name: str, automated: bool, notes: str) -> FeatureAudit:
    try:
        return FeatureAudit(
            feature_id=feature_id,
            feature_name=name,
            source_reference="D&D Beyond Basic Rules 2024: Cleric — high-level progression",
            category="class",
            combat_relevant=True,
            automated=automated,
            notes=notes,
        )
    except Exception:
        logger.exception("Failed to build Cleric feature audit for %s.", feature_id)
        raise


def build_seraphine_dawnshield_level17_profile() -> CharacterBuildProfile:
    try:
        base = build_seraphine_dawnshield_level16_profile()
        data = advance_profile_data(base, 17)
        apply_cleric_level_to_profile_data(data, 17)
        additions = [
            _feature(
                "cleric-combat-spells-9",
                "Level 9 Cleric Spells",
                True,
                "Bind simple legal level-9 combat casting to existing spell primitives before certification.",
            ),
            _feature(
                "supreme-healing",
                "Supreme Healing",
                True,
                "Reuse the universal outgoing-healing-dice maximizer already certified for 2014 Life Cleric.",
            ),
        ]
        data.update(
            feature_audits=[*data["feature_audits"], *(item.model_dump() for item in additions)],
            source_references=[
                *data["source_references"],
                "D&D Beyond Basic Rules 2024: Cleric level 17 — Life Domain feature; level 9 spells",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception:
        logger.exception("Failed to build Seraphine Dawnshield level 17 profile.")
        raise


def build_seraphine_dawnshield_level18_profile() -> CharacterBuildProfile:
    try:
        base = build_seraphine_dawnshield_level17_profile()
        data = advance_profile_data(base, 18)
        apply_cleric_level_to_profile_data(data, 18)
        data.update(
            source_references=[
                *data["source_references"],
                "D&D Beyond Basic Rules 2024: Cleric level 18 — Channel Divinity 4; Divine Spark 4d8",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception:
        logger.exception("Failed to build Seraphine Dawnshield level 18 profile.")
        raise


def build_seraphine_dawnshield_level19_profile() -> CharacterBuildProfile:
    try:
        base = build_seraphine_dawnshield_level18_profile()
        data = advance_profile_data(base, 19)
        apply_cleric_level_to_profile_data(data, 19)
        addition = _feature(
            "boon-of-fate",
            "Boon of Fate",
            False,
            "Audit and bind the 2024 Epic Boon without inventing a Cleric-specific resolver.",
        )
        data.update(
            feature_audits=[*data["feature_audits"], addition.model_dump()],
            source_references=[
                *data["source_references"],
                "D&D Beyond Basic Rules 2024: Cleric level 19 — Epic Boon; +1 Charisma",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception:
        logger.exception("Failed to build Seraphine Dawnshield level 19 profile.")
        raise


def build_seraphine_dawnshield_level20_profile() -> CharacterBuildProfile:
    try:
        base = build_seraphine_dawnshield_level19_profile()
        data = advance_profile_data(base, 20)
        apply_cleric_level_to_profile_data(data, 20)
        addition = _feature(
            "greater-divine-intervention",
            "Greater Divine Intervention",
            False,
            "Audit the 2024 capstone against the existing Divine Intervention resource/cast path.",
        )
        data.update(
            feature_audits=[*data["feature_audits"], addition.model_dump()],
            source_references=[
                *data["source_references"],
                "D&D Beyond Basic Rules 2024: Cleric level 20 — Greater Divine Intervention",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception:
        logger.exception("Failed to build Seraphine Dawnshield level 20 profile.")
        raise
