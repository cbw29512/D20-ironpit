from __future__ import annotations

import logging

from app.content.canonical_progression import advance_profile_data
from app.content.fighter_asi_progression_profile import build_karnok_stoneward_level12_profile
from app.content.fighter_profile_from_levels import apply_fighter_level_to_profile_data
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit

logger = logging.getLogger(__name__)


def build_karnok_stoneward_level13_profile() -> CharacterBuildProfile:
    try:
        previous = build_karnok_stoneward_level12_profile()
        data = advance_profile_data(previous, 13)
        apply_fighter_level_to_profile_data(data, 13)
        studied_attacks = FeatureAudit(
            feature_id="studied-attacks",
            feature_name="Studied Attacks",
            source_reference="D&D Beyond Basic Rules 2024: Fighter Level 13 — Studied Attacks",
            category="class",
            combat_relevant=True,
            automated=True,
            notes=(
                "After Karnok misses an attack roll against a creature, his next attack roll "
                "against that creature has Advantage until the end of his next turn. The shared "
                "Studied Attacks runtime owns the temporary target-bound state."
            ),
        )
        data.update(
            feature_audits=[*data["feature_audits"], studied_attacks.model_dump()],
            source_references=[
                *data["source_references"],
                "D&D Beyond Basic Rules 2024: Fighter Level 13 — Indomitable and Studied Attacks",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception as exc:
        logger.exception("Failed to build Karnok Stoneward level 13 profile.")
        raise RuntimeError("Karnok Stoneward level 13 profile could not be built.") from exc


def build_karnok_stoneward_level14_profile() -> CharacterBuildProfile:
    try:
        previous = build_karnok_stoneward_level13_profile()
        data = advance_profile_data(previous, 14)
        apply_fighter_level_to_profile_data(data, 14)
        ability_score_improvement = FeatureAudit(
            feature_id="ability-score-improvement-l14",
            feature_name="Ability Score Improvement",
            source_reference=(
                "D&D Beyond Basic Rules 2024: Fighter Level 14; "
                "Feats — Ability Score Improvement"
            ),
            category="feat",
            combat_relevant=True,
            automated=True,
            notes=(
                "Deterministic ranged-defense progression choice: +2 Dexterity, DEX 13→15. "
                "The authoritative Fighter table updates initiative, Dexterity-based attacks, "
                "Dexterity checks, and Dexterity saving throws from the new score."
            ),
        )
        data.update(
            feature_audits=[*data["feature_audits"], ability_score_improvement.model_dump()],
            source_references=[
                *data["source_references"],
                "D&D Beyond Basic Rules 2024: Fighter Level 14 — Ability Score Improvement",
                "D&D Beyond Basic Rules 2024: Feats — Ability Score Improvement (+2 Dexterity)",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception as exc:
        logger.exception("Failed to build Karnok Stoneward level 14 profile.")
        raise RuntimeError("Karnok Stoneward level 14 profile could not be built.") from exc


def build_karnok_stoneward_level15_profile() -> CharacterBuildProfile:
    """Advance the canonical 2024 Champion from level 14 to level 15 only."""
    try:
        previous = build_karnok_stoneward_level14_profile()
        data = advance_profile_data(previous, 15)
        apply_fighter_level_to_profile_data(data, 15)
        superior_critical = FeatureAudit(
            feature_id="superior-critical",
            feature_name="Superior Critical",
            source_reference="D&D Beyond Basic Rules 2024: Champion Level 15 — Superior Critical",
            category="subclass",
            combat_relevant=True,
            automated=True,
            notes=(
                "Weapon attacks score a Critical Hit on a natural 18–20. "
                "Iron Pit reuses the universal critical_hit_minimum capability."
            ),
        )
        data.update(
            feature_audits=[*data["feature_audits"], superior_critical.model_dump()],
            source_references=[
                *data["source_references"],
                "D&D Beyond Basic Rules 2024: Champion Level 15 — Superior Critical",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception as exc:
        logger.exception("Failed to build Karnok Stoneward level 15 profile.")
        raise RuntimeError("Karnok Stoneward level 15 profile could not be built.") from exc


def build_karnok_stoneward_level16_profile() -> CharacterBuildProfile:
    """Advance Karnok to Fighter 16 using the audited canonical Dexterity ASI."""
    try:
        previous = build_karnok_stoneward_level15_profile()
        data = advance_profile_data(previous, 16)
        apply_fighter_level_to_profile_data(data, 16)
        ability_score_improvement = FeatureAudit(
            feature_id="ability-score-improvement-l16",
            feature_name="Ability Score Improvement",
            source_reference=(
                "D&D Beyond Basic Rules 2024: Fighter Level 16; "
                "Feats — Ability Score Improvement"
            ),
            category="feat",
            combat_relevant=True,
            automated=True,
            notes=(
                "Deterministic ranged-defense progression choice: +2 Dexterity, DEX 15→17. "
                "The authoritative Fighter table updates initiative, Dexterity-based attacks, "
                "Dexterity checks, and Dexterity saving throws from the new score."
            ),
        )
        data.update(
            feature_audits=[*data["feature_audits"], ability_score_improvement.model_dump()],
            source_references=[
                *data["source_references"],
                "D&D Beyond Basic Rules 2024: Fighter Level 16 — Ability Score Improvement",
                "D&D Beyond Basic Rules 2024: Feats — Ability Score Improvement (+2 Dexterity)",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception as exc:
        logger.exception("Failed to build Karnok Stoneward level 16 profile.")
        raise RuntimeError("Karnok Stoneward level 16 profile could not be built.") from exc


def build_karnok_stoneward_level17_profile() -> CharacterBuildProfile:
    """Advance Karnok to Fighter 17 through the shared Fighter resource progression."""
    try:
        previous = build_karnok_stoneward_level16_profile()
        data = advance_profile_data(previous, 17)
        apply_fighter_level_to_profile_data(data, 17)
        data.update(
            source_references=[
                *data["source_references"],
                "D&D Beyond Basic Rules 2024: Fighter Level 17 — Action Surge and Indomitable",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception as exc:
        logger.exception("Failed to build Karnok Stoneward level 17 profile.")
        raise RuntimeError("Karnok Stoneward level 17 profile could not be built.") from exc
