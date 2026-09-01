from __future__ import annotations

from app.content.canonical_progression import advance_profile_data
from app.content.fighter_asi_progression_profile import build_karnok_stoneward_level8_profile
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit


def build_karnok_stoneward_level9_profile() -> CharacterBuildProfile:
    previous = build_karnok_stoneward_level8_profile()
    data = advance_profile_data(previous, 9)
    source = "D&D Beyond Basic Rules 2024: Fighter Level 9"
    features = [
        FeatureAudit(
            feature_id="indomitable",
            feature_name="Indomitable",
            source_reference=source,
            category="class",
            combat_relevant=True,
            automated=True,
            notes=("After a failed combat saving throw, reroll with +9 and use the new roll. Iron Pit spends the "
                   "single use only when the reroll can mathematically succeed."),
        ),
        FeatureAudit(
            feature_id="tactical-master-sap",
            feature_name="Tactical Master — Sap",
            source_reference=source,
            category="class",
            combat_relevant=True,
            automated=True,
            notes=("Long-Rest mastery choices are optimized to Greatsword, Shortbow, Javelin, and Spear. On a "
                   "mastered Greatsword or Shortbow attack, Tactical Master replaces the normal mastery with Sap. "
                   "Slow is arena-out-of-scope; Push is not selected because extra separation does not improve "
                   "Karnok's melee-closing combat outcome."),
        ),
    ]
    data.update(
        weapon_masteries=["greatsword", "shortbow", "javelin", "spear"],
        feature_audits=[*data["feature_audits"], *(item.model_dump() for item in features)],
        source_references=[
            *data["source_references"],
            "Basic Rules 2024: Fighter — Level 9 Indomitable",
            "Basic Rules 2024: Fighter — Level 9 Tactical Master",
            "Basic Rules 2024: Weapon Mastery — Sap",
        ],
    )
    return CharacterBuildProfile.model_validate(data)
