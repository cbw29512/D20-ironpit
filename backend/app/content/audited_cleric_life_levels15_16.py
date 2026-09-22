from __future__ import annotations

import logging

from app.content.audited_cleric_life_levels13_14 import build_seraphine_dawnshield_level14_profile
from app.content.audited_cleric_life_profile_support import life_class_feature as _class_feature
from app.content.canonical_progression import advance_profile_data
from app.content.cleric_profile_from_levels import apply_cleric_level_to_profile_data
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit

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
                    "Iron Pit uses simple RAW upcasts at this tier: Inflict Wounds at level 8 "
                    "for damage and Mass Cure Wounds at level 8 for healing."
                ),
            ),
            _class_feature(
                "inflict-wounds-upcast-l8",
                "Inflict Wounds — 8th-Level Slot",
                notes="Existing save-damage pipeline: 9d10 Necrotic damage, Constitution save for half.",
            ),
            _class_feature(
                "mass-cure-wounds-upcast-l8",
                "Mass Cure Wounds — 8th-Level Slot",
                notes=(
                    "Shared group-healing pipeline: 8d8 + Wisdom + Disciple of Life "
                    "using one level-8 slot."
                ),
            ),
            _class_feature(
                "sunburst",
                "Sunburst",
                combat=False,
                notes="Legal level-8 prepared damage spell; arena uses the simpler Inflict Wounds upcast.",
            ),
        ]
        data.update(
            feature_audits=[
                *data["feature_audits"],
                *(feature.model_dump() for feature in additions),
            ],
            source_references=[
                *data["source_references"],
                "D&D Beyond Basic Rules 2024: Cleric level 15 — level 8 spell slot and 18 prepared spells",
                "D&D Beyond Basic Rules 2024: Cleric Spell List — Sunburst",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception:
        logger.exception("Failed to build Seraphine Dawnshield level 15 profile.")
        raise


def build_seraphine_dawnshield_level16_profile() -> CharacterBuildProfile:
    try:
        base = build_seraphine_dawnshield_level15_profile()
        data = advance_profile_data(base, 16)
        apply_cleric_level_to_profile_data(data, 16)
        addition = FeatureAudit(
            feature_id="ability-score-improvement-l16",
            feature_name="Ability Score Improvement",
            source_reference=(
                "D&D Beyond Basic Rules 2024: Cleric Level 16; "
                "Feats — Ability Score Improvement"
            ),
            category="feat",
            combat_relevant=True,
            automated=True,
            notes=(
                "+2 Charisma: CHA 17→19; Charisma saving throws and Persuasion "
                "increase by 1 while Wisdom remains 20."
            ),
        )
        data.update(
            feature_audits=[*data["feature_audits"], addition.model_dump()],
            source_references=[
                *data["source_references"],
                "D&D Beyond Basic Rules 2024: Cleric level 16 — Ability Score Improvement",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception:
        logger.exception("Failed to build Seraphine Dawnshield level 16 profile.")
        raise
