from __future__ import annotations

import logging

from app.content.audited_cleric_life_levels13_14 import build_seraphine_dawnshield_level14_profile
from app.content.audited_cleric_life_profile_support import life_class_feature as _class_feature
from app.content.canonical_progression import advance_profile_data
from app.content.cleric_profile_from_levels import apply_cleric_level_to_profile_data
from app.domain.character_builds import CharacterBuildProfile

logger = logging.getLogger(__name__)


def build_seraphine_dawnshield_level15_profile() -> CharacterBuildProfile:
    try:
        base = build_seraphine_dawnshield_level14_profile()
        data = advance_profile_data(base, 15)
        apply_cleric_level_to_profile_data(data, 15)
        additions = [
            _class_feature(
                "cleric-combat-spells-8",
                "Level 8 Cleric Spells",
                notes=(
                    "The level-8 slot is supplied by the canonical Cleric resource progression. "
                    "Sunburst composes existing area-save damage, Blinded, timed-condition, and "
                    "repeat-save primitives; no Cleric-specific resolver is required."
                ),
            ),
            _class_feature(
                "sunburst",
                "Sunburst",
                notes=(
                    "150-foot range, 60-foot-radius sphere, Constitution save, 12d6 radiant damage "
                    "with half damage on success; a failed save applies Blinded for up to 1 minute "
                    "with a Constitution repeat save at the end of each affected creature's turn. "
                    "Its spell-created Darkness cleanup clause is arena-inert because the current "
                    "Iron Pit state model has no spell-created Darkness state."
                ),
            ),
        ]
        data.update(
            feature_audits=[
                *data["feature_audits"],
                *(feature.model_dump() for feature in additions),
            ],
            source_references=[
                *data["source_references"],
                "D&D Beyond Basic Rules 2024: Cleric level 15 — level 8 spell slot",
                "SRD 5.2.1: Sunburst",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception:
        logger.exception("Failed to build Seraphine Dawnshield 2024 level 15 profile.")
        raise
