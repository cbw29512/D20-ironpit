from __future__ import annotations

import logging

from app.content.audited_cleric_life_levels11_12 import build_seraphine_dawnshield_level12_profile
from app.content.audited_cleric_life_profile_support import life_class_feature as _class_feature
from app.content.canonical_progression import advance_profile_data
from app.content.cleric_profile_from_levels import apply_cleric_level_to_profile_data
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit

logger = logging.getLogger(__name__)


def _pending(
    feature_id: str,
    name: str,
    notes: str,
    *,
    automated: bool = False,
) -> FeatureAudit:
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
        logger.exception("Failed to build pending Cleric feature audit for %s.", feature_id)
        raise


def build_seraphine_dawnshield_level13_profile() -> CharacterBuildProfile:
    try:
        base = build_seraphine_dawnshield_level12_profile()
        data = advance_profile_data(base, 13)
        apply_cleric_level_to_profile_data(data, 13)
        additions = [
            _pending(
                "cleric-combat-spells-7",
                "Level 7 Cleric Spells",
                "Reuses existing Inflict Wounds and Mass Cure Wounds upcast primitives with a level-7 slot.",
                automated=True,
            ),
        ]
        data.update(
            feature_audits=[*data["feature_audits"], *(item.model_dump() for item in additions)],
            source_references=[
                *data["source_references"],
                "D&D Beyond Basic Rules 2024: Cleric level 13 — level 7 spells; Divine Spark 3d8",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception:
        logger.exception("Failed to build Seraphine Dawnshield level 13 profile.")
        raise


def build_seraphine_dawnshield_level14_profile() -> CharacterBuildProfile:
    try:
        base = build_seraphine_dawnshield_level13_profile()
        data = advance_profile_data(base, 14)
        apply_cleric_level_to_profile_data(data, 14)
        addition = _pending(
            "improved-blessed-strikes",
            "Improved Blessed Strikes",
            "Potent Spellcasting upgrade: Sacred Flame damage grants Seraphine 10 Temporary HP via the universal source-damage trigger.",
            automated=True,
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
        logger.exception("Failed to build Seraphine Dawnshield level 14 profile.")
        raise


def build_seraphine_dawnshield_level15_profile() -> CharacterBuildProfile:
    try:
        base = build_seraphine_dawnshield_level14_profile()
        data = advance_profile_data(base, 15)
        apply_cleric_level_to_profile_data(data, 15)
        additions = [
            _pending(
                "cleric-combat-spells-8",
                "Level 8 Cleric Spells",
                "Reuses existing Inflict Wounds, Heal, and Mass Cure Wounds upcast primitives with a level-8 slot.",
                automated=True,
            ),
            _class_feature(
                "holy-aura",
                "Holy Aura",
                notes=(
                    "Concentration 1-minute 30-foot emanation: allies have Advantage on all "
                    "saves and attackers have Disadvantage against them. Not auto-cast over damage."
                ),
            ),
            _class_feature(
                "regenerate",
                "Regenerate",
                combat=False,
                notes=(
                    "Printed 1-minute casting time keeps it off fight Actions. It stays on "
                    "the prepared list as a long-cast spell."
                ),
            ),
        ]
        data.update(
            feature_audits=[*data["feature_audits"], *(item.model_dump() for item in additions)],
            source_references=[
                *data["source_references"],
                "D&D Beyond Basic Rules 2024: Cleric level 15 — level 8 spells; Holy Aura",
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
        addition = _class_feature(
            "ability-score-improvement-l16",
            "Ability Score Improvement",
            notes="+2 Charisma: CHA 17→19; Wisdom remains 20.",
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
