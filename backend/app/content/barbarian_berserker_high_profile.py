from __future__ import annotations

from app.content.barbarian_berserker_progression_profile import build_rokhan_stonefury_level7_profile
from app.content.barbarian_profile_from_levels import apply_barbarian_level_to_profile_data
from app.content.canonical_progression import advance_profile_data
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit


def build_rokhan_stonefury_level8_profile() -> CharacterBuildProfile:
    """Advance the certified 2024 Berserker from level 7 to level 8 with the RAW Strength ASI."""
    try:
        previous = build_rokhan_stonefury_level7_profile()
        data = advance_profile_data(previous, 8)
        apply_barbarian_level_to_profile_data(data, 8)
        asi = FeatureAudit(
            feature_id="ability-score-improvement-l8",
            feature_name="Ability Score Improvement",
            source_reference="D&D Beyond Basic Rules 2024: Barbarian Level 8; Feats — Ability Score Improvement",
            category="feat",
            combat_relevant=True,
            automated=True,
            notes=(
                "Canonical damage-first progression raises Strength from 18 to 20. "
                "Existing shared stat math updates attacks, damage, Strength saves, and Athletics; "
                "no new combat primitive is introduced."
            ),
        )
        data.update(
            feature_audits=[*data["feature_audits"], asi.model_dump()],
            source_references=[
                *data["source_references"],
                "D&D Beyond Basic Rules 2024: Barbarian Level 8 Ability Score Improvement (+2 Strength)",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception as exc:
        raise RuntimeError("Rokhan Stonefury level 8 profile could not be built.") from exc


def build_rokhan_stonefury_level9_profile() -> CharacterBuildProfile:
    """Advance the certified 2024 Berserker from level 8 to level 9 using the shared Brutal Strike engine."""
    try:
        previous = build_rokhan_stonefury_level8_profile()
        data = advance_profile_data(previous, 9)
        apply_barbarian_level_to_profile_data(data, 9)
        brutal = FeatureAudit(
            feature_id="brutal-strike",
            feature_name="Brutal Strike",
            source_reference="D&D Beyond Basic Rules 2024: Barbarian Level 9",
            category="class",
            combat_relevant=True,
            automated=True,
            notes=(
                "Reuses the universal Brutal Strike mechanic: when Rokhan makes an eligible Reckless "
                "Strength attack without Disadvantage, Iron Pit can suppress that Reckless Advantage "
                "for the attack and add 1d10 extra damage on a hit. Hamstring Blow remains arena-neutral "
                "under the current documented Iron Pit policy."
            ),
        )
        data.update(
            feature_audits=[*data["feature_audits"], brutal.model_dump()],
            source_references=[
                *data["source_references"],
                "D&D Beyond Basic Rules 2024: Barbarian Level 9 Brutal Strike",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception as exc:
        raise RuntimeError("Rokhan Stonefury level 9 profile could not be built.") from exc
