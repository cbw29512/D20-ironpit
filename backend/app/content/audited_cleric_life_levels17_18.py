from __future__ import annotations

import logging

from app.content.audited_cleric_life_levels15_16 import build_seraphine_dawnshield_level16_profile
from app.content.audited_cleric_life_profile_support import life_class_feature as _class_feature
from app.content.canonical_progression import advance_profile_data
from app.content.cleric_profile_from_levels import apply_cleric_level_to_profile_data
from app.domain.character_builds import CharacterBuildProfile

logger = logging.getLogger(__name__)


def build_seraphine_dawnshield_level17_profile() -> CharacterBuildProfile:
    try:
        base = build_seraphine_dawnshield_level16_profile()
        data = advance_profile_data(base, 17)
        apply_cleric_level_to_profile_data(data, 17)
        additions = [
            _class_feature(
                "cleric-combat-spells-9",
                "Level 9 Cleric Spells",
                notes=(
                    "Iron Pit keeps the ninth-level arena package simple: Inflict Wounds at level 9 "
                    "for damage and Mass Cure Wounds at level 9 for healing."
                ),
            ),
            _class_feature(
                "inflict-wounds-upcast-l9",
                "Inflict Wounds — 9th-Level Slot",
                notes="Existing save-damage pipeline: 10d10 Necrotic damage, Constitution save for half.",
            ),
            _class_feature(
                "mass-cure-wounds-upcast-l9",
                "Mass Cure Wounds — 9th-Level Slot",
                notes="Shared group-healing pipeline: 9d8 + Wisdom + Disciple of Life using one level-9 slot.",
            ),
            _class_feature(
                "supreme-healing",
                "Supreme Healing",
                notes=(
                    "Generic source-scoped healing maximization applies to Seraphine's spell-healing "
                    "actions and Divine Spark without changing unrelated healing."
                ),
            ),
            _class_feature(
                "astral-projection",
                "Astral Projection",
                combat=False,
                notes="Legal ninth-level prepared spell; planar travel is outside the Iron Pit arena.",
            ),
        ]
        data.update(
            feature_audits=[
                *data["feature_audits"],
                *(feature.model_dump() for feature in additions),
            ],
            source_references=[
                *data["source_references"],
                "D&D Beyond Basic Rules 2024: Cleric level 17 — level 9 spell slot and 19 prepared spells",
                "D&D Beyond Basic Rules 2024: Life Domain level 17 — Supreme Healing",
                "D&D Beyond Basic Rules 2024: Cleric Spell List — Astral Projection",
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
        addition = _class_feature(
            "word-of-recall",
            "Word of Recall",
            combat=False,
            notes="Additional legal prepared spell; arena escape/travel is intentionally out of scope.",
        )
        data.update(
            feature_audits=[*data["feature_audits"], addition.model_dump()],
            source_references=[
                *data["source_references"],
                "D&D Beyond Basic Rules 2024: Cleric level 18 — Channel Divinity 4 uses, 20 prepared spells",
                "D&D Beyond Basic Rules 2024: Cleric level 18 — Divine Spark 4d8",
                "D&D Beyond Basic Rules 2024: Cleric Spell List — Word of Recall",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception:
        logger.exception("Failed to build Seraphine Dawnshield level 18 profile.")
        raise
