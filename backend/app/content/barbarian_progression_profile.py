from __future__ import annotations

from app.content.audited_barbarian_profile import build_rokhan_stonefury_profile
from app.content.canonical_progression import advance_profile_data
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit


def _level_two_features() -> list[FeatureAudit]:
    source = "D&D Beyond Basic Rules 2024: Barbarian Level 2"
    return [
        FeatureAudit(
            feature_id="danger-sense",
            feature_name="Danger Sense",
            source_reference=source,
            category="class",
            combat_relevant=True,
            automated=True,
            notes="Advantage applies to Dexterity saving throws unless Rokhan is Incapacitated.",
        ),
        FeatureAudit(
            feature_id="reckless-attack",
            feature_name="Reckless Attack",
            source_reference=source,
            category="class",
            combat_relevant=True,
            automated=True,
            notes=("On Rokhan's first Strength attack roll each turn, Iron Pit chooses Reckless Attack; his Strength "
                   "attack rolls gain Advantage and attacks against him gain Advantage until his next turn starts."),
        ),
    ]


def build_rokhan_stonefury_level2_profile() -> CharacterBuildProfile:
    previous = build_rokhan_stonefury_profile()
    data = advance_profile_data(previous, 2)
    data.update(
        feature_audits=[*data["feature_audits"], *(item.model_dump() for item in _level_two_features())],
        source_references=[
            *data["source_references"],
            "Basic Rules 2024: Barbarian — Level 2 Danger Sense and Reckless Attack",
        ],
    )
    return CharacterBuildProfile.model_validate(data)
