from __future__ import annotations

from app.content.barbarian_berserker_high_profile import build_rokhan_stonefury_level9_profile
from app.content.barbarian_profile_from_levels import apply_barbarian_level_to_profile_data
from app.content.canonical_progression import advance_profile_data
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit


def build_rokhan_stonefury_level10_profile() -> CharacterBuildProfile:
    previous = build_rokhan_stonefury_level9_profile()
    data = advance_profile_data(previous, 10)
    apply_barbarian_level_to_profile_data(data, 10)
    feature = FeatureAudit(
        feature_id="retaliation", feature_name="Retaliation",
        source_reference="D&D Beyond Basic Rules 2024: Path of the Berserker Level 10",
        category="subclass", combat_relevant=True, automated=True,
        notes=("Reuses the universal damage-triggered reaction attack engine already certified by the 2014 Berserker."),
    )
    data.update(
        feature_audits=[*data["feature_audits"], feature.model_dump()],
        source_references=[*data["source_references"], "D&D Beyond Basic Rules 2024: Path of the Berserker Level 10 Retaliation"],
    )
    return CharacterBuildProfile.model_validate(data)


def build_rokhan_stonefury_level11_profile() -> CharacterBuildProfile:
    previous = build_rokhan_stonefury_level10_profile()
    data = advance_profile_data(previous, 11)
    apply_barbarian_level_to_profile_data(data, 11)
    feature = FeatureAudit(
        feature_id="relentless-rage", feature_name="Relentless Rage",
        source_reference="D&D Beyond Basic Rules 2024: Barbarian Level 11",
        category="class", combat_relevant=True, automated=True,
        notes=("Reuses the universal effect-bound survival-save primitive with Rage requirement, escalating Constitution DC, and replacement HP."),
    )
    data.update(
        feature_audits=[*data["feature_audits"], feature.model_dump()],
        source_references=[*data["source_references"], "D&D Beyond Basic Rules 2024: Barbarian Level 11 Relentless Rage"],
    )
    return CharacterBuildProfile.model_validate(data)
