from __future__ import annotations

import logging

from app.content.audited_cleric_life_levels11_12 import build_seraphine_dawnshield_level12_profile
from app.content.audited_cleric_life_profile_support import life_class_feature as _class_feature
from app.content.canonical_progression import advance_profile_data
from app.content.cleric_profile_from_levels import apply_cleric_level_to_profile_data
from app.domain.character_builds import CharacterBuildProfile

logger = logging.getLogger(__name__)


def build_seraphine_dawnshield_level13_profile() -> CharacterBuildProfile:
    try:
        base = build_seraphine_dawnshield_level12_profile()
        data = advance_profile_data(base, 13)
        apply_cleric_level_to_profile_data(data, 13)
        additions = [
            _class_feature(
                "cleric-combat-spells-7",
                "Level 7 Cleric Spells",
                notes=(
                    "The universal spell-slot scaler can cast Inflict Wounds using the level-7 slot. "
                    "Mass Cure Wounds exposes a level-7 healing action through its existing generic upcast factory."
                ),
            ),
            _class_feature(
                "fire-storm",
                "Fire Storm",
                combat=False,
                notes=(
                    "Legal level-7 prepared damage spell retained in the canonical package; "
                    "the arena prefers already-supported simpler damage actions."
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
                "D&D Beyond Basic Rules 2024: Cleric level 13 — level 7 spell slot and 17 prepared spells",
                "D&D Beyond Basic Rules 2024: Cleric Spell List — Fire Storm",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception:
        logger.exception("Failed to build Seraphine Dawnshield 2024 level 13 profile.")
        raise


def build_seraphine_dawnshield_level14_profile() -> CharacterBuildProfile:
    try:
        base = build_seraphine_dawnshield_level13_profile()
        data = advance_profile_data(base, 14)
        apply_cleric_level_to_profile_data(data, 14)
        addition = _class_feature(
            "improved-blessed-strikes",
            "Improved Blessed Strikes — Potent Spellcasting",
            notes=(
                "After Sacred Flame deals damage, the universal post-damage rider grants "
                "10 Temporary HP (2 × Wisdom modifier 5) to Seraphine or one ally within 60 feet."
            ),
        )
        data.update(
            feature_audits=[*data["feature_audits"], addition.model_dump()],
            source_references=[
                *data["source_references"],
                "D&D Beyond Basic Rules 2024: Cleric level 14 — Improved Blessed Strikes",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception:
        logger.exception("Failed to build Seraphine Dawnshield 2024 level 14 profile.")
        raise
