from __future__ import annotations

import logging

from app.content.barbarian_level18_profile import build_rokhan_stonefury_level18_profile
from app.content.barbarian_profile_from_levels import apply_barbarian_level_to_profile_data
from app.content.canonical_progression import advance_profile_data
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit

logger = logging.getLogger(__name__)


def build_rokhan_stonefury_level19_profile() -> CharacterBuildProfile:
    try:
        previous = build_rokhan_stonefury_level18_profile()
        data = advance_profile_data(previous, 19)
        apply_barbarian_level_to_profile_data(data, 19)
        feature = FeatureAudit(
            feature_id="boon-irresistible-offense-l19",
            feature_name="Boon of Irresistible Offense",
            source_reference="D&D Beyond Basic Rules 2024: Barbarian Level 19; Boon of Irresistible Offense",
            category="feat",
            combat_relevant=True,
            automated=True,
            notes=(
                "Strength increases 20→21. Bludgeoning, Piercing, and Slashing damage ignores Resistance "
                "through a universal typed bypass grant. A natural 20 attack roll adds damage equal to the "
                "increased Strength score, using the attack's damage type, through a universal attack rider."
            ),
        )
        maximums = dict(data.get("ability_score_maximums", {}))
        maximums["strength"] = 30
        data.update(
            ability_score_maximums=maximums,
            feature_audits=[*data["feature_audits"], feature.model_dump()],
            source_references=[
                *data["source_references"],
                "D&D Beyond Basic Rules 2024: Barbarian Level 19; Boon of Irresistible Offense",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception:
        logger.exception("Failed to build Rokhan Stonefury 2024 level 19 profile.")
        raise
