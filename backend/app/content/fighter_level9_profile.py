from __future__ import annotations

from app.content.canonical_progression import advance_profile_data
from app.content.fighter_asi_progression_profile import build_karnok_stoneward_level8_profile
from app.content.fighter_profile_from_levels import apply_fighter_level_to_profile_data
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit


def build_karnok_stoneward_level9_profile() -> CharacterBuildProfile:
    previous = build_karnok_stoneward_level8_profile()
    data = advance_profile_data(previous, 9)
    apply_fighter_level_to_profile_data(data, 9)
    source = "D&D Beyond Basic Rules 2024: Fighter Level 9"
    features = [
        FeatureAudit(
            feature_id="indomitable",
            feature_name="Indomitable",
            source_reference=source,
            category="class",
            combat_relevant=True,
            automated=True,
            notes=("After a rolled saving throw fails, the arena automatically spends one available Indomitable use, "
                   "rerolls the save, and adds the Fighter level to the reroll."),
        ),
        FeatureAudit(
            feature_id="tactical-master",
            feature_name="Tactical Master",
            source_reference=source,
            category="class",
            combat_relevant=True,
            automated=True,
            notes=("One legal Long-Rest Weapon Mastery swap changes Longsword to Greatsword, preserving Flail, "
                   "Javelin, and Spear. For Greatsword attacks the arena selects Sap as Tactical Master's replacement, "
                   "so Graze is suppressed for that attack rather than stacked with Sap. The backup Shortbow remains unmastered."),
        ),
    ]
    data.update(
        feature_audits=[*data["feature_audits"], *(item.model_dump() for item in features)],
        source_references=[
            *data["source_references"],
            "Basic Rules 2024: Fighter — Level 9 Indomitable",
            "Basic Rules 2024: Fighter — Level 9 Tactical Master",
            "Basic Rules 2024: Weapon Mastery — Sap",
        ],
    )
    return CharacterBuildProfile.model_validate(data)
