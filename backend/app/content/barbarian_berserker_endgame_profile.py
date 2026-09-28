from __future__ import annotations

from app.content.barbarian_berserker_high_profile import build_rokhan_stonefury_level11_profile
from app.content.barbarian_profile_from_levels import apply_barbarian_level_to_profile_data
from app.content.canonical_progression import advance_profile_data
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit


def build_rokhan_stonefury_level12_profile() -> CharacterBuildProfile:
    """Advance the certified 2024 Berserker from level 11 to level 12 with the RAW Constitution ASI."""
    try:
        previous = build_rokhan_stonefury_level11_profile()
        data = advance_profile_data(previous, 12)
        apply_barbarian_level_to_profile_data(data, 12)
        asi = FeatureAudit(
            feature_id="ability-score-improvement-l12",
            feature_name="Ability Score Improvement",
            source_reference="D&D Beyond Basic Rules 2024: Barbarian Level 12; Feats — Ability Score Improvement",
            category="feat",
            combat_relevant=True,
            automated=True,
            notes=(
                "Canonical progression raises Constitution from 16 to 18. Existing shared stat math updates "
                "Armor Class, hit points, Constitution saves, and all dependent runtime values; no new combat "
                "primitive is introduced."
            ),
        )
        data.update(
            feature_audits=[*data["feature_audits"], asi.model_dump()],
            source_references=[
                *data["source_references"],
                "D&D Beyond Basic Rules 2024: Barbarian Level 12 Ability Score Improvement (+2 Constitution)",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception as exc:
        raise RuntimeError("Rokhan Stonefury level 12 profile could not be built.") from exc


def build_rokhan_stonefury_level13_profile() -> CharacterBuildProfile:
    """Advance the certified 2024 Berserker to Improved Brutal Strike at level 13."""
    try:
        previous = build_rokhan_stonefury_level12_profile()
        data = advance_profile_data(previous, 13)
        apply_barbarian_level_to_profile_data(data, 13)
        improved = FeatureAudit(
            feature_id="improved-brutal-strike",
            feature_name="Improved Brutal Strike",
            source_reference="D&D Beyond Basic Rules 2024: Barbarian Level 13",
            category="class",
            combat_relevant=True,
            automated=True,
            notes=(
                "Adds Staggering Blow and Sundering Blow to the source-declared Brutal Strike option set. "
                "Staggering reuses consumable saving-throw Disadvantage plus Opportunity-Attack suppression. "
                "Sundering reuses the generic defender-scoped +5 next-attack modifier for another creature. "
                "The shared engine selects only legal declared options and still allows one effect at level 13."
            ),
        )
        data.update(
            feature_audits=[*data["feature_audits"], improved.model_dump()],
            source_references=[
                *data["source_references"],
                "D&D Beyond Basic Rules 2024: Barbarian Level 13 Improved Brutal Strike",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception as exc:
        raise RuntimeError("Rokhan Stonefury level 13 profile could not be built.") from exc
