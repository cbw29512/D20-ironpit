from __future__ import annotations

import logging

from app.content.barbarian_level19_profile import build_rokhan_stonefury_level19_profile
from app.content.barbarian_profile_from_levels import apply_barbarian_level_to_profile_data
from app.content.canonical_progression import advance_profile_data
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit

logger = logging.getLogger(__name__)


def build_rokhan_stonefury_level20_profile() -> CharacterBuildProfile:
    try:
        previous = build_rokhan_stonefury_level19_profile()
        data = advance_profile_data(previous, 20)
        apply_barbarian_level_to_profile_data(data, 20)
        feature = FeatureAudit(
            feature_id="primal-champion-l20",
            feature_name="Primal Champion",
            source_reference="D&D Beyond Basic Rules 2024: Barbarian Level 20 Primal Champion",
            category="class",
            combat_relevant=True,
            automated=True,
            notes=(
                "Primal Champion is represented through the normal ability-score progression: "
                "Strength increases 21→25 and Constitution 20→24, with both score maximums raised to 25. "
                "Derived AC, HP, attacks, saves, checks, and existing universal features consume those scores."
            ),
        )
        data.update(
            ability_score_maximums={
                **data.get("ability_score_maximums", {}),
                "strength": 25,
                "constitution": 25,
            },
            feature_audits=[*data["feature_audits"], feature.model_dump()],
            source_references=[
                *data["source_references"],
                "D&D Beyond Basic Rules 2024: Barbarian Level 20 Primal Champion",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception:
        logger.exception("Failed to build Rokhan Stonefury 2024 level 20 profile.")
        raise
